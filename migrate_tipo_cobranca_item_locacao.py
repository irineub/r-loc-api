import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r-loc.db")
    print(f"Connecting to database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(itens_locacao)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tipo_cobranca' not in columns:
            print("Adding 'tipo_cobranca' column to 'itens_locacao' table...")
            cursor.execute("ALTER TABLE itens_locacao ADD COLUMN tipo_cobranca VARCHAR(20) DEFAULT 'mensal'")
            conn.commit()
            print("Column 'tipo_cobranca' added successfully.")
        else:
            print("Column 'tipo_cobranca' already exists in 'itens_locacao'.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
