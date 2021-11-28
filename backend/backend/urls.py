from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from backend.settings import GOAT_TMP_DIR
from common.img_manager import img_data_manager
from common.templates_data_manager import templates_data_manager
from common.variables_data_manager import variables_data_manager
import os

img_data_manager.init()
templates_data_manager.init()
variables_data_manager.init(templates_data_manager.templates())

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create/', include('create.urls')),
    path('dashboard/', include('dashboard.urls')),
]
