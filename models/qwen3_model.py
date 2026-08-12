import dspy

from .llama_server import LLAMA_API_BASE, download_model, start_llama_server


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


def init_ia():
    """Inicializa toda a infraestrutura de IA: baixa o modelo, sobe o servidor e configura o dspy."""
    download_model()
    start_llama_server()
    lm = dspy.LM('openai/Qwen3-0.6B', api_base=LLAMA_API_BASE, api_key='not-needed')
    dspy.configure(lm=lm)


def generate_sql(question):
    """Recebe uma pergunta em linguagem natural e retorna a query SQL gerada pela IA."""
    schema = """
    CREATE TABLE produtos (
      nome VARCHAR(50),
      departmento VARCHAR(50),
    );
    """
    generator = ReliableSQLGenerator()
    sql = generator.forward(schema, question)
    print(sql)
    print(sql.sql_query)
    return sql.sql_query
