import dspy

class TextToSQL(dspy.Signature):
    """Gera uma consulta SQL SELECT a partir de uma pergunta em portugues.
    
    Regras:
        - Responda APENAS com SQL valido para SQLite.
        - Use somente SELECT. Nunca INSERT, UPDATE, DELETE ou DROP.
        - Prefira a view vw_estoque, que ja tem produto, departamento e validade.
        - Hoje e date('now'). "vence hoje" e data_validade = date('now').
        - Busca por nome ou marca usa LIKE, ex: marca LIKE '%danone%'.
        """

    dbschema = dspy.InputField(desc="Esquema do banco (CREATE TABLE / CREATE VIEW)")
    question = dspy.InputField(desc="Pergunta em linguagem natural")

    sql_query = dspy.OutputField(desc="Consulta SQL SELECT valida para SQLite")

    