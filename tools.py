import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BLOG_API_URL", "http://127.0.0.1:8000/api/articulos/").rstrip("/") + "/"

def list_posts() -> list[dict]:
    """Devuelve articulos publicados del blog."""
    result = requests.get(API_URL, timeout=10)
    result.raise_for_status()
    data = result.json()

    if isinstance(data, list):
        return data
    
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return data["results"]
    
    raise ValueError("La API no pudo devolver una lista de articulos")

def create_draft(titulo: str, cuerpo: str) -> dict:
    """Guarda un borrador NO publicado y devuelve sus data."""
    if not all((titulo.strip(), cuerpo.strip())):
        raise ValueError("Titulo y cuerpo no pueden estar vacíos")
    
    token = os.getenv("BLOG_API_TOKEN", "")
    if not token:
        raise RuntimeError("Falta la variable BLOG_API_TOKEN")
    
    result = requests.post(
        API_URL,
        json={"titulo": titulo, "cuerpo": cuerpo},
        headers={"Authorization": f"Token {token}"},
        timeout=15,
    )
    result.raise_for_status()

    data = result.json()
    if data.get("estado") != "borrador":
        raise RuntimeError("La API no ha confirmado el estado borrador")
    
    return data