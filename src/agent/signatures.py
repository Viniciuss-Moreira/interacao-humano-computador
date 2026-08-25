import dspy

class TextToSQL(dspy.Signature):
    dbschema = dspy.InputField(desc="Database schema")
    question = dspy.InputField(desc="Natural language question")
    sql_query = dspy.OutputField(desc="Valid SQL query")

class RefineSQL(dspy.Signature):
    dbschema = dspy.InputField(desc="Database schema")
    question = dspy.InputField(desc="Natural language question")
    previous_sql = dspy.InputField(desc="SQL query that failed")
    error_message = dspy.InputField(desc="Error from executing the SQL")
    sql_query = dspy.OutputField(desc="Corrected SQL query")