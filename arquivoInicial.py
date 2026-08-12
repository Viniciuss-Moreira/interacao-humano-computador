import sqlite3
import os
import telebot #pip install pytelegrambotapi
import json
from ia import init_ia, generate_sql, whisper_transcribe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")

init_ia()

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

question = "qual o departamento do sabonete?"

def generate(question):
    sql_query = generate_sql(question)
    conn = sqlite3.connect(db_path)
    results = conn.execute(sql_query).fetchall()
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

bot.polling()