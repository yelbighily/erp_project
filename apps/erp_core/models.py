
from django.contrib.auth.models import AbstractUser
from django.db import models

# ── Custom User ─────────────────────────────────────────────────
class User(AbstractUser):
    """Extends Django's built-in User. Add extra fields here."""
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone  = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "erp_user"

    def __str__(self):
        return self.get_full_name() or self.username


# ── BaseModel ────────────────────────────────────────────────────
class BaseModel(models.Model):
    """
    Abstract base inherited by every business model.
    Gives us: audit fields, company scoping, soft delete.
    """
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    updated_by  = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_active   = models.BooleanField(default=True)

    class Meta:
        abstract = True  # no DB table created for this


# ── Company ──────────────────────────────────────────────────────
class Company(BaseModel):
    INDUSTRY_CHOICES = [
        ("TRADING",       "Trading"),
        ("MANUFACTURING", "Manufacturing"),
        ("SERVICES",      "Services"),
        ("MIXED",         "Mixed"),
    ]

    name              = models.CharField(max_length=200)
    legal_name        = models.CharField(max_length=200, blank=True)
    tax_id            = models.CharField(max_length=50, blank=True)
    industry_type     = models.CharField(
        max_length=20, choices=INDUSTRY_CHOICES, default="TRADING"
    )
    base_currency     = models.CharField(max_length=3, default="USD")
    default_language  = models.CharField(max_length=10, default="en")
    logo              = models.ImageField(
        upload_to="company_logos/", null=True, blank=True
    )
    address           = models.TextField(blank=True)
    phone             = models.CharField(max_length=30, blank=True)
    email             = models.EmailField(blank=True)
    website           = models.URLField(blank=True)

    class Meta:
        db_table  = "erp_company"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


# ── User ↔ Company membership ────────────────────────────────────
class UserCompanyRole(models.Model):
    ROLE_CHOICES = [
        ("OWNER",    "Owner"),
        ("ADMIN",    "Admin"),
        ("ACCOUNTANT","Accountant"),
        ("SALES",    "Sales"),
        ("PURCHASE", "Purchase"),
        ("WAREHOUSE","Warehouse"),
        ("HR",       "HR Manager"),
        ("MFG",      "Manufacturing Manager"),
        ("VIEWER",   "Viewer"),
    ]

    user       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="company_roles"
    )
    company    = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="user_roles"
    )
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active  = models.BooleanField(default=True)
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = "erp_user_company_role"
        unique_together = [("user", "company")]

    def __str__(self):
        return f"{self.user} @ {self.company} ({self.role})"


# ── Module activation flags ──────────────────────────────────────
class CompanyModule(models.Model):
    MODULE_CHOICES = [
        ("crm",           "CRM"),
        ("sales",         "Sales"),
        ("purchase",      "Purchase"),
        ("inventory",     "Inventory"),
        ("manufacturing", "Manufacturing"),
        ("hr",            "HR"),
        ("accounting",    "Accounting"),
        ("reporting",     "Reporting"),
    ]

    company    = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="modules"
    )
    module     = models.CharField(max_length=20, choices=MODULE_CHOICES)
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = "erp_company_module"
        unique_together = [("company", "module")]

    def __str__(self):
        return f"{self.company} — {self.module}"