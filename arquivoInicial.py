import sqlite3
import dspy
import os
import subprocess
import sys
import time
import signal
import atexit
import requests
import telebot #pip install pytelegrambotapi
import whisper #pip install -U openai-whisper
### whisper requires ffmpeg: on windows: choco install ffmpeg
import json

LLAMA_SERVER_HOST = "127.0.0.1"
LLAMA_SERVER_PORT = 8080
LLAMA_API_BASE = f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}/v1"

HF_REPO_ID = "unsloth/Qwen3-0.6B-GGUF"
HF_FILENAME = "Qwen3-0.6B-Q8_0.gguf"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, HF_FILENAME)
db_path = os.path.join(BASE_DIR, "lojas.db")

_server_process = None

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"modelo já existe: {MODEL_PATH}")
        return MODEL_PATH

    print(f"baixando modelo {HF_REPO_ID}/{HF_FILENAME}...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    from huggingface_hub import hf_hub_download

    path = hf_hub_download(
        repo_id=HF_REPO_ID,
        filename=HF_FILENAME,
        local_dir=MODELS_DIR,
    )
    print(f"Modelo baixado: {path}")
    return path


def start_llama_server():
    global _server_process

    print(f"iniciando llama-cpp-python server na porta {LLAMA_SERVER_PORT}...")

    _server_process = subprocess.Popen(
        [
            sys.executable, "-m", "llama_cpp.server",
            "--model", MODEL_PATH,
            "--host", LLAMA_SERVER_HOST,
            "--port", str(LLAMA_SERVER_PORT),
            "--n_ctx", "2048",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    atexit.register(stop_llama_server)

    _wait_for_server()

    print(f"Servidor llama.cpp rodando em {LLAMA_API_BASE}")


def _wait_for_server(timeout=120, interval=2):
    start = time.time()
    health_url = f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}/v1/models"

    while time.time() - start < timeout:
        # Verifica se o processo crashou
        if _server_process.poll() is not None:
            stderr_output = _server_process.stderr.read().decode() if _server_process.stderr else ""
            raise RuntimeError(
                f"Servidor llama.cpp encerrou inesperadamente (código {_server_process.returncode}).\n"
                f"Stderr: {stderr_output}"
            )

        try:
            resp = requests.get(health_url, timeout=5)
            if resp.status_code == 200:
                return
        except requests.ConnectionError:
            pass

        print(f"Aguardando servidor ({int(time.time() - start)}s)")
        time.sleep(interval)

    raise TimeoutError(
        f"Servidor llama.cpp não respondeu em {timeout}s. "
        f"Verifique se llama-cpp-python está instalado: pip install 'llama-cpp-python[server]'"
    )

def stop_llama_server():
    global _server_process
    if _server_process and _server_process.poll() is None:
        print("encerrando servidor llama.cpp")
        _server_process.terminate()
        try:
            _server_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _server_process.kill()
        _server_process = None

download_model()

start_llama_server()

lm = dspy.LM('openai/Qwen3-0.6B', api_base=LLAMA_API_BASE, api_key='not-needed')
dspy.configure(lm=lm)

def create_db():
  conn = sqlite3.connect(db_path)
  c = conn.cursor()

  # Create tables
  c.execute("""CREATE TABLE IF NOT EXISTS produtos (
                nome TEXT, 
                departamento TEXT
            )""")

  c.executemany("INSERT INTO produtos VALUES (?, ?)", [
    ("sabonete", "higiene"),
    ("agua", "bebidas"),
    ("coca", "bebidas"),
  ])

  conn.commit()
  conn.close()

create_db()

conn = sqlite3.connect(db_path)
results = conn.execute("SELECT * from produtos").fetchall()
print(results)

class TextToSQL(dspy.Signature):
    """Generate SQL from natural language.

        Database schema:
          - produtos: nome, departamento
    """
    dbschema = dspy.InputField(desc="Databases schema")
    question = dspy.InputField(desc="Natural language question")

    sql_query = dspy.OutputField(desc="Valid SQL query")

class ReliableSQLGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        pred = self.generate_sql(schema=schema, question=question)
        return pred
    

question = "qual o departamento do sabonete?"

def generate(question):
    schema = """
    CREATE TABLE produtos (
      nome VARCHAR(50),
      departmento VARCHAR(50),
    );
    """
    generator = ReliableSQLGenerator()
    sql = generator.forward(schema, question)
    print(sql)
    conn = sqlite3.connect(db_path)
    print(sql.sql_query)
    results = conn.execute(sql.sql_query).fetchall()
    return results

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True)
def reply_hi(message):
  result = generate(message.text)
  bot.reply_to(message, json.dumps(result))

@bot.message_handler(content_types=['voice'])
def transcribe_voice_message(message):
    file_id = message.voice.file_id
    # Get url to audio file.
    file_path = bot.get_file_url(file_id)

    # Transcribe the audio using Whisper AI
    text = whisper_transcribe(file_path)

    result = generate(text)
    bot.reply_to(message, json.dumps(result))

def whisper_transcribe(filepath: str, model="tiny") -> str:
    """
    Function to perform ASR on a .mp3 file
    :param filepath: Path to the .mp3 audiofile.
    :param model: Set the model type for whisper
    ["tiny", "base", "small", "medium", "large"].
    Larger model means more parameters, higher memory requirements and
    slower speed.
    :return: transcribed audio.
    """
    # Choose tiny model for faster output.
    model = whisper.load_model(model)
    result = model.transcribe(filepath)

    return result["text"]

bot.polling()