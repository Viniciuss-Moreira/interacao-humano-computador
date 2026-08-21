import os
import sqlite3
import dspy

from .llama_server import LLAMA_API_BASE, download_model, start_llama_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIMIZED_PATH = os.path.join(BASE_DIR, "optimized_sql_generator.json")
DB_PATH = os.path.join(BASE_DIR, "..", "lojas.db")


def get_db_schema():
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
        ).fetchall()
        return "\n".join(row[0] + ";" for row in rows)
    finally:
        conn.close()


class TextToSQL(dspy.Signature):
    """Generate SQL from natural language."""
    dbschema = dspy.InputField(desc="Database schema")
    question = dspy.InputField(desc="Natural language question")
    sql_query = dspy.OutputField(desc="Valid SQL query")


class RefineSQL(dspy.Signature):
    """Fix a SQL query that failed to execute."""
    dbschema = dspy.InputField(desc="Database schema")
    question = dspy.InputField(desc="Natural language question")
    previous_sql = dspy.InputField(desc="SQL query that failed")
    error_message = dspy.InputField(desc="Error from executing the SQL")
    sql_query = dspy.OutputField(desc="Corrected SQL query")


def _try_execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(sql)
        return None
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()


class RecursiveSQLGenerator(dspy.Module):
    def __init__(self, max_retries=3):
        super().__init__()
        self.generate = dspy.Predict(TextToSQL)
        self.refine = dspy.Predict(RefineSQL)
        self.max_retries = max_retries

    def forward(self, schema, question):
        pred = self.generate(dbschema=schema, question=question)

        for _ in range(self.max_retries):
            error = _try_execute_sql(pred.sql_query)
            if error is None:
                return pred
            pred = self.refine(
                dbschema=schema,
                question=question,
                previous_sql=pred.sql_query,
                error_message=error,
            )

        return pred


_generator = None


def init_ia():
    global _generator

    download_model()
    start_llama_server()
    lm = dspy.LM('openai/Qwen3-0.6B', api_base=LLAMA_API_BASE, api_key='not-needed')
    dspy.configure(lm=lm)

    _generator = RecursiveSQLGenerator()
    if os.path.exists(OPTIMIZED_PATH):
        _generator.load(OPTIMIZED_PATH)
        print(OPTIMIZED_PATH, "loaded")


def generate_sql(question):
    global _generator

    schema = get_db_schema()

    if _generator is None:
        _generator = RecursiveSQLGenerator()

    result = _generator.forward(schema, question)
    print(result.sql_query)
    return result.sql_query
