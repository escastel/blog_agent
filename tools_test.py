"""Prueba de integracion de las funciones HTTP sin modelo IA."""
from tools import list_posts, create_draft

before = list_posts()
print("Artículos publicados antes:", len(before))

created = create_draft(
    "Prueba de robótica en el aula",
    "Texto de laboratorio; esto es un texto de prueba.",
)
assert created["estado"] == "borrador"
assert all(a["id"] != created["id"] for a in list_posts())

print("Borrador creado:", created["id"])
print("Comprobación: el borrador no es público")