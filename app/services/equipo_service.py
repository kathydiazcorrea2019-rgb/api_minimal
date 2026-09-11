from fastapi import HTTPException

from app.schemas.equipo import EquipoCreate

_equipos: list[dict] = []
_next_id = 1


def listar_equipos() -> list[dict]:
    return _equipos


def obtener_equipo(equipo_id: int) -> dict:
    for e in _equipos:
        if e["id"] == equipo_id:
            return e
    raise HTTPException(
        status_code=404,
        detail="Equipo no encontrado",
    )


def crear_equipo(equipo: EquipoCreate) -> dict:
    global _next_id

    existe = any(
        e["nombre"].lower() == equipo.nombre.lower() for e in _equipos
    )
    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un equipo con ese nombre",
        )

    nuevo = {
        "id": _next_id,
        "nombre": equipo.nombre,
        "categoria": equipo.categoria,
        "disponible": True,
    }
    _equipos.append(nuevo)
    _next_id += 1

    return nuevo

def actualizar_equipo(equipo_id: int, equipo: EquipoCreate) -> dict:
    equipo_existente = obtener_equipo(equipo_id)

    nombre_duplicado = any(
        e["nombre"].lower() == equipo.nombre.lower() and e["id"] != equipo_id
        for e in _equipos
    )
    if nombre_duplicado:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un equipo con ese nombre",
        )

    equipo_existente["nombre"] = equipo.nombre
    equipo_existente["categoria"] = equipo.categoria

    return equipo_existente

def eliminar_equipo(equipo_id: int) -> None:
    equipo_existente = obtener_equipo(equipo_id)
    _equipos.remove(equipo_existente)
    