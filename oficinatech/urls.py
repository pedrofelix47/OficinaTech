"""
URL configuration for oficinatech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),
    # Django admin route removed — use internal /admin/ instead
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoque/', views.estoque, name='estoque'),
    path('saidas/', views.saidas, name='saidas'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/usuarios/', views.admin_users, name='admin_users'),
    path('admin/usuarios/novo/', views.admin_user_create, name='admin_user_create'),
    path('admin/usuarios/<int:user_id>/editar/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/usuarios/<int:user_id>/deletar/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/fornecedores/', views.admin_fornecedores, name='admin_fornecedores'),
    path('admin/fornecedores/novo/', views.admin_fornecedor_create, name='admin_fornecedor_create'),
    path('admin/fornecedores/<int:pk>/editar/', views.admin_fornecedor_edit, name='admin_fornecedor_edit'),
    path('admin/fornecedores/<int:pk>/deletar/', views.admin_fornecedor_delete, name='admin_fornecedor_delete'),
    path('admin/pecas/', views.admin_pecas, name='admin_pecas'),
    path('admin/pecas/novo/', views.admin_peca_create, name='admin_peca_create'),
    path('admin/pecas/<int:pk>/editar/', views.admin_peca_edit, name='admin_peca_edit'),
    path('admin/pecas/<int:pk>/deletar/', views.admin_peca_delete, name='admin_peca_delete'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
