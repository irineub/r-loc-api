import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r-loc.db")
    print(f"Connecting to database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(locacoes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'frete' not in columns:
            print("Adding 'frete' column to 'locacoes' table...")
            cursor.execute("ALTER TABLE locacoes ADD COLUMN frete FLOAT DEFAULT 0.0")
            
            # Now update the frete of all existing locacoes to match to their orcamento frete
            print("Copying historical frete from orcamentos to locacoes...")
            cursor.execute("""
                UPDATE locacoes
                SET frete = (
                    SELECT frete FROM orcamentos WHERE orcamentos.id = locacoes.orcamento_id
                )
                WHERE locacao_original_id IS NULL
            """)
            conn.commit()
            print("Column 'frete' added and populated successfully.")
        else:
            print("Column 'frete' already exists in 'locacoes'.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
