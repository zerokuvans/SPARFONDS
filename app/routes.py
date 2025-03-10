from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, db, Ahorro
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

# Configurar logging para depuración
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Redirigir directamente a la página de login
    return redirect(url_for('main.login'))

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigir al dashboard correspondiente
    if current_user.is_authenticated:
        logger.debug(f"Usuario ya autenticado: {current_user.documento}, Rol: {current_user.rol}")
        if current_user.rol == 'administrativo':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.rol == 'ahorrador':
            return redirect(url_for('main.saver_dashboard'))
        else:
            # Para cualquier otro rol o valor nulo, mostrar un dashboard genérico
            flash(f'Rol no reconocido: {current_user.rol}', 'warning')
            return redirect(url_for('main.admin_dashboard'))  # Redirigir por defecto
    
    if request.method == 'POST':
        documento = request.form.get('documento')
        password = request.form.get('password')
        
        logger.debug(f"Intento de login para documento: {documento}")
        
        try:
            # Convertir a entero porque la columna es tipo INTEGER en la BD
            documento_int = int(documento)
            user = User.query.filter_by(documento=documento_int).first()
            
            if user:
                logger.debug(f"Usuario encontrado: ID={user.id}, Documento={user.documento}, Rol={user.rol}, Password={user.password}")
                logger.debug(f"¿Contraseña coincide? {user.password == password}")
            else:
                logger.debug(f"Usuario no encontrado para documento: {documento_int}")
            
            # Verificación directa de contraseña sin hash
            if user and user.password == password:
                login_user(user)
                logger.debug(f"Login exitoso para: {user.documento}, Rol={user.rol}")
                
                # Redirección basada en rol
                if user.rol == 'administrativo':
                    logger.debug("Redirigiendo a admin_dashboard")
                    return redirect(url_for('main.admin_dashboard'))
                elif user.rol == 'ahorrador':
                    logger.debug("Redirigiendo a saver_dashboard")
                    return redirect(url_for('main.saver_dashboard'))
                else:
                    # Para cualquier otro rol, dirigir a un dashboard genérico
                    logger.debug(f"Rol no reconocido o nulo: '{user.rol}'. Redirigiendo a dashboard por defecto.")
                    flash(f'Rol no específico: {user.rol}', 'warning')
                    return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
                logger.debug("Credenciales incorrectas")
        except ValueError:
            flash('El documento debe ser un número', 'danger')
            logger.debug(f"Error de conversión: documento '{documento}' no es un número válido")
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('main.login'))

@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    logger.debug(f"Acceso a admin_dashboard por usuario: {current_user.documento}, Rol: {current_user.rol}")
    # Permitir acceso incluso si el rol no es exactamente 'administrativo'
    # Comentamos la restricción temporalmente
    # if current_user.rol != 'administrativo':
    #    flash('No tienes permiso para acceder a esta página', 'danger')
    #    return redirect(url_for('main.login'))
    
    return render_template('admin_dashboard.html')

@main.route('/saver_dashboard')
@login_required
def saver_dashboard():
    logger.debug(f"Acceso a saver_dashboard por usuario: {current_user.documento}, Rol: {current_user.rol}")
    # Permitir acceso incluso si el rol no es exactamente 'ahorrador'
    # Comentamos la restricción temporalmente
    # if current_user.rol != 'ahorrador':
    #    flash('No tienes permiso para acceder a esta página', 'danger')
    #    return redirect(url_for('main.login'))
    
    # Obtener los ahorros del usuario actual
    ahorros_usuario = Ahorro.query.filter_by(usuario_id=current_user.id).all()
    
    # Calcular el saldo total ahorrado
    total_ahorrado = sum(ahorro.monto for ahorro in ahorros_usuario)
    
    # Calcular la rentabilidad (1.6% del total ahorrado)
    tasa_rentabilidad = 0.016  # 1.6%
    rentabilidad = total_ahorrado * tasa_rentabilidad
    
    # Obtener los 5 ahorros más recientes para el historial
    ahorros_recientes = Ahorro.query.filter_by(usuario_id=current_user.id).order_by(Ahorro.fecha.desc()).limit(5).all()
    
    return render_template('saver_dashboard.html', 
                          total_ahorrado=total_ahorrado,
                          rentabilidad=rentabilidad,
                          ahorros_recientes=ahorros_recientes,
                          tasa_rentabilidad=tasa_rentabilidad*100)

# ===== GESTIÓN DE USUARIOS =====

@main.route('/manage_users')
@login_required
def manage_users():
    """Muestra la lista de todos los usuarios"""
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Formulario para crear un nuevo usuario"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            tipo_ident = request.form.get('tipo_ident')
            documento = int(request.form.get('documento'))
            nombre = request.form.get('nombre')
            apellidos = request.form.get('apellidos')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')
            correo = request.form.get('correo')
            
            # Convertir la fecha de nacimiento
            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date() if fecha_nacimiento_str else None
            
            password = request.form.get('password')
            rol = request.form.get('rol')
            
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(documento=documento).first()
            if existing_user:
                flash('Ya existe un usuario con ese documento', 'danger')
                return render_template('create_user.html')
            
            # Obtener el siguiente ID disponible (esto es un workaround si autoincrement no funciona)
            max_id = db.session.query(db.func.max(User.id)).scalar() or 0
            next_id = max_id + 1
            
            # Crear nuevo usuario con ID explícito
            new_user = User(
                id=next_id,
                tipo_ident=tipo_ident,
                documento=documento,
                nombre=nombre,
                apellidos=apellidos,
                direccion=direccion,
                telefono=telefono,
                correo=correo,
                fecha_nacimiento=fecha_nacimiento,
                password=password,
                rol=rol
            )
            
            # Guardar en la base de datos
            db.session.add(new_user)
            db.session.commit()
            
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('main.manage_users'))
            
        except ValueError as e:
            flash(f'Error en los datos del formulario: {str(e)}', 'danger')
            logger.error(f"Error de formato: {str(e)}")
            return render_template('create_user.html')
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            flash('Error al crear el usuario. Revise que el documento no esté duplicado.', 'danger')
            return render_template('create_user.html')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado: {str(e)}")
            flash(f'Error inesperado: {str(e)}', 'danger')
            return render_template('create_user.html')
            
    return render_template('create_user.html')

@main.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Formulario para editar un usuario existente"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos del usuario
            user.tipo_ident = request.form.get('tipo_ident')
            user.documento = int(request.form.get('documento'))
            user.nombre = request.form.get('nombre')
            user.apellidos = request.form.get('apellidos')
            user.direccion = request.form.get('direccion')
            user.telefono = request.form.get('telefono')
            user.correo = request.form.get('correo')
            
            # Convertir la fecha de nacimiento
            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            if fecha_nacimiento_str:
                user.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Solo actualizar la contraseña si se proporciona una nueva
            new_password = request.form.get('password')
            if new_password:
                user.password = new_password
                
            user.rol = request.form.get('rol')
            
            # Guardar cambios
            db.session.commit()
            
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('main.manage_users'))
            
        except ValueError as e:
            flash(f'Error en los datos del formulario: {str(e)}', 'danger')
            logger.error(f"Error de formato: {str(e)}")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            flash('Error al actualizar el usuario. Revise que el documento no esté duplicado.', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado: {str(e)}")
            flash(f'Error inesperado: {str(e)}', 'danger')
    
    return render_template('edit_user.html', user=user)

@main.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Elimina un usuario de la base de datos"""
    try:
        user = User.query.get_or_404(user_id)
        
        # No permitir que un usuario se elimine a sí mismo
        if user.id == current_user.id:
            flash('No puedes eliminar tu propio usuario', 'danger')
            return redirect(url_for('main.manage_users'))
        
        db.session.delete(user)
        db.session.commit()
        
        flash('Usuario eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar usuario: {str(e)}")
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    
    return redirect(url_for('main.manage_users'))

# ===== GESTIÓN DE AHORROS =====

@main.route('/manage_ahorros')
@login_required
def manage_ahorros():
    """Muestra la lista de todos los ahorros"""
    # Obtener todos los ahorros con información del usuario
    ahorros = Ahorro.query.join(User).all()
    return render_template('manage_ahorros.html', ahorros=ahorros)

@main.route('/create_ahorro', methods=['GET', 'POST'])
@login_required
def create_ahorro():
    """Formulario para crear un nuevo ahorro"""
    # Obtener la lista de usuarios ahorradores para el formulario
    usuarios = User.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            usuario_id = int(request.form.get('usuario_id'))
            monto = int(request.form.get('monto'))
            fecha_str = request.form.get('fecha')
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else datetime.now().date()
            concepto = request.form.get('concepto')
            
            # Verificar que el usuario existe
            usuario = User.query.get(usuario_id)
            if not usuario:
                flash('El usuario seleccionado no existe', 'danger')
                return render_template('create_ahorro.html', usuarios=usuarios, today=today)
            
            # Obtener el siguiente ID disponible
            max_id = db.session.query(db.func.max(Ahorro.id)).scalar() or 0
            next_id = max_id + 1
            
            # Crear nuevo ahorro
            new_ahorro = Ahorro(
                id=next_id,
                usuario_id=usuario_id,
                monto=monto,
                fecha=fecha,
                concepto=concepto
            )
            
            # Guardar en la base de datos
            db.session.add(new_ahorro)
            db.session.commit()
            
            flash('Ahorro registrado correctamente', 'success')
            return redirect(url_for('main.manage_ahorros'))
            
        except ValueError as e:
            flash(f'Error en los datos del formulario: {str(e)}', 'danger')
            logger.error(f"Error de formato: {str(e)}")
            return render_template('create_ahorro.html', usuarios=usuarios, today=today)
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            flash('Error al registrar el ahorro', 'danger')
            return render_template('create_ahorro.html', usuarios=usuarios, today=today)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado: {str(e)}")
            flash(f'Error inesperado: {str(e)}', 'danger')
            return render_template('create_ahorro.html', usuarios=usuarios, today=today)
            
    return render_template('create_ahorro.html', usuarios=usuarios, today=today)

@main.route('/edit_ahorro/<int:ahorro_id>', methods=['GET', 'POST'])
@login_required
def edit_ahorro(ahorro_id):
    """Formulario para editar un ahorro existente"""
    ahorro = Ahorro.query.get_or_404(ahorro_id)
    usuarios = User.query.all()
    
    if request.method == 'POST':
        try:
            # Actualizar datos del ahorro
            ahorro.usuario_id = int(request.form.get('usuario_id'))
            ahorro.monto = int(request.form.get('monto'))
            
            fecha_str = request.form.get('fecha')
            if fecha_str:
                ahorro.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            ahorro.concepto = request.form.get('concepto')
            
            # Guardar cambios
            db.session.commit()
            
            flash('Ahorro actualizado correctamente', 'success')
            return redirect(url_for('main.manage_ahorros'))
            
        except ValueError as e:
            flash(f'Error en los datos del formulario: {str(e)}', 'danger')
            logger.error(f"Error de formato: {str(e)}")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            flash('Error al actualizar el ahorro', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado: {str(e)}")
            flash(f'Error inesperado: {str(e)}', 'danger')
    
    return render_template('edit_ahorro.html', ahorro=ahorro, usuarios=usuarios)

@main.route('/delete_ahorro/<int:ahorro_id>', methods=['POST'])
@login_required
def delete_ahorro(ahorro_id):
    """Elimina un ahorro de la base de datos"""
    try:
        ahorro = Ahorro.query.get_or_404(ahorro_id)
        
        db.session.delete(ahorro)
        db.session.commit()
        
        flash('Ahorro eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar ahorro: {str(e)}")
        flash(f'Error al eliminar el ahorro: {str(e)}', 'danger')
    
    return redirect(url_for('main.manage_ahorros'))

@main.route('/reportes_ahorros')
@login_required
def reportes_ahorros():
    """Muestra reportes de ahorros por usuario con cálculos de rendimiento y proyección anual"""
    
    # Obtener todos los usuarios que tienen ahorros
    usuarios_con_ahorros = db.session.query(User).join(Ahorro).distinct().all()
    
    # Lista para almacenar los datos de reporte
    datos_reporte = []
    
    # Tasa de rendimiento anual (1.6%)
    tasa_rendimiento = 0.016
    
    for usuario in usuarios_con_ahorros:
        # Calcular el total ahorrado por el usuario
        total_ahorrado = db.session.query(db.func.sum(Ahorro.monto)).filter(Ahorro.usuario_id == usuario.id).scalar() or 0
        
        # Convertir a float para poder hacer la multiplicación
        if isinstance(total_ahorrado, Decimal):
            total_ahorrado = float(total_ahorrado)
            
        # Calcular el rendimiento (1.6% del total)
        rendimiento = total_ahorrado * tasa_rendimiento
        
        # Calcular la proyección anual (considerando que el usuario seguirá ahorrando al mismo ritmo)
        # Primero, calculamos el promedio mensual
        primer_ahorro = db.session.query(Ahorro.fecha).filter(Ahorro.usuario_id == usuario.id).order_by(Ahorro.fecha).first()
        
        if primer_ahorro:
            # Fecha del primer ahorro
            fecha_primer_ahorro = primer_ahorro[0]
            
            # Calcular meses transcurridos desde el primer ahorro
            hoy = datetime.now().date()
            meses_transcurridos = (hoy.year - fecha_primer_ahorro.year) * 12 + hoy.month - fecha_primer_ahorro.month
            
            # Evitar división por cero
            if meses_transcurridos > 0:
                promedio_mensual = total_ahorrado / meses_transcurridos
            else:
                promedio_mensual = total_ahorrado
                
            # Proyección anual: lo actual + (promedio mensual * meses restantes) + rendimiento anual
            meses_restantes = 12 - meses_transcurridos % 12
            proyeccion_anual = total_ahorrado + (promedio_mensual * meses_restantes) + rendimiento
        else:
            promedio_mensual = 0
            proyeccion_anual = total_ahorrado + rendimiento
        
        # Agregar datos a la lista de reportes
        datos_reporte.append({
            'usuario': usuario,
            'total_ahorrado': total_ahorrado,
            'rendimiento': rendimiento,
            'proyeccion_anual': proyeccion_anual,
            'promedio_mensual': promedio_mensual
        })
    
    return render_template('reportes_ahorros.html', 
                          datos_reporte=datos_reporte, 
                          tasa_rendimiento=tasa_rendimiento*100,
                          fecha_actual=datetime.now())

@main.route('/mis_ahorros')
@login_required
def mis_ahorros():
    """Muestra el historial completo de ahorros del usuario"""
    
    # Obtener todos los ahorros del usuario actual ordenados por fecha (más reciente primero)
    ahorros_usuario = Ahorro.query.filter_by(usuario_id=current_user.id).order_by(Ahorro.fecha.desc()).all()
    
    # Calcular el saldo total ahorrado
    total_ahorrado = sum(ahorro.monto for ahorro in ahorros_usuario)
    
    # Calcular la rentabilidad (1.6% del total ahorrado)
    tasa_rentabilidad = 0.016  # 1.6%
    rentabilidad = total_ahorrado * tasa_rentabilidad
    
    return render_template('mis_ahorros.html', 
                          ahorros=ahorros_usuario,
                          total_ahorrado=total_ahorrado,
                          rentabilidad=rentabilidad,
                          tasa_rentabilidad=tasa_rentabilidad*100)

@main.route('/mi_perfil')
@login_required
def mi_perfil():
    """Muestra los datos personales del usuario"""
    return render_template('mi_perfil.html', usuario=current_user, now=datetime.now) 