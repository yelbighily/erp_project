from django.utils import timezone
from django.db import transaction
from .models import Lead, Account, Contact, Opportunity


def convert_lead(lead, user):
    """
    Converts a Lead into an Account + Contact.
    Marks the lead as CONVERTED.
    Returns (account, contact).
    """
    if lead.status == "CONVERTED":
        raise ValueError("Lead is already converted.")

    with transaction.atomic():
        # Create or find the Account
        account, _ = Account.objects.get_or_create(
            company=lead.company,
            name=lead.company_name or lead.full_name,
            defaults={
                "type":        "PROSPECT",
                "phone":       lead.phone,
                "email":       lead.email,
                "assigned_to": user,
                "created_by":  user,
                "updated_by":  user,
            }
        )

        # Create Contact
        contact = Contact.objects.create(
            company=lead.company,
            account=account,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            assigned_to=user,
            created_by=user,
            updated_by=user,
        )

        # Mark lead converted
        lead.status = "CONVERTED"
        lead.converted_at = timezone.now()
        lead.converted_account = account
        lead.updated_by = user
        lead.save(update_fields=[
            "status", "converted_at",
            "converted_account", "updated_by"
        ])

    return account, contact


def get_pipeline_summary(company):
    """
    Returns opportunity counts and total value per stage.
    Used by the dashboard widget.
    """
    from django.db.models import Count, Sum
    return (
        Opportunity.objects
        .filter(company=company, is_active=True)
        .exclude(stage__in=["WON", "LOST"])
        .values("stage")
        .annotate(count=Count("id"), total=Sum("amount"))
        .order_by("stage")
    )


def get_crm_dashboard_stats(company):
    """Returns dict of key CRM stats for the dashboard widget."""
    return {
        "new_leads": Lead.objects.filter(
            company=company, status="NEW", is_active=True
        ).count(),
        "open_opportunities": Opportunity.objects.filter(
            company=company, is_active=True
        ).exclude(stage__in=["WON", "LOST"]).count(),
        "accounts": Account.objects.filter(
            company=company, is_active=True
        ).count(),
        "activities_due": __import__(
            "apps.crm.models", fromlist=["Activity"]
        ).Activity.objects.filter(
            company=company,
            status="PLANNED",
            is_active=True,
        ).count(),
    }