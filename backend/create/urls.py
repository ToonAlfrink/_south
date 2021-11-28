from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('edit/', views.edit),
    path('maintenance/', views.maintenance),
    path('save/', views.save),
    path('save-status/', views.save_status),
    path('process-csv/', views.process_csv),
    path('upload-csv/', views.upload_csv),
    path('upload-csv-status/', views.upload_csv_status),
]
