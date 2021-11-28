from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('urls/<slug:lang>/', views.urls_list),
    path('delete-template/<slug:templateName>/', views.delete_template),
    path('urls/', views.urls_list),
    path('raw-template/<slug:templateName>/', views.raw_template),
    path('reload-templates/', views.reload_templates),
    path('reload-variables/', views.reload_variables),
    path('reload-imgs/', views.reload_img),
]
