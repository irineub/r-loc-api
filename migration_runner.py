import os
import json
import importlib.util

MIGRATION_HISTORY_FILE = "migration_history.json"
MIGRATION_DIR = os.path.dirname(os.path.abspath(__file__))

def run_migrations():
    print("--- Sistema de Migração Automática ---")
    print("Verificando migrações de banco de dados...")
    
    # Load history
    history = []
    if os.path.exists(MIGRATION_HISTORY_FILE):
        try:
            with open(MIGRATION_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Erro ao ler {MIGRATION_HISTORY_FILE}: {e}")
            
    # Find all migration files
    migration_files = []
    for f in os.listdir(MIGRATION_DIR):
        if f.startswith("migrate_") and f.endswith(".py"):
            migration_files.append(f)
            
    migration_files.sort()
    
    applied_any = False
    
    for filename in migration_files:
        if filename not in history:
            print(f"Aplicando migração pendente: {filename}...")
            # Import and run
            module_name = filename[:-3]
            file_path = os.path.join(MIGRATION_DIR, filename)
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'migrate'):
                    module.migrate()
                    print(f"✓ Migração {filename} concluída.")
                else:
                    print(f"⚠️ Aviso: Arquivo {filename} não possui uma função 'migrate()'.")
                    
                # Mark as applied even if it didn't have migrate() just to avoid repeating
                history.append(filename)
                applied_any = True
                
            except Exception as e:
                print(f"❌ Erro ao aplicar {filename}: {e}")
                
    if applied_any:
        # Save history
        with open(MIGRATION_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        print("Todas as migrações pendentes foram aplicadas e registradas.")
    else:
        print("✓ Banco de dados já está atualizado com as últimas migrações.")
    print("--------------------------------------")

if __name__ == "__main__":
    run_migrations()
