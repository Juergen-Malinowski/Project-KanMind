from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('auth_app.api.urls')),
    path('api/boards/', include('boards_app.api.urls')),
    path('api/tasks/', include('tasks_app.api.urls')),
]
