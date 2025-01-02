from django.urls import path
from . import views


urlpatterns = [
    path('', views.pdf_file_upload, name='upload-pdf'),
    path('list/', views.pdf_files_list, name='pdf-list'),
    path('delete/<int:pk>/', views.pdf_file_delete, name='pdf-delete'),
    path('extract/', views.extract_datas, name='extract-data'),
    path('all_delete/', views.delete_all_data_and_files,
         name='delete-all-data-and-files'),
]
