from django import forms
from .models import Lead, Account, Contact, Opportunity, Activity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "first_name", "last_name", "email", "phone",
            "company_name", "source", "status", "score",
            "notes", "assigned_to",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "score": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict assigned_to choices to users in this company
        from apps.erp_core.models import UserCompanyRole
        user_ids = UserCompanyRole.objects.filter(
            company=company, is_active=True
        ).values_list("user_id", flat=True)
        self.fields["assigned_to"].queryset = (
            self.fields["assigned_to"].queryset.filter(id__in=user_ids)
        )
        # Apply base CSS class to all fields
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            "name", "type", "industry",
            "website", "phone", "email",
            "address", "notes", "assigned_to",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "notes":   forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.erp_core.models import UserCompanyRole
        user_ids = UserCompanyRole.objects.filter(
            company=company, is_active=True
        ).values_list("user_id", flat=True)
        self.fields["assigned_to"].queryset = (
            self.fields["assigned_to"].queryset.filter(id__in=user_ids)
        )
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "first_name", "last_name", "email", "phone",
            "job_title", "account", "notes", "assigned_to",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(
            company=company, is_active=True
        )
        from apps.erp_core.models import UserCompanyRole
        user_ids = UserCompanyRole.objects.filter(
            company=company, is_active=True
        ).values_list("user_id", flat=True)
        self.fields["assigned_to"].queryset = (
            self.fields["assigned_to"].queryset.filter(id__in=user_ids)
        )
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            "name", "account", "contact", "stage",
            "amount", "currency", "probability",
            "close_date", "description", "assigned_to",
        ]
        widgets = {
            "close_date":  forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "probability": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(
            company=company, is_active=True
        )
        self.fields["contact"].queryset = Contact.objects.filter(
            company=company, is_active=True
        )
        from apps.erp_core.models import UserCompanyRole
        user_ids = UserCompanyRole.objects.filter(
            company=company, is_active=True
        ).values_list("user_id", flat=True)
        self.fields["assigned_to"].queryset = (
            self.fields["assigned_to"].queryset.filter(id__in=user_ids)
        )
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "type", "subject", "description",
            "status", "due_date", "assigned_to",
            "lead", "account", "contact", "opportunity",
        ]
        widgets = {
            "due_date":    forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Scope all linked object dropdowns to this company
        self.fields["lead"].queryset = Lead.objects.filter(
            company=company, is_active=True
        )
        self.fields["account"].queryset = Account.objects.filter(
            company=company, is_active=True
        )
        self.fields["contact"].queryset = Contact.objects.filter(
            company=company, is_active=True
        )
        self.fields["opportunity"].queryset = Opportunity.objects.filter(
            company=company, is_active=True
        )

        # Make all link fields optional in the form
        for f in ["lead", "account", "contact", "opportunity"]:
            self.fields[f].required = False

        # Scope assigned_to to company users
        from apps.erp_core.models import UserCompanyRole
        user_ids = UserCompanyRole.objects.filter(
            company=company, is_active=True
        ).values_list("user_id", flat=True)
        self.fields["assigned_to"].queryset = (
            self.fields["assigned_to"].queryset.filter(id__in=user_ids)
        )

        # Apply CSS class to all fields
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")