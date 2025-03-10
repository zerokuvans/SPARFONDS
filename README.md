# Aplicación de Fondo de Ahorro

Esta es una aplicación web desarrollada con Flask para gestionar un fondo de ahorro.

## Características

- Sistema de autenticación basado en roles (Administrativo y Ahorrador)
- Panel de administración para gestionar usuarios y fondos
- Panel de ahorrador para ver saldos y realizar aportes
- Interfaz responsiva con Bootstrap
- Configuración externa segura mediante variables de entorno

## Requisitos

- Python 3.6+ (probado en Python 3.13)
- MySQL

## Instalación

1. Clona este repositorio:
```
git clone https://github.com/tu-usuario/fondo-ahorro.git
cd fondo-ahorro
```

2. Crea un entorno virtual e instala las dependencias:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configura la base de datos:
   - Crea una base de datos llamada "sparfonds" en MySQL
   - Copia el archivo `.env.example` a `.env` y edita los valores según tu configuración:
   ```
   cp .env.example .env
   ```
   - Edita las siguientes variables en el archivo `.env`:
   ```
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_HOST=localhost
   DB_NAME=sparfonds
   ```

4. Crea la tabla "usuarios" con los siguientes datos:
```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuarios_documento VARCHAR(150) NOT NULL UNIQUE,
    usuarios_password VARCHAR(150) NOT NULL,
    rol VARCHAR(50) NOT NULL
);

INSERT INTO usuarios (usuarios_documento, usuarios_password, rol) 
VALUES ('admin123', 'clave123', 'administrativo');

INSERT INTO usuarios (usuarios_documento, usuarios_password, rol) 
VALUES ('ahorrador123', 'clave123', 'ahorrador');
```

5. Ejecuta la aplicación:
```
python run.py
```

6. Abre un navegador y navega a http://localhost:5000

## Estructura del Proyecto

- `/app`: Contiene el código principal de la aplicación
  - `/templates`: Plantillas HTML
  - `/static`: Archivos estáticos (CSS, JS, imágenes)
  - `__init__.py`: Configuración de la aplicación
  - `routes.py`: Definición de rutas
  - `models.py`: Modelos de datos
- `config.py`: Configuración de la aplicación
- `.env`: Variables de entorno (no incluido en el control de versiones)
- `run.py`: Punto de entrada de la aplicación

## Entornos de Ejecución

La aplicación puede ejecutarse en diferentes entornos:

- **Desarrollo** (por defecto): `FLASK_ENV=development python run.py`
- **Producción**: `FLASK_ENV=production python run.py`

## Notas sobre la Base de Datos

La aplicación utiliza la tabla "usuarios" de la base de datos "sparfonds" con las siguientes columnas:
- id (clave primaria)
- usuarios_documento (identificador único de usuario)
- usuarios_password (contraseña del usuario)
- rol (rol del usuario: "administrativo" o "ahorrador")

## Solución de Problemas

Si encuentras el error "Access denied for user", debes verificar:
1. Que el usuario de MySQL que estás utilizando existe
2. Que la contraseña es correcta
3. Que el usuario tiene permisos para acceder a la base de datos "sparfonds"
4. Que los valores en el archivo .env son correctos 