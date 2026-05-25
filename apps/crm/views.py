from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.erp_core.decorators import require_module
from .models import Lead, Account, Contact, Opportunity, Activity
from .forms import LeadForm, AccountForm, ContactForm, OpportunityForm, ActivityForm
from .services import convert_lead, get_pipeline_summary

def crm_context(company):
    """Shared queryset helper — always scope to company."""
    return {"company": company}


# ── Leads ────────────────────────────────────────────────────────

@login_required
@require_module("crm")
def lead_list(request):
    company = request.current_company
    status  = request.GET.get("status", "")
    qs = Lead.objects.filter(company=company, is_active=True).select_related(
        "assigned_to"
    )
    if status:
        qs = qs.filter(status=status)
    return render(request, "crm/lead_list.html", {
        "leads":          qs,
        "status_filter":  status,
        "status_choices": Lead.STATUS_CHOICES,
    })


@login_required
@require_module("crm")
def lead_create(request):
    company = request.current_company
    form = LeadForm(company, request.POST or None)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.company    = company
        lead.created_by = request.user
        lead.updated_by = request.user
        lead.save()
        messages.success(request, f"Lead '{lead.full_name}' created.")
        return redirect("crm:lead_detail", pk=lead.pk)
    return render(request, "crm/lead_form.html", {"form": form, "action": "Create"})


@login_required
@require_module("crm")
def lead_detail(request, pk):
    company = request.current_company
    lead = get_object_or_404(Lead, pk=pk, company=company)
    return render(request, "crm/lead_detail.html", {
        "lead":       lead,
        "activities": lead.activities.select_related("assigned_to"),
    })


@login_required
@require_module("crm")
def lead_edit(request, pk):
    company = request.current_company
    lead = get_object_or_404(Lead, pk=pk, company=company)
    form = LeadForm(company, request.POST or None, instance=lead)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.updated_by = request.user
        lead.save()
        messages.success(request, "Lead updated.")
        return redirect("crm:lead_detail", pk=lead.pk)
    return render(request, "crm/lead_form.html", {
        "form": form, "action": "Edit", "lead": lead
    })


@login_required
@require_module("crm")
def lead_convert(request, pk):
    company = request.current_company
    lead = get_object_or_404(Lead, pk=pk, company=company)
    if request.method == "POST":
        try:
            account, contact = convert_lead(lead, request.user)
            messages.success(
                request,
                f"Lead converted → Account '{account.name}' and Contact '{contact.full_name}'."
            )
            return redirect("crm:account_detail", pk=account.pk)
        except ValueError as e:
            messages.error(request, str(e))
    return render(request, "crm/lead_convert_confirm.html", {"lead": lead})


# ── Accounts ─────────────────────────────────────────────────────

@login_required
@require_module("crm")
def account_list(request):
    company = request.current_company
    qs = Account.objects.filter(
        company=company, is_active=True
    ).select_related("assigned_to")
    return render(request, "crm/account_list.html", {"accounts": qs})


@login_required
@require_module("crm")
def account_create(request):
    company = request.current_company
    form = AccountForm(company, request.POST or None)
    if form.is_valid():
        acc = form.save(commit=False)
        acc.company    = company
        acc.created_by = request.user
        acc.updated_by = request.user
        acc.save()
        messages.success(request, f"Account '{acc.name}' created.")
        return redirect("crm:account_detail", pk=acc.pk)
    return render(request, "crm/account_form.html", {"form": form, "action": "Create"})


@login_required
@require_module("crm")
def account_detail(request, pk):
    company = request.current_company
    account = get_object_or_404(Account, pk=pk, company=company)
    return render(request, "crm/account_detail.html", {
        "account":       account,
        "contacts":      account.contacts.filter(is_active=True),
        "opportunities": account.opportunities.filter(is_active=True),
        "activities":    account.activities.select_related("assigned_to"),
    })


@login_required
@require_module("crm")
def account_edit(request, pk):
    company = request.current_company
    account = get_object_or_404(Account, pk=pk, company=company)
    form = AccountForm(company, request.POST or None, instance=account)
    if form.is_valid():
        acc = form.save(commit=False)
        acc.updated_by = request.user
        acc.save()
        messages.success(request, "Account updated.")
        return redirect("crm:account_detail", pk=acc.pk)
    return render(request, "crm/account_form.html", {
        "form": form, "action": "Edit", "account": account
    })


# ── Opportunities ─────────────────────────────────────────────────

@login_required
@require_module("crm")
def opportunity_list(request):
    company = request.current_company
    qs = Opportunity.objects.filter(
        company=company, is_active=True
    ).select_related("account", "assigned_to")
    pipeline = get_pipeline_summary(company)
    return render(request, "crm/opportunity_list.html", {
        "opportunities": qs,
        "pipeline":      pipeline,
    })


@login_required
@require_module("crm")
def opportunity_create(request):
    company = request.current_company
    form = OpportunityForm(company, request.POST or None)
    if form.is_valid():
        opp = form.save(commit=False)
        opp.company    = company
        opp.currency   = company.base_currency
        opp.created_by = request.user
        opp.updated_by = request.user
        opp.save()
        messages.success(request, f"Opportunity '{opp.name}' created.")
        return redirect("crm:opportunity_detail", pk=opp.pk)
    return render(request, "crm/opportunity_form.html", {
        "form": form, "action": "Create"
    })


@login_required
@require_module("crm")
def opportunity_detail(request, pk):
    company = request.current_company
    opp = get_object_or_404(Opportunity, pk=pk, company=company)
    return render(request, "crm/opportunity_detail.html", {
        "opportunity": opp,
        "activities":  opp.activities.select_related("assigned_to"),
    })


@login_required
@require_module("crm")
def opportunity_edit(request, pk):
    company = request.current_company
    opp = get_object_or_404(Opportunity, pk=pk, company=company)
    form = OpportunityForm(company, request.POST or None, instance=opp)
    if form.is_valid():
        opp = form.save(commit=False)
        opp.updated_by = request.user
        opp.save()
        messages.success(request, "Opportunity updated.")
        return redirect("crm:opportunity_detail", pk=opp.pk)
    return render(request, "crm/opportunity_form.html", {
        "form": form, "action": "Edit", "opportunity": opp
    })

# ── Activities ────────────────────────────────────────────────────

@login_required
@require_module("crm")
def activity_list(request):
    company = request.current_company
    type_filter   = request.GET.get("type", "")
    status_filter = request.GET.get("status", "")

    qs = Activity.objects.filter(
        company=company, is_active=True
    ).select_related(
        "assigned_to", "lead", "account", "contact", "opportunity"
    )

    if type_filter:
        qs = qs.filter(type=type_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, "crm/activity_list.html", {
        "activities":    qs,
        "type_filter":   type_filter,
        "status_filter": status_filter,
        "type_choices":  Activity.TYPE_CHOICES,
        "status_choices":Activity.STATUS_CHOICES,
    })


@login_required
@require_module("crm")
def activity_create(request):
    company = request.current_company

    # Pre-fill linked object from query params
    initial = {}
    lead_id   = request.GET.get("lead")
    acc_id    = request.GET.get("account")
    cont_id   = request.GET.get("contact")
    opp_id    = request.GET.get("opportunity")
    if lead_id:   initial["lead"]        = lead_id
    if acc_id:    initial["account"]     = acc_id
    if cont_id:   initial["contact"]     = cont_id
    if opp_id:    initial["opportunity"] = opp_id

    form = ActivityForm(company, request.POST or None, initial=initial)

    # Also expose link dropdowns scoped to company
    if request.method == "POST" and form.is_valid():
        act = form.save(commit=False)
        act.company    = company
        act.created_by = request.user
        act.updated_by = request.user
        act.save()
        messages.success(request, f"Activity '{act.subject}' created.")

        # Redirect back to the linked object if there is one
        if act.opportunity:
            return redirect("crm:opportunity_detail", pk=act.opportunity.pk)
        if act.account:
            return redirect("crm:account_detail", pk=act.account.pk)
        if act.lead:
            return redirect("crm:lead_detail", pk=act.lead.pk)
        return redirect("crm:activity_list")

    return render(request, "crm/activity_form.html", {
        "form":   form,
        "action": "Create",
    })


@login_required
@require_module("crm")
def activity_edit(request, pk):
    company = request.current_company
    act = get_object_or_404(Activity, pk=pk, company=company)
    form = ActivityForm(company, request.POST or None, instance=act)

    if form.is_valid():
        act = form.save(commit=False)
        act.updated_by = request.user
        act.save()
        messages.success(request, "Activity updated.")

        if act.opportunity:
            return redirect("crm:opportunity_detail", pk=act.opportunity.pk)
        if act.account:
            return redirect("crm:account_detail", pk=act.account.pk)
        if act.lead:
            return redirect("crm:lead_detail", pk=act.lead.pk)
        return redirect("crm:activity_list")

    return render(request, "crm/activity_form.html", {
        "form":     form,
        "action":   "Edit",
        "activity": act,
    })


@login_required
@require_module("crm")
def activity_done(request, pk):
    """Quick-action: mark an activity as done without opening the edit form."""
    company = request.current_company
    act = get_object_or_404(Activity, pk=pk, company=company)
    act.status     = "DONE"
    act.updated_by = request.user
    act.save(update_fields=["status", "updated_by"])
    messages.success(request, f"'{act.subject}' marked as done.")
    return redirect(request.META.get("HTTP_REFERER", "crm:activity_list"))

# ── Contacts ─────────────────────────────────────────────────────

@login_required
@require_module("crm")
def contact_list(request):
    company  = request.current_company
    account_id = request.GET.get("account", "")
    qs = Contact.objects.filter(
        company=company, is_active=True
    ).select_related("account", "assigned_to")
    if account_id:
        qs = qs.filter(account_id=account_id)
    return render(request, "crm/contact_list.html", {
        "contacts":       qs,
        "account_filter": account_id,
    })


@login_required
@require_module("crm")
def contact_create(request):
    company = request.current_company

    # Pre-fill account from query param
    initial = {}
    account_id = request.GET.get("account")
    if account_id:
        initial["account"] = account_id

    form = ContactForm(company, request.POST or None, initial=initial)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.company    = company
        contact.created_by = request.user
        contact.updated_by = request.user
        contact.save()
        messages.success(request, f"Contact '{contact.full_name}' created.")
        # Redirect back to account if we came from one
        if contact.account:
            return redirect("crm:account_detail", pk=contact.account.pk)
        return redirect("crm:contact_detail", pk=contact.pk)

    return render(request, "crm/contact_form.html", {
        "form": form, "action": "Create"
    })


@login_required
@require_module("crm")
def contact_detail(request, pk):
    company = request.current_company
    contact = get_object_or_404(Contact, pk=pk, company=company)
    return render(request, "crm/contact_detail.html", {
        "contact":       contact,
        "opportunities": contact.opportunities.filter(is_active=True)
                                              .select_related("account"),
        "activities":    contact.activities.select_related("assigned_to"),
    })


@login_required
@require_module("crm")
def contact_edit(request, pk):
    company = request.current_company
    contact = get_object_or_404(Contact, pk=pk, company=company)
    form = ContactForm(company, request.POST or None, instance=contact)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.updated_by = request.user
        contact.save()
        messages.success(request, "Contact updated.")
        return redirect("crm:contact_detail", pk=contact.pk)
    return render(request, "crm/contact_form.html", {
        "form": form, "action": "Edit", "contact": contact
    })    