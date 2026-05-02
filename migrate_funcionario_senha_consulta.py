import os
import sqlite3


def migrate():
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r-loc.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "ALTER TABLE funcionarios ADD COLUMN senha_ultima_definida TEXT"
            )
            print("Successfully added 'senha_ultima_definida' to 'funcionarios'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'senha_ultima_definida' already exists.")
            else:
                print(f"Error adding 'senha_ultima_definida': {e}")

        conn.commit()
        conn.close()
        print("Migration migrate_funcionario_senha_consulta done.")
    except Exception as e:
        print(f"Failed to migrate: {e}")


if __name__ == "__main__":
    migrate()
