# Sistema de Autenticación - Implementación Completa

Sistema de autenticación con validación de cuenta, segundo factor, recuperación de contraseña y auditoría completa.

##Requisitos Implementados

- **RS1**: Registro con validación de correo/celular
- **RS2**: Segundo factor de autenticación
- **RS3**: Monitoreo y auditoría completa
- **RS4**: Recuperación de usuario/contraseña
- **RS5**: Control de sesiones únicas y estados de usuario
- **RS6**: Control de intentos y bloqueo/desbloqueo
- **RS7**: Gestión completa de sesiones

## Instalación Paso a Paso

### Paso 1: Descargar el Proyecto

1. Abre el CMD o Terminal
2. Navega a donde quieres guardar el proyecto:
   ```bash
   cd Documentos
   ```

3. Clona el repositorio (después de subirlo):
   ```bash
   git clone https://github.com/TU_USUARIO/sistema-autenticacion.git
   cd sistema-autenticacion
   ```

### Paso 2: Crear Entorno Virtual

#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### En Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Iniciar el Servidor

```bash
python app.py
```

Deberías ver algo como:
```
* Running on http://127.0.0.1:5000
```

### Paso 5: Ejecutar Pruebas

**Abre una NUEVA terminal** (sin cerrar la anterior) y ejecuta:

```bash
cd sistema-autenticacion
# Activar entorno virtual nuevamente
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Mac/Linux

# Ejecutar pruebas
python test_api.py
```

## Estructura del Proyecto

```
sistema-autenticacion/
│
├── app.py                 # Aplicación principal Flask
├── models.py             # Modelos de base de datos
├── test_api.py           # Script de pruebas
├── requirements.txt      # Dependencias Python
├── README.md            # Este archivo
├── .gitignore           # Archivos a ignorar en Git
│
├── autenticacion.db     # Base de datos SQLite (se crea automáticamente)
└── instance/            # Carpeta de configuración Flask
```

## Uso de la API


## Probar con Postman o Thunder Client

### Opción 1: Postman
1. Descarga Postman: https://www.postman.com/downloads/
2. Importa la colección desde File > Import
3. Ejecuta las peticiones en orden

### Opción 2: Thunder Client (VS Code)
1. Instala la extensión Thunder Client en VS Code
2. Crea nuevas peticiones con los ejemplos de arriba
3. Guarda en una colección

### Opción 3: cURL (Terminal)
```bash
# Registro
curl -X POST http://localhost:5000/api/registro \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan","apellido":"Pérez","mail":"juan@example.com","telefono":"593987654321"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"juperez123","password":"aB3$dE6fG8hJ"}'
```

## Para el Documento PDF

Toma capturas de pantalla de:

1. **Instalación**: Terminal mostrando `pip install -r requirements.txt`
2. **Servidor iniciado**: Terminal mostrando Flask corriendo
3. **Prueba de registro**: Respuesta exitosa del endpoint `/api/registro`
4. **Validación de cuenta**: Respuesta de `/api/validar-cuenta`
5. **Login exitoso**: Respuesta con código 2FA
6. **Segundo factor**: Verificación exitosa
7. **Intentos fallidos**: Mostrando bloqueo después de 4 intentos
8. **Desbloqueo**: Usuario desbloqueado
9. **Recuperación**: Código de recuperación generado
10. **Auditoría**: Lista de accesos registrados
11. **Sesiones activas**: Lista de sesiones
12. **Base de datos**: Captura de `autenticacion.db` en un visor SQLite

## Visualizar la Base de Datos

### Opción 1: DB Browser for SQLite
1. Descarga: https://sqlitebrowser.org/
2. Abre el archivo `autenticacion.db`
3. Navega por las tablas

### Opción 2: VS Code Extension
1. Instala "SQLite Viewer" en VS Code
2. Haz clic en `autenticacion.db`

## Solución de Problemas

### Error: "No module named flask"
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
El puerto 5000 está ocupado. Cambia el puerto en `app.py`:
```python
app.run(debug=True, port=5001)  # Cambia a otro puerto
```

### Error: "Permission denied"
En Mac/Linux, usa `python3` en lugar de `python`

### La base de datos no se crea
Asegúrate de estar en el directorio correcto y que Flask tenga permisos de escritura

## 📤 Subir a GitHub

### Primera vez:
```bash
git init
git add .
git commit -m "Implementación completa del sistema de autenticación"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/sistema-autenticacion.git
git push -u origin main
```

### Actualizaciones posteriores:
```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

## Notas Importantes

- La contraseña se genera automáticamente y se devuelve una sola vez
- Los códigos de validación expiran en 24 horas
- Máximo 4 intentos fallidos antes de bloqueo
- No se permiten sesiones simultáneas del mismo usuario
- Todos los accesos quedan registrados en auditoría

## Tecnologías Utilizadas

- **Backend**: Python 3.11, Flask 3.0
- **Base de Datos**: SQLite
- **ORM**: SQLAlchemy
- **Seguridad**: Werkzeug (hashing de contraseñas)

## Licencia

Este proyecto fue desarrollado con fines académicos."# seguridadInformacion" 
