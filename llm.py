import json
import ollama
from datetime import datetime

def check_intent(user_prompt):
    """
    Lightning-fast router to check if the user wants a visual/dashboard or raw data.
    """
    system_prompt = """
    You are an ultra-fast intent router. Analyze the user's prompt.
    
    If the user asks to see a dashboard, open a report, or view a visual, respond with this EXACT JSON format:
    {"intent": "DASHBOARD", "pbi_filter": "TableName/ColumnName eq 'Value'"}
    
    CRITICAL POWER BI FILTER RULES:
    - Vendor rule: "Transactions/VendorName eq 'Vendor_Name_Here'"
    - Department rule: "Departments/DepartmentName eq 'Department_Name_Here'"
    - No specific filter: ""
    
    EXAMPLE 1:
    User: "Show me the dashboard for Cloud Compute AWS"
    Output: {"intent": "DASHBOARD", "pbi_filter": "Transactions/VendorName eq 'Cloud Compute AWS'"}
    
    If the user asks a question that requires calculating numbers, listing items, or pulling data tables, respond with:
    {"intent": "DATA", "pbi_filter": ""}
    
    You MUST output ONLY valid JSON.
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
        
        result = json.loads(response['message']['content'])
        return result.get("intent", "DATA"), result.get("pbi_filter", "")
        
    except Exception as e:
        print(f"Intent parsing error: {e}")
        return "DATA", ""


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