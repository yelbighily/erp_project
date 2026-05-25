from django.contrib import admin
from .models import Lead, Account, Contact, Opportunity, Activity


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "company_name", "source",
                     "status", "score", "assigned_to", "created_at"]
    list_filter   = ["status", "source", "company"]
    search_fields = ["first_name", "last_name", "email", "company_name"]
    readonly_fields = ["converted_at", "converted_account"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display  = ["name", "type", "industry", "phone", "assigned_to"]
    list_filter   = ["type", "company"]
    search_fields = ["name", "email", "phone"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "account", "email", "phone", "job_title"]
    list_filter   = ["company"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display  = ["name", "account", "stage", "amount",
                     "probability", "close_date", "assigned_to"]
    list_filter   = ["stage", "company"]
    search_fields = ["name"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display  = ["subject", "type", "status", "due_date", "assigned_to"]
    list_filter   = ["type", "status", "company"]
    search_fields = ["subject"]