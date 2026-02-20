from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response
import os
from app.auth import require_master
from fastapi import Depends

router = APIRouter()

@router.post("/generate")
async def generate_pdf(
    html: str = Body(..., embed=True),
    _: str = Depends(require_master)
):
    try:
        from weasyprint import HTML, CSS
        
        # Obter caminho absoluto para assets
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # assumindo estrutura r-loc-api/app/routers/pdf.py -> r-loc-api/assets
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "assets")
        logo_path = os.path.join(assets_dir, "logo-r-loc.jpg")
        
        # Substituir caminho da imagem para caminho absoluto do arquivo
        # O frontend usa /logo-r-loc.jpg ou ./assets/logo-r-loc.jpg
        # Vamos ser robustos e substituir qualquer referência ao logo
        modified_html = html.replace('src="/logo-r-loc.jpg"', f'src="file://{logo_path}"')
        modified_html = modified_html.replace("src='/logo-r-loc.jpg'", f"src='file://{logo_path}'")
        
        # Configurar WeasyPrint
        pdf_bytes = HTML(string=modified_html).write_pdf()
        
        return Response(content=pdf_bytes, media_type="application/pdf")
        
    except ImportError:
        raise HTTPException(status_code=500, detail="WeasyPrint não está instalado no servidor")
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
