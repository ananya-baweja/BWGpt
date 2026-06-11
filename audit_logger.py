import database
import uuid
from datetime import datetime

def log_user_login(login_id):
    """Marks user as active, creates them if they are new, and logs the LOGIN event."""
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
        
        # 2. Start the Session Ledger by creating a UUID and logging the event
        session_id = uuid.uuid4().hex
        insert_session_sql = """
            INSERT INTO Admin.ActivityLogs (loginIdM, SessionId, EventType, EventTime) 
            VALUES (?, ?, 'LOGIN', GETDATE())
        """
        cursor.execute(insert_session_sql, login_id, session_id)
        
        conn.commit()
        return session_id
        
    except Exception as e:
        print(f"Audit Log Error (Login): {e}")
        return None


def log_user_logout(login_id, session_id):
    """Marks user as inactive and drops a LOGOUT event into the ledger."""
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
        
        # Insert a LOGOUT event timestamp rather than updating the old login row
        close_session_sql = """
            INSERT INTO Admin.ActivityLogs (loginIdM, SessionId, EventType, EventTime) 
            VALUES (?, ?, 'LOGOUT', GETDATE())
        """
        cursor.execute(close_session_sql, login_id, session_id)
        
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error (Logout): {e}")


def log_chat_query(login_id, user_prompt, generated_sql, session_id=None):
    """Stamps the exact question and AI-generated SQL into the ActivityLogs table."""
    conn = database.get_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        insert_chat_sql = """
            INSERT INTO Admin.ActivityLogs (loginIdM, SessionId, EventType, UserPrompt, GeneratedSQL, EventTime) 
            VALUES (?, ?, 'CHAT', ?, ?, GETDATE())
        """
        cursor.execute(insert_chat_sql, login_id, session_id, user_prompt, generated_sql)
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error (Chat): {e}")