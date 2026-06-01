import ollama
from datetime import datetime

def stream_sql(user_input, schema):
    """
    Streams a translated SQL query chunk-by-chunk using a local Ollama model.
    """
    # Fetch the exact date and year dynamically at the moment the user asks the question
    today_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    system_prompt = f"""
    You are an expert database administrator. You write EXACT, valid T-SQL code for Microsoft SQL Server.
    
    TEMPORAL AWARENESS: 
    Today's date is {today_date}. If the user asks for a date, month, or time period without explicitly stating the year, you MUST default to the current year ({current_year}).
    
    Schema:
    {schema}
    
    Rule 1: Return ONLY the raw SQL query. No markdown formatting (```sql), no backticks, no explanations.
    Rule 2: You are writing T-SQL. To limit row returns, you MUST use 'SELECT TOP (N)'. 
    
    Example Question: Which department has the maximum budget?
    Example Answer: SELECT TOP (1) DepartmentName, AnnualBudget FROM Departments ORDER BY AnnualBudget DESC
    """
    
    try:
        # stream=True enables the real-time typing effect
        stream_generator = ollama.chat(
            model='qwen3:8b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input}
            ],
            stream=True
        )
        
        for chunk in stream_generator:
            yield chunk['message']['content']
            
    except Exception as e:
        raise Exception(f"Failed to connect to local Ollama model: {e}")