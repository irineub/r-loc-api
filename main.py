from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import clientes, equipamentos, orcamentos, locacoes, funcionarios, logs

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="R-Loc API",
    description="Sistema de Locação de Equipamentos de Construção",
    version="1.0.0",
    openapi_version="3.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:4200", "http://localhost:4201", "https://srv938431.hstgr.cloud", "https://*.ngrok-free.app"],  # Angular dev server
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(equipamentos.router, prefix="/equipamentos", tags=["Equipamentos"])
app.include_router(orcamentos.router, prefix="/orcamentos", tags=["Orçamentos"])
app.include_router(locacoes.router, prefix="/locacoes", tags=["Locações"])
app.include_router(funcionarios.router, prefix="/funcionarios", tags=["Funcionários"])
app.include_router(logs.router, prefix="/logs", tags=["Logs"])

@app.get("/")
async def root():
    return {"message": "R-Loc API - Sistema de Locação de Equipamentos"} 