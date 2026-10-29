"""Agente único con límite de pasos y dos herramientas verificadas."""
import json
import os
from ollama import chat
from tools import list_posts, create_draft

MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
TOOLS = {
    "list_posts": list_posts,
    "create_draft": create_draft,
}
RULES = (
    "Eres redactor de un blog de robótica. Trabaja solo con los hechos "
    "que facilite el usuario; no inventes hechos, citas ni enlaces. "
    "Antes de crear un borrador, consulta los articulos publicados. "
    "Si faltan datos, pide aclaración. Puedes crear como máximo "
    "un borrador, nunca publicar ni borrar. "
    "Indica que es una simulación si los hechos son ficticios."
)


def execute(promt: str) -> None:
    msg = [
        {"role": "system", "content": RULES},
        {"role": "user", "content": promt},
    ]
    consulted = False
    save = False
    for _ in range(6):
        result = chat(
            model=MODEL,
            messages=msg,
            tools=list(TOOLS.values()),
        )
        msg.append(result.message)
        calls = result.message.tool_calls or []
        if not calls:
            print(result.message.content or "Sin result final del modelo")
            return
        for call in calls:
            name = call.function.name
            args = call.function.arguments
            try:
                if name not in TOOLS:
                    raise ValueError("Herramienta no autorizada")
                if name == "create_draft" and not consulted:
                    raise ValueError("Consulta articulos antes de guardar")
                if name == "create_draft" and save:
                    raise ValueError("Ya se ha creado un borrador")
                if not isinstance(args, dict):
                    raise ValueError("Argumentos no validos")
                resultado = TOOLS[name](**args)
                if name == "list_posts":
                    consulted = True
                if name == "create_draft":
                    save = True
            except Exception as error:
                resultado = {"error": type(error).__name__, "detalle": str(error)}
            print("Herramienta:", name, "->", resultado)
            msg.append({
                "role": "tool",
                "tool_name": name,
                "content": json.dumps(resultado, ensure_ascii=False),
            })
    print("Detenido: máximo de seis ciclos alcanzado")

if __name__ == "__main__":
    execute(input("Cuéntame tu idea para el artículo: "))