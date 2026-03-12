import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('/home/irineu/rloc/r-loc-api/r-loc.db')
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
