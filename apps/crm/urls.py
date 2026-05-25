from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    # Leads
    path("leads/",
         views.lead_list,    name="lead_list"),
    path("leads/create/",
         views.lead_create,  name="lead_create"),
    path("leads/<int:pk>/",
         views.lead_detail,  name="lead_detail"),
    path("leads/<int:pk>/edit/",
         views.lead_edit,    name="lead_edit"),
    path("leads/<int:pk>/convert/",
         views.lead_convert, name="lead_convert"),

    # Accounts
    path("accounts/",
         views.account_list,   name="account_list"),
    path("accounts/create/",
         views.account_create, name="account_create"),
    path("accounts/<int:pk>/",
         views.account_detail, name="account_detail"),
    path("accounts/<int:pk>/edit/",
         views.account_edit,   name="account_edit"),

    # Opportunities
    path("opportunities/",
         views.opportunity_list,      name="opportunity_list"),
    path("opportunities/create/",
         views.opportunity_create,    name="opportunity_create"),
    path("opportunities/<int:pk>/",
         views.opportunity_detail,    name="opportunity_detail"),
    path("opportunities/<int:pk>/edit/",
         views.opportunity_edit,      name="opportunity_edit"),

    # Activities
    path("activities/",
         views.activity_list,   name="activity_list"),
    path("activities/create/",
         views.activity_create, name="activity_create"),
    path("activities/<int:pk>/edit/",
         views.activity_edit,   name="activity_edit"),
    path("activities/<int:pk>/done/",
         views.activity_done,   name="activity_done"),

     # Contacts
    path("contacts/",
         views.contact_list,   name="contact_list"),
    path("contacts/create/",
         views.contact_create, name="contact_create"),
    path("contacts/<int:pk>/",
         views.contact_detail, name="contact_detail"),
    path("contacts/<int:pk>/edit/",
         views.contact_edit,   name="contact_edit"),
]