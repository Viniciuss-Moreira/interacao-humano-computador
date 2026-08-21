import os
import sqlite3
import dspy

from .llama_server import LLAMA_API_BASE, download_model, start_llama_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIMIZED_PATH = os.path.join(BASE_DIR, "optimized_sql_generator.json")
DB_PATH = os.path.join(BASE_DIR, "..", "lojas.db")


def get_db_schema():
    """Lê o schema atual do banco de dados dinamicamente."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
    ).fetchall()
    conn.close()
    return "\n".join(row[0] + ";" for row in rows)


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


# Instância global do gerador (carregada uma vez no init_ia)
_generator = None


def init_ia():
    """Inicializa toda a infraestrutura de IA: baixa o modelo, sobe o servidor e configura o dspy."""
    global _generator

    download_model()
    start_llama_server()
    lm = dspy.LM('openai/Qwen3-0.6B', api_base=LLAMA_API_BASE, api_key='not-needed')
    dspy.configure(lm=lm)

    # Carrega o programa otimizado (GEPA) se disponível
    _generator = ReliableSQLGenerator()
    if os.path.exists(OPTIMIZED_PATH):
        _generator.load(OPTIMIZED_PATH)
        print(f"✓ Programa otimizado GEPA carregado: {OPTIMIZED_PATH}")
    else:
        print("⚠ Programa base (não otimizado). Execute run_gepa_optimization() para otimizar.")


def generate_sql(question):
    """Recebe uma pergunta em linguagem natural e retorna a query SQL gerada pela IA."""
    global _generator

    schema = get_db_schema()

    if _generator is None:
        _generator = ReliableSQLGenerator()

    sql = _generator.forward(schema, question)
    print(sql)
    print(sql.sql_query)
    return sql.sql_query
