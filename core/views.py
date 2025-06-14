# core/views.py
from django.shortcuts import render
from tasks.views import TaskListHomeView # Importamos la vista que lista las tareas

def home_dispatch_view(request):
    """
    Esta vista actúa como un despachador en la ruta raíz.
    - Si el usuario está autenticado, le muestra el dashboard de tareas.
    - Si no lo está, le muestra la página pública de aterrizaje.
    """
    if request.user.is_authenticated:
        # Llama a la vista basada en clase TaskListHomeView como si fuera una función.
        # Esto reutiliza la lógica que ya tenemos para obtener la lista de tareas.
        return TaskListHomeView.as_view()(request)

    # Para usuarios anónimos, renderiza la landing page.
    return render(request, 'public/landing.html')