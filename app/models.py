from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column('id_usuarios', db.Integer, primary_key=True)
    documento = db.Column('usuarios_documento', db.Integer, nullable=True)
    password = db.Column('usuarios_password', db.String(45), nullable=True)
    rol = db.Column(db.String(45), nullable=True)
    tipo_ident = db.Column('usuarios_tipo_ident', db.String(45), nullable=True)
    nombre = db.Column('usuarios_nombre', db.String(45), nullable=True)
    apellidos = db.Column('usuarios_apellidos', db.String(45), nullable=True)
    direccion = db.Column('usuarios_direccion', db.String(45), nullable=True)
    telefono = db.Column('usuarios_telefono', db.String(45), nullable=True)
    correo = db.Column('usuarios_correo', db.String(45), nullable=True)
    fecha_nacimiento = db.Column('usuarios_fecha_nacimiento', db.Date, nullable=True)
    fecha_afiliacion = db.Column('usuarios_fecha_afiliacion', db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # Relación con ahorros
    ahorros = db.relationship('Ahorro', backref='usuario', lazy=True)
    
    def get_id(self):
        return str(self.id)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuarios'), nullable=False)
    user = db.relationship('User', backref=db.backref('contributions', lazy=True))

class Ahorro(db.Model):
    __tablename__ = 'ahorros'
    
    id = db.Column('id_ahorros', db.Integer, primary_key=True)
    usuario_id = db.Column('id_usuarios', db.Integer, db.ForeignKey('usuarios.id_usuarios'), nullable=True)
    monto = db.Column('ahorros_valor_ahorro', db.Integer, nullable=True)
    fecha = db.Column('ahorros_fecha_ahorro', db.Date, nullable=True)
    concepto = db.Column('ahorros_observacion', db.String(80), nullable=True)
    
    def __repr__(self):
        return f"<Ahorro {self.id}: {self.monto} - {self.fecha}>" 