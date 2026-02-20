from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import Response
import os

router = APIRouter()


def _replace_logo_paths(html: str) -> str:
    """Substitui caminhos relativos do logo por caminho absoluto de arquivo."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # r-loc-api/app/routers → r-loc-api/assets
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "assets")
    logo_path = os.path.join(assets_dir, "logo-r-loc.jpg")

    if os.path.exists(logo_path):
        for ref in ["/logo-r-loc.jpg", "./assets/logo-r-loc.jpg"]:
            html = html.replace(f'src="{ref}"', f'src="file://{logo_path}"')
            html = html.replace(f"src='{ref}'", f"src='file://{logo_path}'")
    return html


def _try_weasyprint(html: str) -> bytes:
    """Tenta gerar PDF com WeasyPrint (alta qualidade)."""
    from weasyprint import HTML
    return HTML(string=html).write_pdf()


def _try_xhtml2pdf(html: str) -> bytes:
    """Tenta gerar PDF com xhtml2pdf (pure-Python)."""
    from io import BytesIO
    from xhtml2pdf import pisa
    buf = BytesIO()
    result = pisa.CreatePDF(html.encode("utf-8"), dest=buf)
    if result.err:
        raise RuntimeError(f"xhtml2pdf error code {result.err}")
    return buf.getvalue()


def _generate_simple_pdf_from_html(html: str) -> bytes:
    """
    Fallback usando reportlab — extrai texto limpo do HTML e gera um PDF simples.
    Não rende CSS/tabelas complexas, mas garante que algo seja entregue.
    """
    import re
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    # Remover tags HTML e manter texto limpo
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'\s{3,}', '\n\n', text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    story = []
    for line in lines:
        story.append(Paragraph(line, normal))
        story.append(Spacer(1, 4))
    doc.build(story)
    return buf.getvalue()


@router.post("/generate")
async def generate_pdf(
    html: str = Body(..., embed=True),
):
    """
    Gera um PDF a partir de HTML.
    Tenta WeasyPrint (melhor qualidade) → xhtml2pdf → reportlab (fallback texto).
    """
    try:
        modified_html = _replace_logo_paths(html)
        errors = []

        # 1. WeasyPrint
        try:
            return Response(content=_try_weasyprint(modified_html), media_type="application/pdf")
        except ImportError:
            errors.append("WeasyPrint: não instalado")
        except Exception as e:
            err = str(e)
            if any(lib in err for lib in ["libpango", "libcairo", "libgdk", "libffi", "cannot load", "No such file"]):
                errors.append(f"WeasyPrint: libs de sistema ausentes ({err[:100]})")
            else:
                errors.append(f"WeasyPrint: {err[:100]}")

        # 2. xhtml2pdf
        try:
            return Response(content=_try_xhtml2pdf(modified_html), media_type="application/pdf")
        except ImportError:
            errors.append("xhtml2pdf: não instalado")
        except Exception as e:
            errors.append(f"xhtml2pdf: {str(e)[:100]}")

        # 3. reportlab (fallback — texto simples, sem layout rico)
        try:
            pdf_bytes = _generate_simple_pdf_from_html(modified_html)
            return Response(content=pdf_bytes, media_type="application/pdf")
        except Exception as e:
            errors.append(f"reportlab: {str(e)[:100]}")

        # Nenhum gerador funcionou
        raise HTTPException(
            status_code=500,
            detail=(
                "Nenhum gerador de PDF disponível no servidor. Erros: "
                + " | ".join(errors)
                + ". Instale: sudo apt-get install -y libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0"
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
