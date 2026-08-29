#erros gerias
ERROR_RESOURCE_NOT_FOUND = "Recurso nao encontrado"
ERROR_INVALID_REQUEST = "Requisicao invalida"
ERROR_INTERNAL_SERVER = "Erro interno do servidor"
ERROR_INVALID_INPUT = "Erro ao processar a requisicao: entrada invalida"

#erros consultas
ERROR_SQL_NAO_PERMITIDO = "Somente consultas SELECT sao permitidas. Recebido: {comando}"
ERROR_SQL_MULTIPLOS_COMANDOS = "Apenas um comando por consulta e permitido"
ERROR_SQL_VAZIO = "A LLM nao gerou nenhuma consulta"
ERROR_SQL_INVALIDO = "A consulta gerada nao pode ser executada"
ERROR_LLM_INDISPONIVEL = "Nao consegui falar com o modelo de linguagem"
ERROR_TRANSCRICAO = "Nao consegui entender o audio"

#Sucesso
SUCCESS_DB_CRIADO = "Banco criado e populado {total} lotes!"
SUCCESS_SQL_GERADO = "SQL gerado para '{pergunta}': {sql}"
SUCCESS_CONSULTA = "Consulta executada: {total} linha(s)"
SUCCESS_TRANSCRICAO = "Audio transcrito: {texto}"


#Mensaem Bot
BOT_BOAS_VINDAS = (
    "Ola! Pergunte sobre o estoque do mercado, por texto ou audio.\n\n"
    "Exemplos:\n"
    "- Quais produtos vencem hoje?\n"
    "- Quais produtos custam mais de 100 reais?\n"
    "- Quantos danones tem no estoque?"
)
BOT_SEM_RESULTADO = "Nao encontrei nada para essa pergunta."
BOT_PROCESSANDO =  "Consulta o estoque..."
BOT_ERRO = "Deu erro aqui: {erro}"