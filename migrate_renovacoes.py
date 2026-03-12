import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('r-loc.db')
        cursor = conn.cursor()
        
        # Add locacao_original_id
        try:
            cursor.execute("ALTER TABLE locacoes ADD COLUMN locacao_original_id INTEGER REFERENCES locacoes(id)")
            print("Successfully added 'locacao_original_id' to 'locacoes'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'locacao_original_id' already exists.")
            else:
                print(f"Error adding 'locacao_original_id': {e}")
                
        conn.commit()
        conn.close()
        print("Migration done.")
    except Exception as e:
        print(f"Failed to migrate renovacoes: {e}")

if __name__ == "__main__":
    migrate()
