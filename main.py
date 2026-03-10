from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.routers import clientes, equipamentos, orcamentos, locacoes, funcionarios, logs, upload, config, pdf, relatorios

# ... existing code ...


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="R-Loc API",
    description="Sistema de Locação de Equipamentos de Construção",
    version="1.0.0",
    openapi_version="3.1.0",
)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:4200", "http://localhost:4201", "https://srv938431.hstgr.cloud", "https://*.ngrok-free.app"],  # Angular dev server
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"Erro não tratado: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )

# Include routers
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(equipamentos.router, prefix="/api/equipamentos", tags=["Equipamentos"])
app.include_router(orcamentos.router, prefix="/api/orcamentos", tags=["Orçamentos"])
app.include_router(locacoes.router, prefix="/api/locacoes", tags=["Locações"])
app.include_router(funcionarios.router, prefix="/api/funcionarios", tags=["Funcionários"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(config.router, prefix="/api/config", tags=["Config"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF"])

@app.get("/api")
async def root():
    return {"message": "R-Loc API - Sistema de Locação de Equipamentos"} 