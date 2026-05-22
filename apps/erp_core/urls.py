from django.urls import path
from . import views

app_name = "erp_core"

urlpatterns = [
    path("auth/login/",          views.login_view,      name="login"),
    path("auth/logout/",         views.logout_view,     name="logout"),
    path("auth/select-company/", views.select_company,  name="select_company"),
    path("company/switch/<int:company_id>/", views.switch_company, name="switch_company"),
    path("company/create/",      views.company_create,  name="company_create"),
    path("dashboard/",           views.dashboard,       name="dashboard"),
]