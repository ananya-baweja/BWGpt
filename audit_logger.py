import database
from datetime import datetime

def log_user_login(login_id):
    """Marks user as active, creates them if they are new, and starts a session."""
    conn = database.get_connection()
    if not conn: return None
    
    try:
        cursor = conn.cursor()
        
        # 1. Check if the user already exists in the Master Table
        cursor.execute("SELECT 1 FROM Admin.Users WHERE loginIdM = ?", login_id)
        user_exists = cursor.fetchone()
        
        if not user_exists:
            # If they are brand new, INSERT them!
            insert_user_sql = """
                INSERT INTO Admin.Users (loginIdM, emailAdd, isActive, createDt) 
                VALUES (?, ?, 'Y', GETDATE())
            """
            cursor.execute(insert_user_sql, login_id, login_id)
        else:
            # If they already exist, just UPDATE their status!
            update_user_sql = """
                UPDATE Admin.Users 
                SET isActive = 'Y', updateDt = GETDATE() 
                WHERE loginIdM = ?
            """
            cursor.execute(update_user_sql, login_id)
        
        # 2. Start the Session Ledger and grab the new SessionId
        insert_session_sql = """
            INSERT INTO Admin.LoginHistory (loginIdM, LoginTime) 
            OUTPUT INSERTED.SessionId
            VALUES (?, GETDATE())
        """
        cursor.execute(insert_session_sql, login_id)
        session_id = cursor.fetchone()[0]
        
        conn.commit()
        return session_id
        
    except Exception as e:
        print(f"Audit Log Error (Login): {e}")
        return None

def log_user_logout(login_id, session_id):
    """Marks user as inactive and closes out their session timer."""
    if not session_id: return
    
    conn = database.get_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        
        update_user_sql = """
            UPDATE Admin.Users 
            SET isActive = 'N', updateDt = GETDATE() 
            WHERE loginIdM = ?
        """
        cursor.execute(update_user_sql, login_id)
        
        close_session_sql = """
            UPDATE Admin.LoginHistory 
            SET LogoutTime = GETDATE() 
            WHERE SessionId = ?
        """
        cursor.execute(close_session_sql, session_id)
        
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error (Logout): {e}")

def log_chat_query(login_id, user_prompt, generated_sql):
    """Stamps the exact question and AI-generated SQL into the ChatLogs table."""
    conn = database.get_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        insert_chat_sql = """
            INSERT INTO Admin.ChatLogs (loginIdM, UserPrompt, GeneratedSQL, SystemTime) 
            VALUES (?, ?, ?, GETDATE())
        """
        cursor.execute(insert_chat_sql, login_id, user_prompt, generated_sql)
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error (Chat): {e}")