import os
import sqlite3
import dspy
from .generator import RecursiveSQLGenerator, get_db_schema

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIMIZED_PATH = os.path.join(BASE_DIR, "optimized_sql_generator.json")
DB_PATH = os.path.join(BASE_DIR, "..", "lojas.db")

def _example(schema, question, sql_query):
    return dspy.Example(
        dbschema=schema, question=question, sql_query=sql_query
    ).with_inputs("dbschema", "question")

QUERY_TEMPLATES = [
    ("liste todos os {table}",
     "SELECT * FROM {table}"),
    ("quantos {table} existem?",
     "SELECT COUNT(*) FROM {table}"),
    ("quais {col} existem em {table}?",
     "SELECT DISTINCT {col} FROM {table}"),
    ("qual o {target_col} onde {filter_col} é {value}?",
     "SELECT {target_col} FROM {table} WHERE {filter_col} = {value_sql}"),
    ("quantos {table} tem {filter_col} igual a {value}?",
     "SELECT COUNT(*) FROM {table} WHERE {filter_col} = {value_sql}"),
]

def _sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"

def _get_tables_with_columns():
    conn = sqlite3.connect(DB_PATH)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

        result = []
        for (table,) in tables:
            columns = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
            sample_row = conn.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
            result.append((table, columns, sample_row))

        return result
    finally:
        conn.close()

def _expand_templates(table, columns, sample_row):
    pairs = []

    for question_tpl, sql_tpl in QUERY_TEMPLATES:
        for kw in _template_vars(question_tpl, table, columns, sample_row):
            pairs.append((question_tpl.format(**kw), sql_tpl.format(**kw)))

    return pairs

def _template_vars(tpl, table, columns, sample_row):
    if "{target_col}" in tpl:
        return _filter_target_vars(table, columns, sample_row)
    if "{filter_col}" in tpl:
        return _filter_vars(table, columns, sample_row)
    if "{col}" in tpl:
        return [{"table": table, "col": col} for col in columns]
    return [{"table": table}]

def _filter_vars(table, columns, sample_row):
    if not sample_row:
        return []
    return [{"table": table, "filter_col": col, "value": sample_row[i],
             "value_sql": _sql_literal(sample_row[i])}
            for i, col in enumerate(columns)]

def _filter_target_vars(table, columns, sample_row):
    if not sample_row:
        return []
    return [{"table": table, "filter_col": fc, "target_col": tc, "value": sample_row[i],
             "value_sql": _sql_literal(sample_row[i])}
            for i, fc in enumerate(columns)
            for tc in columns if tc != fc]

def build_trainset():
    schema = get_db_schema()
    examples = []

    for table, columns, sample_row in _get_tables_with_columns():
        for question, sql in _expand_templates(table, columns, sample_row):
            examples.append(_example(schema, question, sql))

    return examples

def _execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute(sql).fetchall()
    except sqlite3.Error:
        return None
    finally:
        conn.close()

def sql_results_match(example, pred, trace=None):
    generated = _execute_sql(pred.sql_query.strip().rstrip(";"))
    if generated is None:
        return False

    expected = _execute_sql(example.sql_query.strip().rstrip(";"))
    if expected is None:
        return False

    return sorted(generated) == sorted(expected)

def evaluate_program(program, trainset):
    correct = 0

    for example in trainset:
        try:
            pred = program.forward(example.dbschema, example.question)
            score = sql_results_match(example, pred)
            print(example.question, example.sql_query, pred.sql_query, score)
            if score:
                correct += 1
        except Exception:
            pass

    accuracy = correct / len(trainset) * 100
    print(correct, len(trainset), accuracy)

    return accuracy

def run_gepa_optimization(trainset=None):
    if trainset is None:
        trainset = build_trainset()

    optimizer = dspy.BootstrapFewShot(
        metric=sql_results_match,
        metric_threshold=1.0,
        max_bootstrapped_demos=4,
        max_labeled_demos=4,
        max_rounds=2,
    )

    optimized_program = optimizer.compile(
        RecursiveSQLGenerator(),
        trainset=trainset,
    )

    accuracy = evaluate_program(optimized_program, trainset)

    optimized_program.save(OPTIMIZED_PATH)
    print(OPTIMIZED_PATH, accuracy)

    return optimized_program
