import csv
import io
from datetime import datetime

# Registro en memoria
# Nota: los logs se pierden si el servidor se reinicia.
# Para persistencia real, migrar a Supabase o PostgreSQL en una fase posterior.
_log: list[dict] = []


def log_interaction(
    user: str,
    category: str,
    question: str,
    was_blocked: bool,
):
    """
    Registra una interacción en memoria.
    - user: número de teléfono hasheado para no almacenar dato personal directo
    - category: línea productiva seleccionada
    - question: texto de la consulta
    - was_blocked: si el filtro bloqueó la respuesta
    """
    _log.append({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user_id": _anonymize(user),
        "category": category,
        "question": question[:300],  # límite por seguridad
        "blocked": "Sí" if was_blocked else "No",
    })


def _anonymize(user: str) -> str:
    """Ofusca el número dejando solo los últimos 4 dígitos."""
    digits = "".join(filter(str.isdigit, user))
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


def export_csv() -> str:
    """
    Devuelve el log completo como string CSV listo para descargar.
    """
    if not _log:
        return "timestamp,user_id,category,question,blocked\n(sin registros)"

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["timestamp", "user_id", "category", "question", "blocked"]
    )
    writer.writeheader()
    writer.writerows(_log)
    return output.getvalue()


def get_summary() -> dict:
    """
    Resumen rápido de indicadores para mostrar en el endpoint de admin.
    """
    if not _log:
        return {"total": 0, "blocked": 0, "by_category": {}}

    blocked = sum(1 for r in _log if r["blocked"] == "Sí")

    by_category: dict[str, int] = {}
    for r in _log:
        cat = r["category"] or "sin_categoría"
        by_category[cat] = by_category.get(cat, 0) + 1

    return {
        "total": len(_log),
        "blocked": blocked,
        "by_category": by_category,
    }