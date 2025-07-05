# tasks/models.py

from django.db import models
from django.conf import settings 
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    """
    Representa una unidad de trabajo publicable en la plataforma.
    El diseño se enfoca en la claridad de las relaciones y en un ciclo de
    vida bien definido a través del campo 'status'.
    """
    class Status(models.TextChoices):
        """
        Define los estados posibles del pipeline de una tarea de forma robusta,
        evitando el uso de strings 'mágicos' en el resto del código.
        """
        POSTED = 'POSTED', 'Publicado'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completado'
        PAID = 'PAID', 'Pagado'
        CANCELLED = 'CANCELLED', 'Cancelado' 

    # --- Relaciones Clave ---

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_tasks',
        verbose_name="Publicado por"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Si el asignado borra su cuenta, la tarea no se borra.
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="Asignado a"
    )

    # --- Detalles de la Tarea ---

    title = models.CharField(
        verbose_name="Título",
        max_length=200
    )
    description = models.TextField(
        verbose_name="Descripción",
        blank=True
    )
    reward = models.DecimalField(
        verbose_name="Recompensa",
        max_digits=10,
        decimal_places=2,
        help_text="Monto a pagar al completar la tarea."
    )
    status = models.CharField(
        verbose_name="Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.POSTED,
        db_index=True # Se añade un índice de DB para optimizar búsquedas por estado.
    )
    
    # --- Timestamps ---

    created_at = models.DateTimeField(
        verbose_name="Fecha de creación",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name="Última actualización",
        auto_now=True
    )
    due_date = models.DateField(
        verbose_name="Fecha Límite",
        null=True,
        blank=True,
        help_text="Fecha opcional en la que la tarea debería estar completada."
    )
    
    owner_comment = models.TextField(
        verbose_name="Comentario del propietario",
        blank=True,
        null=True,
    )
    owner_rating = models.DecimalField(
        verbose_name="Calificación del propietario",
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
    )

    class Meta:
        ordering = ['-created_at'] # Por defecto, las tareas más nuevas aparecen primero.
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return f"'{self.title}' por @{self.posted_by.username}"
    
    
class Application(models.Model):
    """
    Representa una postulación de un usuario a una tarea específica.
    El ciclo lo inicia un usuario y lo cierra el creador de la tarea al asignarlo.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Tarea'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Postulante'
    )
    message = models.TextField(
        verbose_name='Mensaje del postulante',
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de postulación'
    )

    class Meta:
        unique_together = ('task', 'applicant')
        verbose_name = 'Postulación'
        verbose_name_plural = 'Postulaciones'

    def __str__(self):
        return f"{self.applicant.email} → {self.task.title}"
    