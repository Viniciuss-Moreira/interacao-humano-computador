from datetime import date, timedelta
from typing import List

from loguru import logger

from src.database.connection import get_connection
from src.strings import SUCCESS_DB_CRIADO

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS departamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
    );
    
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    marca TEXT,
    unidade_medida TEXT NOT NULL DEFAULT 'un',
    preco REAL NOT NULL DEFAULT 0,
    departamento_id INTERGER NOT NULL REFERENCES departamento(id)
    );
    
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produto(id),
    lote TEXT NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    data_fabricacao TEXT NOT NULL,
    data_validade TEXT NOT NULL,
    corredor TEXT,
    prateleira TEXT,
    UNIQUE (produto_id, lote)
    );
    
    CREATE INDEX IF NOT EXISTS idx_estoque_validade ON estoque(data_validade);
    CREATE INDEX IF NOT EXISTS idx_produto_marca ON produto(marca);
    """

# A view existe para o LLM: um modelo pequeno acerta muito mais SQL sobre
# UMA tabela plana do que sobre tres tabelas com JOIN.
CREATE_VIEW_SQL = """
CREATE VIEW IF NOT EXISTS vw_estoque AS
SELECT
    e.id              AS id,
    p.nome            AS produto,
    p.marca           AS marca,
    d.nome            AS departamento,
    e.lote            AS lote,
    e.quantidade      AS quantidade,
    p.unidade_medida  AS unidade_medida,
    p.preco           AS preco,
    e.data_fabricacao AS data_fabricacao,
    e.data_validade   AS data_validade,
    CAST(julianday(e.data_validade) - julianday(date('now')) AS INTEGER)
                      AS dias_para_vencer,
    e.corredor        AS corredor,
    e.prateleira      AS prateleira
FROM estoque e
JOIN produto p      ON p.id = e.produto_id
JOIN departamento d ON d.id = p.departamento_id;
"""

DEPARTAMENTOS = [
    "laticinios", "bebidas", "higiene", "limpeza",
    "padaria", "hortifruti", "mercearia", "frios",
]

# (nome, marca, departamento, unidade, preco)
PRODUTOS = [
    ("iogurte natural 170g", "danone", "laticinios", "un", 3.49),
    ("danoninho morango 320g", "danone", "laticinios", "un", 8.99),
    ("iogurte grego 100g", "danone", "laticinios", "un", 6.49),
    ("leite integral 1l", "italac", "laticinios", "l", 4.99),
    ("requeijao cremoso 200g", "nestle", "laticinios", "un", 9.90),
    ("queijo mussarela", "tirolez", "frios", "kg", 39.90),
    ("presunto cozido", "sadia", "frios", "kg", 29.90),
    ("whisky 1l", "johnnie walker", "bebidas", "un", 189.90),
    ("espumante 750ml", "chandon", "bebidas", "un", 119.00),
    ("coca-cola 2l", "coca-cola", "bebidas", "un", 9.49),
    ("agua mineral 500ml", "crystal", "bebidas", "un", 2.50),
    ("sabonete glicerina 90g", "dove", "higiene", "un", 3.20),
    ("creme dental 90g", "colgate", "higiene", "un", 6.70),
    ("detergente neutro 500ml", "ype", "limpeza", "un", 2.89),
    ("pao frances", "padaria da casa", "padaria", "kg", 14.90),
    ("banana prata", "hortifruti local", "hortifruti", "kg", 6.99),
    ("tomate italiano", "hortifruti local", "hortifruti", "kg", 8.49),
    ("arroz branco 5kg", "camil", "mercearia", "un", 27.90),
    ("feijao carioca 1kg", "kicaldo", "mercearia", "un", 8.99),
    ("cafe premium 500g", "melitta", "mercearia", "un", 24.90),
]

LOTES = [
    ("iogurte natural 170g", "L-2201", 24, -25, 0, "3", "A"),
    ("danoninho morango 320g", "L-2202", 12, -20, 0, "3", "A"),
    ("tomate italiano", "L-7702", 25, -3, 0, "9", "B"),
    ("iogurte grego 100g", "L-2203", 30, -18, 2, "3", "B"),
    ("requeijao cremoso 200g", "L-3302", 40, -30, 1, "3", "C"),
    ("pao frances", "L-6601", 15, 0, 1, "2", "A"),
    ("banana prata", "L-7701", 40, -2, 3, "9", "A"),
    ("queijo mussarela", "L-3303", 18, -12, 5, "5", "A"),
    ("danoninho morango 320g", "L-2199", 6, -35, -3, "3", "A"),
    ("presunto cozido", "L-3304", 9, -8, -1, "5", "A"),
    ("iogurte natural 170g", "L-2204", 60, -10, 15, "3", "A"),
    ("leite integral 1l", "L-3301", 120, -15, 45, "4", "C"),
    ("coca-cola 2l", "L-4401", 200, -40, 180, "1", "A"),
    ("agua mineral 500ml", "L-4402", 480, -20, 300, "1", "B"),
    ("whisky 1l", "L-4501", 12, -200, 900, "1", "D"),
    ("espumante 750ml", "L-4502", 30, -150, 500, "1", "D"),
    ("sabonete glicerina 90g", "L-5501", 150, -90, 400, "7", "A"),
    ("creme dental 90g", "L-5502", 90, -70, 365, "7", "A"),
    ("detergente neutro 500ml", "L-5504", 110, -45, 250, "8", "A"),
    ("arroz branco 5kg", "L-8801", 80, -100, 400, "10", "A"),
    ("feijao carioca 1kg", "L-8802", 95, -80, 300, "10", "B"),
    ("cafe premium 500g", "L-8803", 50, -60, 200, "10", "C"),
]


def _data(dias: int) -> str:
    """Deslocamento em dias -> 'YYYY-MM-DD'."""
    return (date.today() + timedelta(days=dias)).isoformat()

def create_db() -> None:
    """Cria o banco, as tabelas, a view e os dados de exemplo."""

    with get_connection() as conection:
        conection.executescript(CREATE_TABLES_SQL)
        conection.executescript(CREATE_VIEW_SQL)

        ja_populado = conection.execute("SELECT COUNT(*) FROM estoque").fetchone()[0]
        if ja_populado:
            return

        conection.executemany(
            "INSERT OR IGNORE INTO departamento (nome) VALUES (?)",
            [(nome,) for nome in DEPARTAMENTOS],
        )

        departamentos = {
            linha["nome"]: linha["id"]
            for linha in conection.execute("SELECT id, nome FROM departamento")
        }

        conection.executemany(
            "INSERT OR IGNORE INTO produto "
            "(nome, marca, unidade_medida, preco, departamento_id) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (nome, marca, unidade, preco, departamentos[departamento])
                for nome, marca, departamento, unidade, preco in PRODUTOS
            ],
        )

        produtos  ={ 
            linha["nome"]: linha["id"]
            for linha in conection.execute("SELECT id, nome FROM produto")
        }
        conection.executemany(
            "INSERT INTO estoque "
            "(produto_id, lote, quantidade, data_fabricacao, data_validade, "
            "corredor, prateleira) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (produtos[produto], lote, qtd, _data(fab), _data(val), corredor, prateleira)
                for produto, lote, qtd, fab, val, corredor, prateleira in LOTES
            ],
        )

    logger.info(SUCCESS_DB_CRIADO.format(total=len(LOTES)))

def get_schema_ddl() -> str:
    """Le o esquema real do banco para montar o prompt do LLM.

    Vem do sqlite_master, nao de uma string mantida a mao: mudou a
    tabela, o prompt muda junto, sem ninguem lembrar de atualizar.
    """
    with get_connection() as connection:
        linhas = connection.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' "
            "ORDER BY CASE type WHEN 'view' THEN 0 ELSE 1 END, name"
        ).fetchall()

    definicoes: List[str] = [linha["sql"] for linha in linhas if linha["sql"]]
    return "\n\n".join(definicoes)

