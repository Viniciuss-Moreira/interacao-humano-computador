import requests
import telebot
from loguru import logger

from src.agent import transcrever
from src.core import configure_logger, settings
from src.strings import BOT_BOAS_VINDAS, BOT_ERRO, BOT_PROCESSANDO, BOT_SEM_RESULTADO

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def _perguntar_para_api(pergunta: str) -> dict:
    resposta = requests.get(
        f"{settings.API_URL}/consulta",
        params={"pergunta": pergunta},
        timeout=120,
    )
    if resposta.status_code >= 400:
        raise RuntimeError(resposta.json().get("detail", resposta.text))
    return resposta.json()


def _formatar(dados: dict) -> str:

    linhas = dados.get("linhas", [])
    if not linhas:
        return BOT_SEM_RESULTADO

    partes = [f"Encontrei {dados['total']} resultado(s):\n"]
    for item in linhas[:20]:
        campos = [f"{chave}: {valor}" for chave, valor in item.items() if valor is not None]
        partes.append("- " + " | ".join(campos))

    if len(linhas) > 20:
        partes.append(f"\n(mostrando 20 de {len(linhas)})")

    partes.append(f"\nConsulta usada:\n{dados['sql']}")
    return "\n".join(partes)


def _responder(message, pergunta: str) -> None:
    bot.reply_to(message, BOT_PROCESSANDO)
    try:
        dados = _perguntar_para_api(pergunta)
        bot.reply_to(message, _formatar(dados))
    except Exception as erro:
        logger.error(f"Erro ao responder: {erro}")
        bot.reply_to(message, BOT_ERRO.format(erro=erro))


@bot.message_handler(commands=["start", "help"])
def boas_vindas(message):
    bot.reply_to(message, BOT_BOAS_VINDAS)


@bot.message_handler(content_types=["voice"])
def mensagem_de_voz(message):
    url_audio = bot.get_file_url(message.voice.file_id)
    try:
        pergunta = transcrever(url_audio)
    except Exception as erro:
        bot.reply_to(message, BOT_ERRO.format(erro=erro))
        return
    _responder(message, pergunta)


@bot.message_handler(func=lambda message: True)
def mensagem_de_texto(message):
    _responder(message, message.text)


def main() -> None:
    configure_logger()
    logger.info("Bot do Telegram iniciado")
    bot.polling(non_stop=True, timeout=60)


if __name__ == "__main__":
    main()