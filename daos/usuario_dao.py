from models.usuario import Usuario
from database import db

class UsuarioDAO:
    """DAO completo para CRUD de usuarios Militech"""
    
    @classmethod
    def seleccionar_todos(cls):
        """SELECT * FROM usuarios ORDER BY usuario"""
        return Usuario.query.order_by(Usuario.usuario).all()
    
    @classmethod
    def seleccionar_por_usuario(cls, usuario):
        """SELECT * WHERE usuario = ?"""
        return Usuario.query.get(usuario)
    
    @classmethod
    def insertar(cls, usuario_data):
        """INSERT INTO usuarios"""
        try:
            # Verificar si ya existe
            if cls.seleccionar_por_usuario(usuario_data['usuario']):
                return None
            
            nuevo = Usuario(**usuario_data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar: {e}")
            return None
    
    @classmethod
    def actualizar(cls, usuario_data):
        """UPDATE usuarios SET ... WHERE usuario = ?"""
        try:
            usuario = cls.seleccionar_por_usuario(usuario_data['usuario'])
            if not usuario:
                return None
            
            # Actualizar campos permitidos
            campos_permitidos = ['password', 'rango', 'nombre']
            for campo in campos_permitidos:
                if campo in usuario_data:
                    setattr(usuario, campo, usuario_data[campo])
            
            db.session.commit()
            return usuario
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar: {e}")
            return None
    
    @classmethod
    def eliminar(cls, usuario):
        """DELETE FROM usuarios WHERE usuario = ?"""
        try:
            user = cls.seleccionar_por_usuario(usuario)
            if not user:
                return False
            
            # PRECAUCIÓN: No eliminar sargento o superior
            if user.rango >= 2:
                print(f"Error: No se puede eliminar usuario rango {user.rango}")
                return False
            
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar: {e}")
            return False
    
    @classmethod
    def contar(cls):
        """COUNT(*)"""
        return Usuario.query.count()

