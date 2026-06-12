from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Funcionario


class CustomUserAdmin(DjangoUserAdmin):
	change_form_template = 'admin/change_form_with_back.html'

	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		extra_context['back_url'] = request.META.get('HTTP_REFERER')
		return super().change_view(request, object_id, form_url, extra_context=extra_context)


class FuncionarioAdmin(admin.ModelAdmin):
	change_form_template = 'admin/change_form_with_back.html'

	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		extra_context['back_url'] = request.META.get('HTTP_REFERER')
		return super().change_view(request, object_id, form_url, extra_context=extra_context)


# unregister default User admin and register custom
try:
	admin.site.unregister(User)
except Exception:
	pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(Funcionario, FuncionarioAdmin)
