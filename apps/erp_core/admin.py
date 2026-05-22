from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, UserCompanyRole, CompanyModule

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ["username", "email", "first_name", "last_name", "is_staff"]
    fieldsets     = BaseUserAdmin.fieldsets + (
        ("ERP Extra", {"fields": ("avatar", "phone")}),
    )

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ["name", "industry_type", "base_currency", "is_active"]
    list_filter   = ["industry_type", "is_active"]
    search_fields = ["name", "tax_id"]

@admin.register(UserCompanyRole)
class UserCompanyRoleAdmin(admin.ModelAdmin):
    list_display  = ["user", "company", "role", "is_active"]
    list_filter   = ["role", "is_active"]

@admin.register(CompanyModule)
class CompanyModuleAdmin(admin.ModelAdmin):
    list_display  = ["company", "module", "is_enabled"]
    list_filter   = ["module", "is_enabled"]