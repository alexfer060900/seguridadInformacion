"""
Script para probar todos los endpoints del sistema
Ejecutar después de iniciar app.py
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def imprimir_respuesta(titulo, response):
    """Imprimir respuesta formateada"""
    print(f"\n{'='*60}")
    print(f"🔍 {titulo}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Respuesta: {response.text}")
    print(f"{'='*60}\n")


def test_rs1_registro():
    """RS1: Probar registro de usuario"""
    print("\n🧪 PROBANDO RS1: REGISTRO DE USUARIOS")
    
    data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "mail": "juan.perez@example.com",
        "telefono": "593987654321"
    }
    
    response = requests.post(f'{BASE_URL}/registro', json=data)
    imprimir_respuesta("RS1 - Registro de Usuario", response)
    
    if response.status_code == 201:
        return response.json()
    return None


def test_rs1_validacion(usuario, codigo):
    """RS1: Probar validación de cuenta"""
    print("\n🧪 PROBANDO RS1: VALIDACIÓN DE CUENTA")
    
    data = {
        "usuario": usuario,
        "codigo": codigo
    }
    
    response = requests.post(f'{BASE_URL}/validar-cuenta', json=data)
    imprimir_respuesta("RS1 - Validación de Cuenta", response)


def test_rs6_intentos_fallidos(usuario):
    """RS6: Probar bloqueo por intentos fallidos"""
    print("\n🧪 PROBANDO RS6: CONTROL DE INTENTOS FALLIDOS")
    
    for i in range(5):
        data = {
            "usuario": usuario,
            "password": "password_incorrecta"
        }
        response = requests.post(f'{BASE_URL}/login', json=data)
        imprimir_respuesta(f"RS6 - Intento {i+1} con contraseña incorrecta", response)
        time.sleep(1)


def test_rs6_desbloqueo(usuario):
    """RS6: Probar desbloqueo de usuario"""
    print("\n🧪 PROBANDO RS6: DESBLOQUEO DE USUARIO")
    
    data = {"usuario": usuario}
    response = requests.post(f'{BASE_URL}/desbloquear-usuario', json=data)
    imprimir_respuesta("RS6 - Desbloqueo de Usuario", response)


def test_rs2_login(usuario, password):
    """RS2: Probar login y segundo factor"""
    print("\n🧪 PROBANDO RS2: LOGIN Y SEGUNDO FACTOR")
    
    data = {
        "usuario": usuario,
        "password": password
    }
    
    response = requests.post(f'{BASE_URL}/login', json=data)
    imprimir_respuesta("RS2 - Login (Primera Fase)", response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_rs2_segundo_factor(usuario_id, codigo):
    """RS2: Probar segundo factor de autenticación"""
    print("\n🧪 PROBANDO RS2: VERIFICACIÓN SEGUNDO FACTOR")
    
    data = {
        "usuario_id": usuario_id,
        "codigo": codigo
    }
    
    response = requests.post(f'{BASE_URL}/verificar-segundo-factor', json=data)
    imprimir_respuesta("RS2 - Segundo Factor", response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_rs5_sesion_duplicada(usuario, password):
    """RS5: Probar restricción de sesión única"""
    print("\n🧪 PROBANDO RS5: NO PERMITIR SESIONES DUPLICADAS")
    
    # Intentar login nuevamente con sesión activa
    data = {
        "usuario": usuario,
        "password": password
    }
    
    response = requests.post(f'{BASE_URL}/login', json=data)
    imprimir_respuesta("RS5 - Intento de Segunda Sesión Simultánea", response)


def test_rs7_cerrar_sesion(sesion_id):
    """RS7: Probar cierre de sesión"""
    print("\n🧪 PROBANDO RS7: CERRAR SESIÓN")
    
    data = {"sesion_id": sesion_id}
    response = requests.post(f'{BASE_URL}/cerrar-sesion', json=data)
    imprimir_respuesta("RS7 - Cerrar Sesión", response)


def test_rs4_recuperar_cuenta(mail):
    """RS4: Probar recuperación de cuenta"""
    print("\n🧪 PROBANDO RS4: RECUPERACIÓN DE CUENTA")
    
    data = {"mail": mail}
    response = requests.post(f'{BASE_URL}/recuperar-cuenta', json=data)
    imprimir_respuesta("RS4 - Solicitar Recuperación", response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_rs4_restablecer_password(usuario, codigo):
    """RS4: Probar restablecimiento de contraseña"""
    print("\n🧪 PROBANDO RS4: RESTABLECER CONTRASEÑA")
    
    data = {
        "usuario": usuario,
        "codigo": codigo,
        "nueva_password": "NuevaPassword123!"
    }
    
    response = requests.post(f'{BASE_URL}/restablecer-password', json=data)
    imprimir_respuesta("RS4 - Restablecer Contraseña", response)


def test_rs5_cambiar_estado(id_user):
    """RS5: Probar baja temporal de usuario"""
    print("\n🧪 PROBANDO RS5: BAJA TEMPORAL DE USUARIO")
    
    # Desactivar
    data = {"estado": "inactivo"}
    response = requests.put(f'{BASE_URL}/usuario/{id_user}/estado', json=data)
    imprimir_respuesta("RS5 - Desactivar Usuario", response)
    
    time.sleep(1)
    
    # Reactivar
    data = {"estado": "activo"}
    response = requests.put(f'{BASE_URL}/usuario/{id_user}/estado', json=data)
    imprimir_respuesta("RS5 - Reactivar Usuario", response)


def test_rs3_auditoria():
    """RS3: Probar consulta de auditoría"""
    print("\n🧪 PROBANDO RS3: AUDITORÍA Y MONITOREO")
    
    response = requests.get(f'{BASE_URL}/auditoria')
    imprimir_respuesta("RS3 - Consultar Auditoría", response)


def test_consultas():
    """Probar endpoints de consulta"""
    print("\n🧪 PROBANDO CONSULTAS GENERALES")
    
    # Listar usuarios
    response = requests.get(f'{BASE_URL}/usuarios')
    imprimir_respuesta("Listar Usuarios", response)
    
    # Sesiones activas
    response = requests.get(f'{BASE_URL}/sesiones-activas')
    imprimir_respuesta("Sesiones Activas", response)


def ejecutar_todas_las_pruebas():
    """Ejecutar todas las pruebas en secuencia"""
    print("\n" + "="*60)
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("="*60)
    
    # RS1: Registro y validación
    registro = test_rs1_registro()
    if not registro:
        print("❌ Error en registro, deteniendo pruebas")
        return
    
    usuario = registro['usuario']
    password = registro['password']
    codigo_validacion = registro['codigo_validacion']
    
    input("\n⏸️  Presiona Enter para continuar con la validación...")
    test_rs1_validacion(usuario, codigo_validacion)
    
    # RS6: Intentos fallidos y bloqueo
    input("\n⏸️  Presiona Enter para probar intentos fallidos...")
    test_rs6_intentos_fallidos(usuario)
    
    input("\n⏸️  Presiona Enter para desbloquear usuario...")
    test_rs6_desbloqueo(usuario)
    
    # RS2: Login con segundo factor
    input("\n⏸️  Presiona Enter para hacer login...")
    login_result = test_rs2_login(usuario, password)
    
    if not login_result:
        print("❌ Error en login")
        return
    
    codigo_2fa = login_result['codigo_2fa']
    usuario_id = login_result['usuario_id']
    
    input("\n⏸️  Presiona Enter para verificar segundo factor...")
    sesion_result = test_rs2_segundo_factor(usuario_id, codigo_2fa)
    
    if not sesion_result:
        print("❌ Error en segundo factor")
        return
    
    sesion_id = sesion_result['sesion_id']
    
    # RS5: Intentar sesión duplicada
    input("\n⏸️  Presiona Enter para probar sesión duplicada...")
    test_rs5_sesion_duplicada(usuario, password)
    
    # RS7: Cerrar sesión
    input("\n⏸️  Presiona Enter para cerrar sesión...")
    test_rs7_cerrar_sesion(sesion_id)
    
    # RS4: Recuperación de cuenta
    input("\n⏸️  Presiona Enter para probar recuperación de cuenta...")
    recuperacion = test_rs4_recuperar_cuenta("juan.perez@example.com")
    
    if recuperacion:
        codigo_recuperacion = recuperacion['codigo']
        input("\n⏸️  Presiona Enter para restablecer contraseña...")
        test_rs4_restablecer_password(usuario, codigo_recuperacion)
    
    # RS5: Cambiar estado
    input("\n⏸️  Presiona Enter para probar cambio de estado...")
    test_rs5_cambiar_estado(usuario_id)
    
    # RS3: Auditoría
    input("\n⏸️  Presiona Enter para ver auditoría...")
    test_rs3_auditoria()
    
    # Consultas generales
    input("\n⏸️  Presiona Enter para ver consultas generales...")
    test_consultas()
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)


if __name__ == '__main__':
    try:
        ejecutar_todas_las_pruebas()
    except KeyboardInterrupt:
        print("\n\n❌ Pruebas interrumpidas por el usuario")
    except requests.exceptions.ConnectionError:
        print("\n\n❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que app.py esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {str(e)}")