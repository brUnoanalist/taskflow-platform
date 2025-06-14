# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    # ... (tus clases Status y los campos status, bio, reputation se quedan igual) ...

    # --- AÑADIR ESTOS DOS CAMPOS PARA SOLUCIONAR EL ERROR ---
    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="customuser_set", # <--- NOMBRE ÚNICO
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="customuser_set", # <--- NOMBRE ÚNICO
        related_query_name="user",
    )
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo'
        VERIFICATION_PENDING = 'VERIFICATION_PENDING', 'Verificación Pendiente'

    # --- Campos Personalizados ---
    
    # El estado del usuario en la plataforma.
    status = models.CharField(
        "Estado", 
        max_length=50, 
        choices=Status.choices, 
        default=Status.ACTIVE
    )

    # La biografía del usuario.
    bio = models.TextField("Biografía", max_length=500, blank=True)
    
    # Campo de reputación, calculado en base a las tareas completadas.
    # Un número entre 1 y 5, por ejemplo.
    reputation = models.DecimalField(
        "Reputación",
        max_digits=3,
        decimal_places=2,
        default=3.0, # Todos empiezan con una reputación perfecta
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )

    def __str__(self):
        return self.username