import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('r-loc.db')
        cursor = conn.cursor()
        
        # Add assinatura_realizada
        try:
            cursor.execute("ALTER TABLE locacoes ADD COLUMN assinatura_realizada BOOLEAN DEFAULT 0")
            print("Successfully added 'assinatura_realizada' to 'locacoes'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'assinatura_realizada' already exists.")
            else:
                print(f"Error adding 'assinatura_realizada': {e}")
                
        # Add assinatura_base64
        try:
            cursor.execute("ALTER TABLE locacoes ADD COLUMN assinatura_base64 TEXT")
            print("Successfully added 'assinatura_base64' to 'locacoes'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'assinatura_base64' already exists.")
            else:
                print(f"Error adding 'assinatura_base64': {e}")
                
        # Mapeamento do SQLite para BOOLEAN é tipicamente INTEGER (0 ou 1)
        # SQLAlchemy pode lidar com isso. O SQLite aceita "BOOLEAN" na sintaxe e trata internamente como numérico ou int.

        conn.commit()
        conn.close()
        print("Migration done.")
    except Exception as e:
        print(f"Failed to migrate: {e}")

if __name__ == "__main__":
    migrate()
