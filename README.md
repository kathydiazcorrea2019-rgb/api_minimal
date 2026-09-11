# API de Equipos

Ejemplo básico de una API REST construida con **FastAPI** siguiendo una arquitectura por capas (rutas → servicios → schemas). El tema del recurso es **equipos**.

## Stack

- Python 3.12
- [FastAPI](https://fastapi.tiangolo.com/)
- Uvicorn (servidor ASGI)
- Pydantic (validación de datos)

## Estructura del proyecto

```
api_minimal/
└── app/
    ├── main.py                    # Instancia de FastAPI y registro de routers
    ├── routers/
    │   └── equipos.py             # Definición de los endpoints (rutas)
    ├── services/
    │   └── equipo_service.py      # Lógica de negocio (datos en memoria)
    └── schemas/
        └── equipo.py              # Modelos Pydantic (EquipoCreate, EquipoResponse)
```

## Requisitos e instalación

1. (Opcional pero recomendado) Crear y activar un entorno virtual:

```bash
   python -m venv .venv

   # Linux / macOS
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
```

2. Instalar las dependencias:

```bash
   pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto (`api_minimal/`):

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

## Dónde probar la API

Con la app corriendo, abre en el navegador:

| Interfaz | URL |
|----------|-----|
| **Swagger UI** (recomendada) | http://127.0.0.1:8000/docs |
| **ReDoc** | http://127.0.0.1:8000/redoc |
| Endpoint raíz | http://127.0.0.1:8000/ |

Swagger te permite probar cada endpoint de forma interactiva sin escribir código.

## Endpoints implementados

El CRUD de equipos está **completo**:

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/equipos/` | Lista todos los equipos |
| `GET` | `/equipos/{equipo_id}` | Obtiene un equipo por su id |
| `POST` | `/equipos/` | Crea un nuevo equipo |
| `PUT` | `/equipos/{equipo_id}` | Actualiza el nombre y la categoría de un equipo existente |
| `DELETE` | `/equipos/{equipo_id}` | Elimina un equipo por su id |

Modelo de un equipo:

```json
{
  "id": 1,
  "nombre": "Barcelona",
  "categoria": "Futbol",
  "disponible": true
}
```

Para crear o actualizar un equipo solo se envían `nombre` (3–80 caracteres) y `categoria` (3–50 caracteres); el `id` y `disponible` los genera/mantiene la API.

### Manejo de errores

| Código | Cuándo ocurre |
|--------|----------------|
| `404` | El `equipo_id` no corresponde a ningún equipo registrado (en `GET /{id}`, `PUT` y `DELETE`) |
| `400` | En `PUT`, el nuevo nombre ya pertenece a **otro** equipo distinto al que se está actualizando |
| `422` | El cuerpo enviado no cumple con las validaciones de `EquipoCreate` (longitud de `nombre`/`categoria`, tipos, etc.) |

## Arquitectura

- **`routers/equipos.py`**: define las rutas HTTP (`GET`, `POST`, `PUT`, `DELETE`) y delega toda la lógica de negocio al servicio.
- **`services/equipo_service.py`**: contiene la lógica de negocio y el almacenamiento en memoria (`_equipos`). Funciones: `listar_equipos`, `obtener_equipo`, `crear_equipo`, `actualizar_equipo`, `eliminar_equipo`. Los errores de negocio (equipo no encontrado, nombre duplicado) se lanzan aquí mediante `HTTPException`.
- **`schemas/equipo.py`**: modelos Pydantic reutilizados en todos los endpoints: `EquipoCreate` (entrada) y `EquipoResponse` (salida).

## Cómo probar

1. Levanta el servidor con `uvicorn app.main:app --reload`.
2. Abre `http://127.0.0.1:8000/docs`.
3. Crea un par de equipos con `POST /equipos/`.
4. Lista los equipos con `GET /equipos/`.
5. Actualiza uno con `PUT /equipos/{equipo_id}` (prueba también con un id inexistente → `404`, y con el nombre de otro equipo ya registrado → `400`).
6. Elimina uno con `DELETE /equipos/{equipo_id}` (prueba también eliminarlo dos veces → la segunda debe dar `404`).
   
1. ¿Qué recibe PUT y qué devuelve?
Recibe dos cosas: el equipo_id (viene en la URL) y un body tipo EquipoCreate (con nombre y categoria). Devuelve el equipo ya actualizado, como EquipoResponse (incluye id y disponible, que no se tocan).

2. ¿Cómo localiza el equipo por id?
Reutiliza obtener_equipo(equipo_id), que recorre la lista _equipos comparando e["id"] == equipo_id. Si lo encuentra, devuelve ese diccionario; si no, ya lanza el 404 automáticamente.

3. ¿Cómo valida el nombre duplicado excluyendo al propio equipo? ¿Por qué importa?
Con any(e["nombre"].lower() == equipo.nombre.lower() and e["id"] != equipo_id for e in _equipos). La condición e["id"] != equipo_id es la clave: sin ella, cada vez que actualices un equipo dejándole el mismo nombre que ya tenía, el sistema lo vería como "duplicado" (porque se compara contra sí mismo) y siempre daría error 400, incluso sin cambiar nada.

4. ¿Cómo maneja "no encontrado"? ¿Qué código y por qué?
No lo maneja directamente — delega en obtener_equipo, que lanza HTTPException(404). Se usa 404 porque semánticamente significa "el recurso solicitado no existe en el servidor", que es exactamente el caso.

5. ¿Qué recibe DELETE y qué devuelve?
Recibe solo el equipo_id. No devuelve contenido (204 No Content) — es el estándar HTTP para "la operación fue exitosa pero no hay nada que mostrar de vuelta".

6. ¿Cómo elimina el equipo?
Primero obtiene la referencia con obtener_equipo(equipo_id), y luego usa _equipos.remove(equipo_existente) para quitar ese diccionario específico de la lista.

7. ¿Cómo maneja "no encontrado" en DELETE?
Igual que en PUT: al llamar obtener_equipo primero, si no existe lanza 404 antes de siquiera intentar eliminar nada.

8. ¿Por qué separar lógica (service) de endpoints (router)?
El router se encarga solo de "recibir la petición HTTP y devolver una respuesta HTTP" (la capa de transporte). El service contiene las reglas de negocio (qué es un nombre duplicado, cómo se guarda un equipo), sin saber nada de HTTP. Ventaja: puedes cambiar cómo se expone la API (agregar otra ruta, otro framework) sin tocar la lógica, o testear la lógica de negocio sin necesitar un servidor corriendo.

9. ¿Qué papel juegan EquipoCreate y EquipoResponse?
EquipoCreate valida los datos de entrada (lo que el cliente envía): fuerza que nombre y categoria cumplan longitud mínima/máxima antes de que lleguen a tu lógica. EquipoResponse define la forma de salida: qué campos exactamente ve el cliente en la respuesta (incluyendo id y disponible, que el cliente no envía pero sí recibe).

10. ¿Qué es HTTPException y por qué se usa?
Es una clase de FastAPI que, al lanzarla (raise), detiene la ejecución e inmediatamente devuelve una respuesta HTTP con el status_code y detail que le indiques. Se usa porque permite manejar errores de negocio (equipo no encontrado, nombre duplicado) de forma limpia, sin tener que envolver cada función en if/else gigantes dentro del router.
