def migrate():
    """Libera estoque indevidamente ocupado por orçamentos ainda não aprovados."""
    from app.database import SessionLocal
    from app import crud

    db = SessionLocal()
    try:
        crud.recalcular_estoque_alugado(db)
        db.commit()
        print("Estoque alugado recalculado: apenas locações ativas/atrasadas e orçamentos aprovados sem contrato.")
    except Exception as e:
        db.rollback()
        print(f"Falha ao recalcular estoque alugado: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
