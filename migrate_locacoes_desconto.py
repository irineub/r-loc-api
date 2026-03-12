import sqlite3

import os

def migrate():
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r-loc.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add desconto
        try:
            cursor.execute("ALTER TABLE locacoes ADD COLUMN desconto FLOAT DEFAULT 0.0")
            print("Successfully added 'desconto' to 'locacoes'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'desconto' already exists.")
            else:
                print(f"Error adding 'desconto': {e}")
                
        # Add desconto_percentual
        try:
            cursor.execute("ALTER TABLE locacoes ADD COLUMN desconto_percentual FLOAT DEFAULT 0.0")
            print("Successfully added 'desconto_percentual' to 'locacoes'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'desconto_percentual' already exists.")
            else:
                print(f"Error adding 'desconto_percentual': {e}")
                
        conn.commit()
        conn.close()
        print("Migration done.")
    except Exception as e:
        print(f"Failed to migrate: {e}")

if __name__ == "__main__":
    migrate()
