from django.db import models
from apps.erp_core.models import BaseModel, User


class Lead(BaseModel):
    SOURCE_CHOICES = [
        ("MANUAL",    "Manual entry"),
        ("WEBSITE",   "Website"),
        ("REFERRAL",  "Referral"),
        ("CAMPAIGN",  "Campaign"),
        ("SOCIAL",    "Social media"),
        ("OTHER",     "Other"),
    ]
    STATUS_CHOICES = [
        ("NEW",         "New"),
        ("CONTACTED",   "Contacted"),
        ("QUALIFIED",   "Qualified"),
        ("UNQUALIFIED", "Unqualified"),
        ("CONVERTED",   "Converted"),
    ]

    company      = models.ForeignKey(
        "erp_core.Company", on_delete=models.CASCADE,
        related_name="leads"
    )
    first_name   = models.CharField(max_length=100)
    last_name    = models.CharField(max_length=100)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    source       = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default="MANUAL"
    )
    status       = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="NEW"
    )
    score        = models.PositiveSmallIntegerField(default=0)
    notes        = models.TextField(blank=True)
    assigned_to  = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_leads"
    )
    converted_at    = models.DateTimeField(null=True, blank=True)
    converted_account = models.ForeignKey(
        "Account", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="source_leads"
    )

    class Meta:
        db_table = "crm_lead"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["company", "assigned_to"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Account(BaseModel):
    TYPE_CHOICES = [
        ("CUSTOMER",  "Customer"),
        ("PROSPECT",  "Prospect"),
        ("PARTNER",   "Partner"),
        ("VENDOR",    "Vendor"),
        ("OTHER",     "Other"),
    ]

    company     = models.ForeignKey(
        "erp_core.Company", on_delete=models.CASCADE,
        related_name="accounts"
    )
    name        = models.CharField(max_length=200)
    type        = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="PROSPECT"
    )
    industry    = models.CharField(max_length=100, blank=True)
    website     = models.URLField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    email       = models.EmailField(blank=True)
    address     = models.TextField(blank=True)
    notes       = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_accounts"
    )

    class Meta:
        db_table = "crm_account"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["company", "type"]),
        ]

    def __str__(self):
        return self.name


class Contact(BaseModel):
    company     = models.ForeignKey(
        "erp_core.Company", on_delete=models.CASCADE,
        related_name="contacts"
    )
    account     = models.ForeignKey(
        Account, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="contacts"
    )
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100, blank=True)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    job_title   = models.CharField(max_length=100, blank=True)
    notes       = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_contacts"
    )

    class Meta:
        db_table = "crm_contact"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["company", "account"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Opportunity(BaseModel):
    STAGE_CHOICES = [
        ("PROSPECT",     "Prospect"),
        ("PROPOSAL",     "Proposal"),
        ("NEGOTIATION",  "Negotiation"),
        ("WON",          "Won"),
        ("LOST",         "Lost"),
    ]

    company       = models.ForeignKey(
        "erp_core.Company", on_delete=models.CASCADE,
        related_name="opportunities"
    )
    name          = models.CharField(max_length=200)
    account       = models.ForeignKey(
        Account, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunities"
    )
    contact       = models.ForeignKey(
        Contact, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunities"
    )
    stage         = models.CharField(
        max_length=20, choices=STAGE_CHOICES, default="PROSPECT"
    )
    amount        = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    currency      = models.CharField(max_length=3, default="USD")
    probability   = models.PositiveSmallIntegerField(default=20)
    close_date    = models.DateField(null=True, blank=True)
    description   = models.TextField(blank=True)
    assigned_to   = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_opportunities"
    )
    lost_reason   = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "crm_opportunity"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "stage"]),
            models.Index(fields=["company", "assigned_to"]),
            models.Index(fields=["close_date"]),
        ]

    def __str__(self):
        return self.name

    @property
    def expected_value(self):
        if self.amount:
            return self.amount * self.probability / 100
        return None


class Activity(BaseModel):
    TYPE_CHOICES = [
        ("CALL",    "Call"),
        ("MEETING", "Meeting"),
        ("EMAIL",   "Email"),
        ("NOTE",    "Note"),
        ("TASK",    "Task"),
    ]
    STATUS_CHOICES = [
        ("PLANNED",   "Planned"),
        ("DONE",      "Done"),
        ("CANCELLED", "Cancelled"),
    ]

    company       = models.ForeignKey(
        "erp_core.Company", on_delete=models.CASCADE,
        related_name="activities"
    )
    type          = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="NOTE"
    )
    subject       = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    status        = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PLANNED"
    )
    due_date      = models.DateTimeField(null=True, blank=True)
    assigned_to   = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_activities"
    )

    # Generic links — any activity can attach to any CRM object
    lead          = models.ForeignKey(
        Lead, null=True, blank=True,
        on_delete=models.CASCADE, related_name="activities"
    )
    account       = models.ForeignKey(
        Account, null=True, blank=True,
        on_delete=models.CASCADE, related_name="activities"
    )
    contact       = models.ForeignKey(
        Contact, null=True, blank=True,
        on_delete=models.CASCADE, related_name="activities"
    )
    opportunity   = models.ForeignKey(
        Opportunity, null=True, blank=True,
        on_delete=models.CASCADE, related_name="activities"
    )

    class Meta:
        db_table = "crm_activity"
        ordering = ["-due_date", "-created_at"]
        indexes = [
            models.Index(fields=["company", "type", "status"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.subject}"