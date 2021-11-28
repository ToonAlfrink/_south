from django.conf.urls import include
from django.urls import path

from django.urls import path
from frontend.variables_data_manager import variables_data_manager

from frontend.img_manager import img_data_manager
from . import views

img_data_manager.init()
variables_data_manager.init()

urlpatterns = [
    # path('maintenance/', views.maintenance),
    path("", views.home),
    path("<lang_iso_code>/<content_id>/", views.home),
    path("<lang_iso_code>/", views.home),
]
