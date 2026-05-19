from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('laboratorios/', views.laboratorio_list, name='laboratorio_list'),
    path('laboratorio/create/', views.laboratorio_create, name='laboratorio_create'),
    path('laboratorio/<int:pk>/edit/', views.laboratorio_edit, name='laboratorio_edit'),
    path('laboratorio/<int:pk>/delete/', views.laboratorio_delete, name='laboratorio_delete'),
    path('semestre/', views.semestre_list, name='semestre_list'),
    path('semestre/create/', views.semestre_create, name='semestre_create'),
    path('semestre/<int:pk>/edit/', views.semestre_edit, name='semestre_edit'),
    path('semestre/<int:pk>/delete/', views.semestre_delete, name='semestre_delete'),
    path('agendar/', views.agendamento_create, name='agendamento_create'),
    path('agendar/excluir/<int:pk>/', views.agendamento_delete, name='agendamento_delete'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
]
