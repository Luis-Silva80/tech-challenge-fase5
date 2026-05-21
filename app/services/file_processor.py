import base64
import fitz  # PyMuPDF
from PIL import Image
import io

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

def file_to_base64(file_bytes: bytes, content_type: str) -> tuple[str, str]:
    """
    Converte o arquivo recebido para base64.
    - Se for imagem: converte direto
    - Se for PDF: extrai a primeira página como imagem
    Retorna: (base64_string, mime_type)
    """
    if content_type in SUPPORTED_IMAGE_TYPES:
        encoded = base64.b64encode(file_bytes).decode("utf-8")
        return encoded, content_type

    if content_type == "application/pdf":
        return _pdf_to_base64(file_bytes)

    raise ValueError(f"Tipo não suportado: {content_type}")

def _pdf_to_base64(file_bytes: bytes) -> tuple[str, str]:
    """
    Extrai a primeira página do PDF e converte para PNG em base64.
    """
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

    if pdf_document.page_count == 0:
        raise ValueError("PDF não contém páginas.")

    page = pdf_document[0]
    pix = page.get_pixmap(dpi=150)

    img_bytes = pix.tobytes("png")
    encoded = base64.b64encode(img_bytes).decode("utf-8")

    return encoded, "image/png"
