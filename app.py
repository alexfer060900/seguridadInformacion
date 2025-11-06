from flask import Flask, request, jsonify, session
from datetime import datetime, timedelta
from models import *
import random
import string
import os
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autenticacion.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Crear tablas al iniciar
with app.app_context():
    db.create_all()


def generar_usuario(nombre, apellido):
    """Generar usuario automáticamente"""
    base = (nombre[:2] + apellido[:4]).lower()
    numero = random.randint(100, 999)
    return f"{base}{numero}"


def generar_codigo(longitud=6):
    """Generar código de verificación"""
    return ''.join(random.choices(string.digits, k=longitud))


def generar_password():
    """Generar contraseña aleatoria"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(caracteres, k=12))


def obtener_ip():
    """Obtener IP del cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr or '127.0.0.1'


# ==================== RS1: REGISTRO DE USUARIOS ====================
@app.route('/api/registro', methods=['POST'])
def registro_usuario():
    """
    RS1: Registro de nuevos usuarios con validación
    Body JSON: {"nombre": "", "apellido": "", "mail": "", "telefono": ""}
    """
    try:
        data = request.json
        
                # Validación básica
        required = ['nombre', 'apellido', 'mail', 'telefono']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo {field} es obligatorio'}), 400
        
        if not isinstance(data['telefono'], (int, str)) or not str(data['telefono']).isdigit():
            return jsonify({'error': 'Teléfono debe ser numérico'}), 400
        
        # Validar formato email básico
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['mail']):
            return jsonify({'error': 'Email inválido'}), 400
        # Validar que no exista el correo
        if Cliente.query.filter_by(mail=data['mail']).first():
            return jsonify({'error': 'El correo ya está registrado'}), 400
        
        # Crear cliente
        cliente = Cliente(
            nombre=data['nombre'],
            apellido=data['apellido'],
            mail=data['mail'],
            telefono=int(data['telefono'])
        )
        db.session.add(cliente)
        db.session.flush()
        
        # Generar usuario y contraseña automáticamente
        nuevo_usuario = generar_usuario(data['nombre'], data['apellido'])
        nueva_password = generar_password()
        
        # Crear usuario
        usuario = Usuario(
            usuario=nuevo_usuario,
            idCli=cliente.idCli,
            estado='pendiente'
        )
        usuario.set_password(nueva_password)
        db.session.add(usuario)
        db.session.flush()
        
        # Generar código de validación por email
        codigo = generar_codigo()
        validacion = ValidarCuenta(
            codigo=codigo,
            tipo='email',
            estado='pendiente',
            idUser=usuario.idUser
        )
        db.session.add(validacion)
        
        # Registrar en auditoría
        auditoria = Auditoria(
        usuario='sistema',
        accion=datetime.utcnow(),  # Esto es redundante si fechaHora es DateTime
        fechaHora=datetime.utcnow()  # Cambia a DateTime
        )

        db.session.add(auditoria)
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': nuevo_usuario,
            'password': nueva_password,
            'codigo_validacion': codigo,
            'nota': 'Guarda estas credenciales. El código expira en 24 horas.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/validar-cuenta', methods=['POST'])
def validar_cuenta():
    """
    RS1: Validar cuenta con código enviado por email
    Body JSON: {"usuario": "", "codigo": ""}
    """
    try:
        data = request.json
        
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        validacion = ValidarCuenta.query.filter_by(
            idUser=usuario.idUser,
            codigo=data['codigo'],
            estado='pendiente'
        ).first()
        
        if not validacion:
            return jsonify({'error': 'Código inválido o ya usado'}), 400
        
        # Verificar expiración (24 horas)
        if (datetime.utcnow().date() - validacion.fechaEnvio).days > 1:
            validacion.estado = 'expirado'
            db.session.commit()
            return jsonify({'error': 'Código expirado'}), 400
        
        # Activar cuenta
        validacion.fechaConfirmacion = datetime.utcnow().date()
        validacion.estado = 'confirmado'
        usuario.estado = 'activo'
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Cuenta activada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== RS2: LOGIN Y SEGUNDO FACTOR ====================
@app.route('/api/login', methods=['POST'])
def login():
    """
    RS2 y RS6: Login con control de intentos
    Body JSON: {"usuario": "", "password": ""}
    """
    try:
        data = request.json
        ip = obtener_ip()
        
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
        
        # Validar usuario existe
        if not usuario:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # RS6: Verificar si está bloqueado (4 intentos)
        if usuario.intentosFallidos >= 4:
            registrar_acceso(usuario.idUser, data['usuario'], ip, 'bloqueado')
            return jsonify({
                'error': 'Usuario bloqueado por múltiples intentos fallidos',
                'nota': 'Contacte al administrador para desbloquear'
            }), 403
        
        # Verificar estado de la cuenta
        if usuario.estado != 'activo':
            return jsonify({'error': f'Cuenta {usuario.estado}'}), 403
        
        # Verificar contraseña
        if not usuario.check_password(data['password']):
            usuario.intentosFallidos += 1
            db.session.commit()
            registrar_acceso(usuario.idUser, data['usuario'], ip, 'fallido')
            
            intentos_restantes = 4 - usuario.intentosFallidos
            return jsonify({
                'error': 'Credenciales inválidas',
                'intentos_restantes': intentos_restantes
            }), 401
        
        # RS5: Verificar si ya tiene sesión activa
        sesion_activa = Sesion.query.filter_by(
            idUser=usuario.idUser,
            estado='activa'
        ).first()
        
        if sesion_activa:
            return jsonify({
                'error': 'Ya existe una sesión activa para este usuario',
                'sesion_ip': sesion_activa.direccionIp
            }), 409
        
        # Login exitoso - resetear intentos
        usuario.intentosFallidos = 0
        db.session.commit()
        
        # Generar código para segundo factor
        codigo_2fa = generar_codigo()
        codigo = Codigo(
            codigo=int(codigo_2fa),
            canal='email',
            idUser=usuario.idUser
        )
        db.session.add(codigo)
        db.session.commit()
        
        registrar_acceso(usuario.idUser, data['usuario'], ip, 'login_exitoso')
        
        return jsonify({
            'mensaje': 'Login exitoso. Ingrese código de segundo factor',
            'codigo_2fa': codigo_2fa,
            'usuario_id': usuario.idUser
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/verificar-segundo-factor', methods=['POST'])
def verificar_segundo_factor():
    """
    RS2: Verificar segundo factor de autenticación
    Body JSON: {"usuario_id": 0, "codigo": ""}
    """
    try:
        data = request.json
        ip = obtener_ip()
        
        codigo_db = Codigo.query.filter_by(
            idUser=data['usuario_id'],
            codigo=int(data['codigo'])
        ).first()
        
        if not codigo_db:
            return jsonify({'error': 'Código inválido'}), 401
        
        usuario = Usuario.query.get(data['usuario_id'])
        
        # RS7: Crear sesión
        sesion = Sesion(
            usuario=usuario.usuario,
            idUser=usuario.idUser,
            direccionIp=ip,
            estado='activa'
        )
        db.session.add(sesion)
        
        # Eliminar código usado
        db.session.delete(codigo_db)
        
        db.session.commit()
        
        registrar_acceso(usuario.idUser, usuario.usuario, ip, 'acceso_completo')
        
        return jsonify({
            'mensaje': 'Autenticación completa',
            'sesion_id': sesion.idSesion,
            'usuario': usuario.usuario
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== RS3: MONITOREO ====================
def registrar_acceso(id_user, usuario, ip, resultado, tipo_acceso=None):
    """Registrar todos los accesos al sistema"""
    registro = RegistroAcceso(
        usuario=usuario,
        ipAcceso=ip,
        resultado=resultado,
        tipoAcceso=tipo_acceso,
        idUser=id_user
    )
    db.session.add(registro)
    db.session.commit()


@app.route('/api/auditoria', methods=['GET'])
def obtener_auditoria():
    """RS3: Obtener registros de auditoría"""
    registros = RegistroAcceso.query.order_by(RegistroAcceso.fechaHora.desc()).limit(100).all()
    
    resultado = [{
        'id': r.idRegistro,
        'usuario': r.usuario,
        'fecha': r.fechaHora.strftime('%Y-%m-%d %H:%M:%S'),
        'ip': r.ipAcceso,
        'resultado': r.resultado,
        'tipo': r.tipoAcceso
    } for r in registros]
    
    return jsonify(resultado), 200


# ==================== RS4: RECUPERAR CONTRASEÑA ====================
@app.route('/api/recuperar-cuenta', methods=['POST'])
def recuperar_cuenta():
    """
    RS4: Solicitar recuperación de cuenta por email
    Body JSON: {"mail": ""}
    """
    try:
        data = request.json
        
        cliente = Cliente.query.filter_by(mail=data['mail']).first()
        if not cliente:
            # Por seguridad, no revelar si el email existe
            return jsonify({'mensaje': 'Si el correo existe, recibirás un código'}), 200
        
        usuario = cliente.usuario_obj
        
        # Generar código de recuperación
        codigo = generar_codigo()
        fecha_exp = datetime.utcnow().date() + timedelta(days=1)
        
        recuperacion = RecuperarCuenta(
            codigo=codigo,
            usuario=usuario.usuario,
            fechaExpiracion=fecha_exp,
            idUser=usuario.idUser
        )
        db.session.add(recuperacion)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Código de recuperación generado',
            'codigo': codigo,
            'usuario': usuario.usuario,
            'expira': fecha_exp.strftime('%Y-%m-%d')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/restablecer-password', methods=['POST'])
def restablecer_password():
    """
    RS4: Restablecer contraseña con código
    Body JSON: {"usuario": "", "codigo": "", "nueva_password": ""}
    """
    try:
        data = request.json
        
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        recuperacion = RecuperarCuenta.query.filter_by(
            idUser=usuario.idUser,
            codigo=data['codigo'],
            estado='pendiente'
        ).first()
        
        if not recuperacion:
            return jsonify({'error': 'Código inválido o ya usado'}), 400
        
        # Verificar expiración
        if datetime.utcnow().date() > recuperacion.fechaExpiracion:
            recuperacion.estado = 'expirado'
            db.session.commit()
            return jsonify({'error': 'Código expirado'}), 400
        
        # Cambiar contraseña
        usuario.set_password(data['nueva_password'])
        recuperacion.estado = 'usado'
        usuario.intentosFallidos = 0  # Resetear intentos
        
        db.session.commit()
        
        return jsonify({'mensaje': 'Contraseña restablecida exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== RS5: GESTIÓN DE USUARIOS ====================
@app.route('/api/usuario/<int:id_user>/estado', methods=['PUT'])
def cambiar_estado_usuario(id_user):
    """
    RS5: Dar de baja temporal o activar usuario
    Body JSON: {"estado": "activo" | "inactivo"}
    """
    try:
        data = request.json
        usuario = Usuario.query.get(id_user)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Cerrar sesiones activas si se desactiva
        if data['estado'] == 'inactivo':
            sesiones = Sesion.query.filter_by(idUser=id_user, estado='activa').all()
            for sesion in sesiones:
                sesion.estado = 'cerrada'
                sesion.fechaFin = datetime.utcnow()
        
        usuario.estado = data['estado']
        db.session.commit()
        
        return jsonify({
            'mensaje': f'Usuario {data["estado"]}',
            'usuario': usuario.usuario
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/cerrar-sesion', methods=['POST'])
def cerrar_sesion():
    """
    RS5 y RS7: Cerrar sesión activa
    Body JSON: {"sesion_id": 0}
    """
    try:
        data = request.json
        sesion = Sesion.query.get(data['sesion_id'])
        
        if not sesion:
            return jsonify({'error': 'Sesión no encontrada'}), 404
        
        sesion.estado = 'cerrada'
        sesion.fechaFin = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'mensaje': 'Sesión cerrada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== RS6: DESBLOQUEO DE USUARIO ====================
@app.route('/api/desbloquear-usuario', methods=['POST'])
def desbloquear_usuario():
    """
    RS6: Desbloquear usuario después de 4 intentos fallidos
    Body JSON: {"usuario": ""}
    """
    try:
        data = request.json
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        usuario.intentosFallidos = 0
        
        # Registrar desbloqueo
        auditoria = Auditoria(
            usuario='admin',
            accion=datetime.utcnow(),  # Esto es redundante si fechaHora es DateTime
            fechaHora=datetime.utcnow() 
        )
        db.session.add(auditoria)
        db.session.commit()
        
        return jsonify({'mensaje': 'Usuario desbloqueado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE CONSULTA ====================
@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """Listar todos los usuarios"""
    usuarios = Usuario.query.all()
    resultado = [{
        'id': u.idUser,
        'usuario': u.usuario,
        'estado': u.estado,
        'intentos_fallidos': u.intentosFallidos,
        'fecha_creacion': u.fechaCrea.strftime('%Y-%m-%d')
    } for u in usuarios]
    
    return jsonify(resultado), 200


@app.route('/api/sesiones-activas', methods=['GET'])
def listar_sesiones_activas():
    """RS7: Listar sesiones activas"""
    sesiones = Sesion.query.filter_by(estado='activa').all()
    resultado = [{
        'id': s.idSesion,
        'usuario': s.usuario,
        'ip': s.direccionIp,
        'inicio': s.fechaInicio.strftime('%Y-%m-%d %H:%M:%S')
    } for s in sesiones]
    
    return jsonify(resultado), 200


@app.route('/')
def home():
    return render_template('test_interface.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)