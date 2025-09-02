import pymysql # Libreria per connettersi a MySQL
from config import Config # Configurazioni database
from datetime import datetime # Per gestire date/ore

def get_connection(): # Funzione per connettersi al database
    return pymysql.connect( # Crea connessione usando:
        host=Config.DB_HOST, #indirizzo db
        user=Config.DB_USER, #username
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4' #codifica caratteri
    )

def init_database():
    try:
        print(f"Connessione al database: {Config.DB_HOST}")
        print(f"Nome database: {Config.DB_NAME}")
        
        # Crea database se non exists
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor() # Crea cursore per eseguire query
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}`")
        conn.close() # Chiude la connessione
        print("Database creato/verificato!")
        
        # Crea tabella conversations
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_ip VARCHAR(45)
            )
        ''')
        conn.commit() # Salva le modifiche
        conn.close()
        print("Tabella conversations creata/verificata!")
        
    except Exception as e:
        print(f"Errore durante l'inizializzazione del database: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_conversation(user_message, ai_response, user_ip=None):
    conn = get_connection() # Connessione al database
    cursor = conn.cursor() # Crea cursore per eseguire query
    cursor.execute(
        "INSERT INTO conversations (user_message, ai_response, user_ip) VALUES (%s, %s, %s)",
        (user_message, ai_response, user_ip)
    )
    conn.commit()
    conn.close()

def get_recent_conversations(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_message, ai_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    results = cursor.fetchall()
    conn.close()
    return results