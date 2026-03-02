# Gestor de Transacciones

Aplicación web académica para la gestión de transacciones financieras construida con **Flask** (Python). Permite registrar usuarios, autenticarlos mediante **JWT**, y realizar operaciones de depósito, retiro y transferencia entre usuarios con un sistema de comisiones configurable. Incluye un frontend con dashboard interactivo y un sistema completo de auditoría.

---

## Tabla de contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Base de datos](#base-de-datos)
- [Autenticación JWT](#autenticación-jwt)
- [Endpoints de la API](#endpoints-de-la-api)
- [Sistema de comisiones](#sistema-de-comisiones)
- [Auditoría y logs](#auditoría-y-logs)
- [Frontend](#frontend)

---

## Características

- Registro e inicio de sesión de usuarios con contraseñas hasheadas (bcrypt).
- Autenticación basada en tokens JWT (access token + refresh token).
- Operaciones financieras: depósito, retiro y transferencia entre usuarios.
- Sistema de comisiones configurable por tipo de transacción.
- Validación de esquemas con Marshmallow.
- Registro de auditoría completo: se registran tanto las transacciones exitosas como las fallidas.
- Logging a consola y archivo (`app.log`).
- Manejo centralizado de excepciones de dominio.
- Frontend con HTML, JavaScript puro y TailwindCSS.
- Moneda: COP (Peso Colombiano).

---

## Tecnologías

| Componente       | Tecnología                |
|------------------|---------------------------|
| Backend          | Flask 3.1.0               |
| ORM              | Flask-SQLAlchemy 3.1.0    |
| Autenticación    | Flask-JWT-Extended 4.7.0  |
| CORS             | Flask-CORS 6.0.2          |
| Hashing          | bcrypt 5.0.0              |
| Validación       | Marshmallow 4.2.2         |
| Variables de env | python-dotenv 1.2.2       |
| Base de datos    | SQLite (archivo local)    |
| Frontend         | HTML + JS + TailwindCSS   |

---

## Arquitectura del proyecto

El proyecto sigue una arquitectura por capas con separación de responsabilidades:

```
transaction-manager/
├── run.py                  # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── .env                    # Variables de entorno (crear manualmente)
├── app.log                 # Archivo de logs generado automáticamente
├── instance/
│   └── app.db              # Base de datos SQLite (generada automáticamente)
├── app/
│   ├── __init__.py         # Factory de la app Flask y manejo de errores
│   ├── config.py           # Configuración y comisiones
│   ├── extensions.py       # Instancias de SQLAlchemy y JWT
│   ├── models/             # Modelos de base de datos (User, Transaction, AuditLog)
│   ├── repositories/       # Capa de acceso a datos
│   ├── services/           # Lógica de negocio
│   ├── routes/             # Endpoints de la API (Blueprints)
│   ├── schemas/            # Esquemas de validación (Marshmallow)
│   ├── contracts/          # DTOs / objetos de transferencia de datos
│   ├── common/
│   │   ├── decorators.py   # Decoradores (validación de esquemas)
│   │   ├── security.py     # Utilidades de seguridad
│   │   └── exceptions/     # Excepciones de dominio personalizadas
│   ├── utils/              # Utilidades (response factory)
│   ├── templates/          # Plantillas HTML (index, login, dashboard)
│   └── static/             # Archivos estáticos (CSS, JS)
```

---

## Requisitos previos

- **Python 3.10+** instalado en el sistema.
- **pip** (gestor de paquetes de Python).

---

## Instalación y ejecución

1. **Clonar el repositorio:**

   ```bash
   git clone <url-del-repositorio>
   cd transaction-manager
   ```

2. **Crear un entorno virtual (recomendado):**

   ```bash
   python -m venv venv

   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**

   Crear un archivo `.env` en la raíz del proyecto (ver sección [Variables de entorno](#variables-de-entorno)).

5. **Ejecutar la aplicación:**

   ```bash
   python run.py
   ```

   La aplicación estará disponible en `http://127.0.0.1:5000`.

6. **Ejecutar tests (opcional):**

   ```bash
   python test.py
   ```

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables. Todas tienen valores por defecto, por lo que el archivo es opcional para entornos de desarrollo:

```env
# URI de la base de datos (por defecto: SQLite local)
SQLALCHEMY_DATABASE_URI=sqlite:///app.db

# Clave secreta de la aplicación Flask
SECRET_KEY=tu-clave-secreta

# Clave secreta para firmar tokens JWT
JWT_SECRET_KEY=tu-clave-jwt-secreta

# Duración del access token en horas (por defecto: 1)
JWT_ACCESS_TOKEN_EXPIRES_HOURS=1

# Duración del refresh token en días (por defecto: 30)
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30
```

> **Nota:** En un entorno de producción, es fundamental cambiar las claves secretas por valores seguros y únicos.

---

## Base de datos

La aplicación utiliza **SQLite** como motor de base de datos. Dado el carácter académico del proyecto, la base de datos se almacena como un **archivo local** (`instance/app.db`) que se genera automáticamente al iniciar la aplicación por primera vez.

No es necesario instalar ni configurar ningún servidor de base de datos externo. Al ejecutar `python run.py`, Flask-SQLAlchemy crea todas las tablas automáticamente mediante `db.create_all()`.

### Modelos principales

| Modelo          | Descripción                                                  |
|-----------------|--------------------------------------------------------------|
| **User**        | Usuario con username, email, contraseña hasheada y saldo.    |
| **Transaction** | Registro de transacción con monto, comisión, tipo y estado.  |
| **AuditLog**    | Registro de auditoría con acción, usuario, IP y detalles.    |

### Identificadores

Todos los modelos utilizan **UUID v4** como clave primaria, garantizando identificadores únicos y no predecibles.

---

## Autenticación JWT

La autenticación se implementa mediante **JSON Web Tokens (JWT)** usando la extensión `Flask-JWT-Extended`.

### Flujo de autenticación

1. El usuario se registra en `/auth/register` proporcionando username, email y contraseña.
2. La contraseña se hashea con **bcrypt** antes de almacenarse.
3. El usuario inicia sesión en `/auth/login` con email y contraseña.
4. Al autenticarse correctamente, el servidor retorna un **access token** y un **refresh token**.
5. El access token se envía en el header `Authorization: Bearer <token>` en cada petición protegida.
6. Cuando el access token expira, se puede renovar usando el refresh token en `/auth/refresh`.

### Manejo de errores JWT

La aplicación maneja de forma centralizada los siguientes escenarios:

- **Token expirado:** responde con `401` y mensaje descriptivo.
- **Token inválido:** responde con `401`.
- **Token ausente:** responde con `401`.
- **Token revocado:** responde con `401`.

---

## Endpoints de la API

### Autenticación (`/auth`)

| Método | Ruta             | Descripción                        | Autenticación |
|--------|------------------|------------------------------------|---------------|
| POST   | `/auth/register` | Registrar un nuevo usuario         | No            |
| POST   | `/auth/login`    | Iniciar sesión                     | No            |
| POST   | `/auth/refresh`  | Renovar access token               | Refresh Token |

### Usuarios (`/users`)

| Método | Ruta        | Descripción                            | Autenticación |
|--------|-------------|----------------------------------------|---------------|
| GET    | `/users/me` | Obtener información del usuario actual | JWT           |

### Transacciones (`/transactions`)

| Método | Ruta                       | Descripción                      | Autenticación |
|--------|----------------------------|----------------------------------|---------------|
| POST   | `/transactions/deposit`    | Realizar un depósito             | JWT           |
| POST   | `/transactions/withdrawal` | Realizar un retiro               | JWT           |
| POST   | `/transactions/transfer`   | Realizar una transferencia       | JWT           |
| GET    | `/transactions/`           | Listar transacciones del usuario | JWT           |

### Auditoría (`/audit`)

| Método | Ruta             | Descripción                           | Autenticación |
|--------|------------------|---------------------------------------|---------------|
| GET    | `/audit/my-logs` | Obtener logs de auditoría del usuario | JWT           |

### Páginas web

| Método | Ruta          | Descripción           |
|--------|---------------|-----------------------|
| GET    | `/`           | Página de inicio      |
| GET    | `/login`      | Página de login       |
| GET    | `/dashboard`  | Dashboard del usuario |

---

## Sistema de comisiones

Cada tipo de transacción tiene una tasa de comisión configurable:

| Tipo de transacción | Comisión |
|---------------------|----------|
| Depósito            | 0%       |
| Retiro              | 2%       |
| Transferencia       | 3%       |

- En **depósitos**, el usuario recibe el monto neto (monto - comisión).
- En **retiros**, se deduce el monto + comisión del saldo del usuario.
- En **transferencias**, el remitente paga el monto + comisión, y el destinatario recibe el monto completo.

Las tasas de comisión se configuran en `app/config.py` en el diccionario `COMMISSION_RATES`.

---

## Auditoría y logs

El sistema implementa un mecanismo de auditoría completo para garantizar la trazabilidad de todas las operaciones.

### Registro de auditoría en base de datos

Cada acción relevante genera un registro en la tabla `audit_logs` que incluye:

- **Acción realizada** (tipo de evento).
- **ID del usuario** que ejecutó la acción.
- **Dirección IP** desde donde se realizó.
- **Detalles** en formato JSON (montos, IDs de transacción, motivos de fallo, etc.).
- **Fecha y hora** del evento.

### Acciones auditadas

| Acción               | Descripción                                  |
|----------------------|----------------------------------------------|
| `USER_REGISTERED`    | Usuario registrado exitosamente              |
| `USER_LOGIN`         | Inicio de sesión exitoso                     |
| `USER_LOGIN_FAILED`  | Intento de inicio de sesión fallido          |
| `TOKEN_REFRESHED`    | Token de acceso renovado                     |
| `USER_UPDATED`       | Datos del usuario actualizados               |
| `USER_DELETED`       | Usuario eliminado                            |
| `DEPOSIT_CREATED`    | Depósito realizado exitosamente              |
| `DEPOSIT_FAILED`     | Depósito fallido                             |
| `WITHDRAWAL_CREATED` | Retiro realizado exitosamente                |
| `WITHDRAWAL_FAILED`  | Retiro fallido (fondos insuficientes)        |
| `TRANSFER_CREATED`   | Transferencia realizada exitosamente         |
| `TRANSFER_FAILED`    | Transferencia fallida (fondos insuficientes) |

> **Importante:** Las transacciones rechazadas (por fondos insuficientes, por ejemplo) también se registran en la base de datos tanto como transacción con estado `FAILED` como en el log de auditoría. Esto permite tener un historial completo para fines de auditoría, incluyendo intentos fallidos con el motivo del rechazo.

### Logging a archivo

Además de la auditoría en base de datos, la aplicación escribe logs en:

- **Consola** (`stdout`): nivel DEBUG, para desarrollo.
- **Archivo** (`app.log`): nivel INFO, para registro persistente.

Los logs incluyen excepciones de dominio, errores HTTP y errores no controlados con stack trace completo.

---

## Frontend

El frontend está construido con **HTML puro**, **JavaScript vanilla** y **TailwindCSS** (vía CDN), minimizando la dependencia de templates del servidor. Flask solo sirve las páginas HTML base; toda la lógica de interacción se maneja desde el cliente con llamadas a la API REST.

### Páginas

- **Inicio (`/`):** Página de bienvenida con acceso a registro e inicio de sesión.
- **Login (`/login`):** Formulario de inicio de sesión y registro de usuario.
- **Dashboard (`/dashboard`):** Panel principal con:
  - Información del usuario y saldo actual.
  - Historial de transaccione.
  - Formularios para depósito, retiro y transferencia.

---

## Licencia

Proyecto académico — uso educativo.

