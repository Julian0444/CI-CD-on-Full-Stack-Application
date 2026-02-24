# API Contract — Backend

> **Fuente:** Extraído directamente del código Go (`main.go`, `routes.go`, handlers, services).
> **Fecha:** 2026-02-11
> **Propósito:** Referencia canónica para la migración Go → Django. Ningún endpoint, payload o status code debe cambiar.

---

## Información general

| Propiedad           | Valor                          |
|---------------------|--------------------------------|
| Puerto por defecto  | `8080` (env: `PORT`)           |
| Prefijo de rutas    | Ninguno (rutas en raíz `/`)    |
| Content-Type        | `application/json`             |
| Auth                | Sin JWT/tokens. Login valida credenciales y devuelve mensaje. |
| DB original         | MongoDB (colecciones: `users`, `todos`) |
| CORS                | Orígenes por defecto + `FRONT_ORIGINS` env |

---

## Endpoints

### 1. Health Check

```
GET /healthz
```

| Campo       | Detalle                  |
|-------------|--------------------------|
| Auth        | No                       |
| Request     | Sin body                 |
| Response 200| `{"status": "ok"}`       |

---

### 2. Registro de usuario

```
POST /register
```

| Campo       | Detalle                                      |
|-------------|----------------------------------------------|
| Auth        | No                                           |
| Request     | `{"email": "string", "password": "string"}`  |

**Responses:**

| Status | Body                                              | Condición                          |
|--------|---------------------------------------------------|------------------------------------|
| 201    | `{"message": "usuario registrado con exito"}`     | Registro exitoso                   |
| 400    | `{"error": "datos invalidos"}`                    | JSON malformado / bind error       |
| 400    | `{"error": "email y clave son requeridos"}`       | Email o password vacíos tras trim  |
| 409    | `{"error": "usuario ya existe"}`                  | Email duplicado                    |
| 500    | `{"error": "error al registrar usuario"}`         | Error interno                      |

**Lógica de negocio:**
- Email: `strings.ToLower(strings.TrimSpace(email))`
- Password: `strings.TrimSpace(password)`
- Passwords almacenados en texto plano (sin hash)

---

### 3. Login

```
POST /login
```

| Campo       | Detalle                                      |
|-------------|----------------------------------------------|
| Auth        | No                                           |
| Request     | `{"email": "string", "password": "string"}`  |

**Responses:**

| Status | Body                                       | Condición                          |
|--------|--------------------------------------------|------------------------------------|
| 200    | `{"message": "login exitoso"}`             | Credenciales válidas               |
| 400    | `{"error": "datos invalidos"}`             | JSON malformado / bind error       |
| 401    | `{"error": "credenciales invalidas"}`      | Email no existe o password incorrecto |
| 500    | `{"error": "error al autenticar"}`         | Error interno                      |

**Lógica de negocio:**
- Email normalizado (lower + trim) antes de buscar
- Password trimmed antes de comparar
- Si email o password vacíos después de trim → `credenciales invalidas`

---

### 4. Listar usuarios

```
GET /users
```

| Campo       | Detalle                                      |
|-------------|----------------------------------------------|
| Auth        | No                                           |
| Request     | Sin body                                     |

**Responses:**

| Status | Body                                               | Condición       |
|--------|-----------------------------------------------------|-----------------|
| 200    | `{"users": [{"email": "string"}, ...]}`             | OK (puede ser array vacío) |
| 500    | `{"error": "error al obtener usuarios"}`            | Error interno   |

**Nota:** El password NUNCA se expone en la respuesta (se usa `PublicUser`).

---

### 5. Limpiar usuarios

```
DELETE /users
```

| Campo       | Detalle                                      |
|-------------|----------------------------------------------|
| Auth        | No                                           |
| Request     | Sin body                                     |

**Responses:**

| Status | Body                                       | Condición       |
|--------|---------------------------------------------|-----------------|
| 200    | `{"message": "usuarios eliminados"}`        | OK              |
| 500    | `{"error": "error al limpiar usuarios"}`    | Error interno   |

---

### 6. Listar tareas

```
GET /todos?email={email}
```

| Campo       | Detalle                                      |
|-------------|----------------------------------------------|
| Auth        | No                                           |
| Query param | `email` (opcional) — filtra por usuario      |
| Request     | Sin body                                     |

**Responses:**

| Status | Body                                                       | Condición       |
|--------|-------------------------------------------------------------|-----------------|
| 200    | `{"todos": [TodoResponse, ...]}`                            | OK (puede ser array vacío) |
| 500    | `{"error": "error al obtener tareas"}`                      | Error interno   |

**TodoResponse:**
```json
{
  "id": "string (hex ObjectID → en Django será UUID o int como string)",
  "email": "string",
  "title": "string",
  "completed": false,
  "createdAt": "2025-01-01T10:00:00Z"
}
```

**Lógica de negocio:**
- Si `email` presente: normalizar (lower + trim) y filtrar
- Orden: por `createdAt` ascendente

---

### 7. Crear tarea

```
POST /todos
```

| Campo       | Detalle                                              |
|-------------|------------------------------------------------------|
| Auth        | No                                                   |
| Request     | `{"email": "string", "title": "string"}`             |

**Responses:**

| Status | Body                                              | Condición                          |
|--------|---------------------------------------------------|------------------------------------|
| 201    | `{"todo": TodoResponse}`                          | Creación exitosa                   |
| 400    | `{"error": "datos invalidos"}`                    | JSON malformado / bind error       |
| 400    | `{"error": "email y titulo son requeridos"}`      | Email o título vacíos tras trim    |
| 500    | `{"error": "error al crear tarea"}`               | Error interno                      |

**Lógica de negocio:**
- Email normalizado (lower + trim)
- Title trimmed
- `completed` siempre `false` al crear
- `createdAt` se setea al momento de creación

---

### 8. Actualizar tarea

```
PUT /todos/:id
```

| Campo       | Detalle                                              |
|-------------|------------------------------------------------------|
| Auth        | No                                                   |
| URL param   | `id` — string (hex ObjectID en Go, UUID/int en Django) |
| Request     | `{"title": "string?", "completed": bool?}`           |

**Responses:**

| Status | Body                                              | Condición                          |
|--------|---------------------------------------------------|------------------------------------|
| 200    | `{"todo": TodoResponse}`                          | Actualización exitosa              |
| 400    | `{"error": "datos invalidos"}`                    | JSON malformado / bind error       |
| 400    | `{"error": "nada para actualizar"}`               | Ni title ni completed enviados     |
| 400    | `{"error": "id invalido"}`                        | ID no parseable como ObjectID      |
| 404    | `{"error": "tarea no encontrada"}`                | ID no existe en DB                 |
| 500    | `{"error": "error al actualizar tarea"}`          | Error interno                      |

**Lógica de negocio:**
- Al menos `title` o `completed` debe estar presente
- Si `title` presente: se trimma; si queda vacío → `ErrInvalidTodoInput`
- Parcial update (solo campos enviados)

---

### 9. Eliminar tarea

```
DELETE /todos/:id
```

| Campo       | Detalle                                              |
|-------------|------------------------------------------------------|
| Auth        | No                                                   |
| URL param   | `id` — string                                        |

**Responses:**

| Status | Body                                              | Condición                          |
|--------|---------------------------------------------------|------------------------------------|
| 200    | `{"message": "tarea eliminada"}`                  | Eliminación exitosa                |
| 400    | `{"error": "id invalido"}`                        | ID no parseable                    |
| 404    | `{"error": "tarea no encontrada"}`                | ID no existe                       |
| 500    | `{"error": "error al eliminar tarea"}`            | Error interno                      |

---

### 10. Limpiar tareas

```
DELETE /todos?email={email}
```

| Campo       | Detalle                                              |
|-------------|------------------------------------------------------|
| Auth        | No                                                   |
| Query param | `email` (opcional) — filtra qué tareas eliminar      |

**Responses:**

| Status | Body                                              | Condición       |
|--------|---------------------------------------------------|-----------------|
| 200    | `{"message": "tareas eliminadas"}`                | OK              |
| 500    | `{"error": "error al limpiar tareas"}`            | Error interno   |

**Lógica de negocio:**
- Si `email` presente: normalizar y eliminar solo las de ese usuario
- Si `email` vacío: eliminar todas

---

## Modelos de datos

### User (almacenamiento)

| Campo    | Tipo   | Notas                        |
|----------|--------|------------------------------|
| email    | string | Normalizado (lower + trim), unique |
| password | string | Texto plano, trimmed         |

### PublicUser (respuesta API)

| Campo | Tipo   |
|-------|--------|
| email | string |

### Todo (almacenamiento)

| Campo     | Tipo              | Notas                    |
|-----------|-------------------|--------------------------|
| id        | ObjectID (Mongo)  | Auto-generado            |
| email     | string            | Normalizado              |
| title     | string            | Trimmed                  |
| completed | bool              | Default: false           |
| createdAt | datetime          | Set al crear             |

### TodoResponse (respuesta API)

| Campo     | Tipo     | Notas                        |
|-----------|----------|------------------------------|
| id        | string   | Hex del ObjectID             |
| email     | string   |                              |
| title     | string   |                              |
| completed | bool     |                              |
| createdAt | datetime | ISO 8601 format              |

---

## Variables de entorno

| Variable       | Default                      | Descripción                       |
|----------------|------------------------------|-----------------------------------|
| `PORT`         | `8080`                       | Puerto del servidor               |
| `MONGO_URI`    | `mongodb://localhost:27017`  | URI de conexión MongoDB           |
| `MONGO_DB`     | `hotelapp`                   | Nombre de la base de datos        |
| `FRONT_ORIGINS`| (vacío)                      | Origins CORS adicionales (comma-separated) |

---

## Convenciones CORS

- Métodos: GET, POST, PUT, DELETE, OPTIONS
- Headers permitidos: Origin, Content-Type, Authorization
- Headers expuestos: Content-Length
- Credentials: true
- Max Age: 12 horas
- Orígenes por defecto: `http://localhost:3000`, `http://localhost:5173`, `http://127.0.0.1:3000`, `http://127.0.0.1:5173`
- Orígenes adicionales: desde `FRONT_ORIGINS` env var (comma-separated)
