# users/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import random

class CustomAccountAdapter(DefaultAccountAdapter):
    
    def __init__(self, *args, **kwargs):
        print("--- CustomAccountAdapter is being loaded! ---")
        super().__init__(*args, **kwargs)
    """    
    Adaptador personalizado para la creación de cuentas.
    Anula el comportamiento predeterminado para generar un nombre de usuario único
    cuando no se proporciona uno, evitando errores de restricción UNIQUE.
    """
    def save_user(self, request, user, form, commit=True):
        """
        Este método se invoca al guardar un nuevo usuario.
        Genera un nombre de usuario único si no existe uno.
        """
        # Primero, permite que el adaptador predeterminado haga su trabajo, 
        # pero sin guardar en la base de datos todavía (commit=False).
        user = super().save_user(request, user, form, commit=False)

        if not user.username:
            # Si no hay nombre de usuario, lo generamos a partir del correo electrónico.
            # ej. 'bruno.fuenzalida' de 'bruno.fuenzalida@gmail.com'
            base_username = slugify(user.email.split('@')[0]) or 'user'
            
            # Bucle para garantizar que el nombre de usuario sea único.
            # Si 'bruno.fuenzalida' ya existe, intentará 'bruno.fuenzalida123', etc.
            username = base_username
            while get_user_model().objects.filter(username=username).exists():
                random_number = random.randint(1, 9999)
                username = f"{base_username}{random_number}"
            
            user.username = username
            
        if commit:
            user.save()
            
        return user
