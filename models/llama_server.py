import os
import subprocess
import sys
import time
import atexit
import requests

LLAMA_SERVER_HOST = "127.0.0.1"
LLAMA_SERVER_PORT = 8080
LLAMA_API_BASE = f"http://{LLAMA_SERVER_HOST}:{LLAMA_SERVER_PORT}/v1"

HF_REPO_ID = "unsloth/Qwen3-0.6B-GGUF"
HF_FILENAME = "Qwen3-0.6B-Q8_0.gguf"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, HF_FILENAME)

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
