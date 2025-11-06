from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Cliente(db.Model):
    """RS1: Registro de nuevos usuarios"""
    __tablename__ = 'cliente'
    
    idCli = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.BigInteger, nullable=False)
    
    # Relación con Usuario
    usuario_obj = db.relationship('Usuario', backref='cliente', uselist=False, cascade='all, delete-orphan')


class Usuario(db.Model):
    """RS1: Usuario y contraseña generados por el sistema"""
    __tablename__ = 'usuario'
    
    idUser = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fechaCrea = db.Column(db.Date, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, activo, inactivo
    intentosFallidos = db.Column(db.Integer, default=0)
    
    # Foreign Key
    idCli = db.Column(db.Integer, db.ForeignKey('cliente.idCli'), nullable=False)
    
    # Relaciones - back_populates ajustados
    validaciones = db.relationship('ValidarCuenta', back_populates='usuario_obj', cascade='all, delete-orphan')
    accesos = db.relationship('RegistroAcceso', back_populates='usuario_obj', cascade='all, delete-orphan')
    sesiones = db.relationship('Sesion', back_populates='usuario_obj', cascade='all, delete-orphan')
    recuperaciones = db.relationship('RecuperarCuenta', back_populates='usuario_obj', cascade='all, delete-orphan')

    def set_password(self, password):
        """Encriptar contraseña"""
        self.contrasena = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.contrasena, password)


class ValidarCuenta(db.Model):
    """RS1: Validación de correo electrónico o celular"""
    __tablename__ = 'validar_cuenta'
    
    idValidacion = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), nullable=False)
    fechaEnvio = db.Column(db.Date, default=datetime.utcnow)
    fechaConfirmacion = db.Column(db.Date, nullable=True)
    tipo = db.Column(db.String(20), nullable=False)  # email, sms
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmado, expirado
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)
    # Relación inversa
    usuario_obj = db.relationship('Usuario', back_populates='validaciones')

class SegundoFactor(db.Model):
    """RS2: Segundo factor de autenticación"""
    __tablename__ = 'segundo_factor'
    
    tipo = db.Column(db.Integer, primary_key=True)
    validoHasta = db.Column(db.Date, nullable=True)
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)


class Pregunta(db.Model):
    """RS2: Preguntas frecuentes para segundo factor"""
    __tablename__ = 'pregunta'
    
    pregunta = db.Column(db.String(255), primary_key=True)
    respuesta = db.Column(db.String(255), nullable=False)
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)


class Codigo(db.Model):
    """RS2: Códigos de verificación"""
    __tablename__ = 'codigo'
    
    codigo = db.Column(db.Integer, primary_key=True)
    canal = db.Column(db.String(20), nullable=False)  # email, sms
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)


class Llave(db.Model):
    """RS2: Llave USB para autenticación"""
    __tablename__ = 'llave'
    
    idDispositivo = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)


class RegistroAcceso(db.Model):
    """RS3 y RS6: Monitoreo de accesos al sistema"""
    __tablename__ = 'registro_acceso'
    
    idRegistro = db.Column(db.Integer, primary_key=True)
    # Columna String
    usuario = db.Column(db.String(50), nullable=False)
    fechaHora = db.Column(db.DateTime, default=datetime.utcnow)
    ipAcceso = db.Column(db.String(50), nullable=False)
    resultado = db.Column(db.String(20), nullable=False)  # exitoso, fallido, bloqueado
    tipoAcceso = db.Column(db.String(50), nullable=True)
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)
    # 🌟 Relación ORM renombrada para evitar conflicto con la columna 'usuario'
    usuario_obj = db.relationship('Usuario', back_populates='accesos')

class RecuperarCuenta(db.Model):
    """RS4: Recuperación de usuario/contraseña"""
    __tablename__ = 'recuperar_cuenta'
    
    idRecuperacion = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), nullable=False)
    # Columna String
    usuario = db.Column(db.String(50), nullable=False)
    fechaSolicitud = db.Column(db.Date, default=datetime.utcnow)
    fechaExpiracion = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, usado, expirado
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)
    # 🌟 Relación ORM renombrada para evitar conflicto con la columna 'usuario'
    usuario_obj = db.relationship('Usuario', back_populates='recuperaciones')


class Sesion(db.Model):
    """RS5 y RS7: Gestión de sesiones de trabajo"""
    __tablename__ = 'sesion'
    
    idSesion = db.Column(db.Integer, primary_key=True)
    # Columna String
    usuario = db.Column(db.String(50), nullable=False)
    fechaInicio = db.Column(db.DateTime, default=datetime.utcnow)
    fechaFin = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(20), default='activa')  # activa, cerrada, expirada
    direccionIp = db.Column(db.String(50), nullable=False)
    
    # Foreign Key
    idUser = db.Column(db.Integer, db.ForeignKey('usuario.idUser'), nullable=False)
    usuario_obj = db.relationship('Usuario', back_populates='sesiones')


class Auditoria(db.Model):
    """RS3: Monitoreo de creación de usuarios"""
    __tablename__ = 'auditoria'
    
    idAuditoria = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.DateTime, nullable=False)
    fechaHora = db.Column(db.DateTime, nullable=False)


class Admin(db.Model):
    """Administrador del sistema"""
    __tablename__ = 'admin'
    
    idAdmin = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(150), unique=True, nullable=False)