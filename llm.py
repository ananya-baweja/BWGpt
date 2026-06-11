import json
import ollama
from datetime import datetime

def stream_sql(user_input, schema):
    """
    Streams a translated SQL query chunk-by-chunk using a local Ollama model.
    """
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
    Rule 3: ALWAYS select and group by human-readable text columns (e.g., DepartmentName, VendorName, ProductName) instead of raw IDs. Never return a raw ID column to the user unless they explicitly ask for it.
    """
    
    try:
        stream_generator = ollama.chat(
            model='qwen2.5-coder:7b-instruct-q8_0',
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


def stream_insights(user_prompt, data_string):
    """
    Takes the raw data and asks the AI to analyze it as a business analyst.
    """
    system_prompt = """
    You are an expert business analyst. Your job is to look at raw data and provide brief, punchy bullet points of business insights. 
    
    Rule 1: Focus on the most important trends, highest numbers, or anomalies.
    Rule 2: Keep the bullet points short (1-2 sentences max).
    Rule 3: NEVER write SQL or Python code here. Just plain English insights.
    Rule 4: Do not include introductory filler text (e.g., "Here are the insights..."). Just start with the bullet points.
    Rule 5: NEVER use markdown formatting like bold (**text**) or italics. Generate plain text only.
    """
    
    user_message = f"User's Question: {user_prompt}\n\nData Returned:\n{data_string}"
    
    try:
        stream_generator = ollama.chat(
            model='qwen2.5-coder:7b-instruct-q8_0',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            stream=True
        )
        
        for chunk in stream_generator:
            yield chunk['message']['content']
            
    except Exception as e:
        yield f"⚠️ Could not generate insights: {e}"


def generate_chart_spec(user_prompt, schema):
    """
    Generates a clean JSON containing both the T-SQL query and chart configuration 
    for custom native chart rendering inside the dedicated UI workspace.
    """
    system_prompt = f"""
    You are a data visualization assistant. Translate the user's plotting request into a single database SQL query and configuration parameters.
    
    Schema context:
    {schema}
    
    Supported chart types: "bar", "line", "scatter", "pie".
    
    Return EXACTLY a valid JSON object conforming to this structure:
    {{
        "sql": "SELECT Column1, Column2 FROM ...",
        "chart_config": {{
            "type": "bar",
            "x": "Column1",
            "y": "Column2"
        }}
    }}
    
    Rule 1: The 'sql' attribute MUST contain a single, executable T-SQL query.
    Rule 2: No markdown wraps (no ```json codeblocks), no introductory or conversational remarks. Output only the raw JSON.
    """
    
    try:
        response = ollama.chat(
            model='qwen2.5-coder:7b-instruct-q8_0',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            format='json'
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"Chart configuration spec error: {e}")
        return None