"""frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from backend.views import Home, Setting_IPCam, Setting_Plate, Access_Recording, delete_IPCamera, Export, images, restart

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', Home),
    path('Setting_IPCam/', Setting_IPCam),
    path('Setting_Plate/', Setting_Plate),
    path('Access_Recording/', Access_Recording),
    path('Export/<str:filename>', Export, name="export"),
    path('images/<str:filename>', images, name="images"),
    path("Delete_IPCamera/", delete_IPCamera),
    path("restart/", restart),
]