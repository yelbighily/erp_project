from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Company, UserCompanyRole, CompanyModule

def login_view(request):
    if request.user.is_authenticated:
        return redirect("erp_core:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Middleware will handle company selection on next request
            return redirect(request.POST.get("next") or "erp_core:dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "erp_core/login.html")


def logout_view(request):
    # Clear company from session before logout
    request.session.pop("active_company_id", None)
    logout(request)
    return redirect("erp_core:login")


@login_required
def select_company(request):
    """Shown when a user belongs to multiple companies."""
    roles = UserCompanyRole.objects.filter(
        user=request.user, is_active=True
    ).select_related("company")

    if request.method == "POST":
        company_id = request.POST.get("company_id")
        # Verify the user actually belongs to this company
        if roles.filter(company_id=company_id).exists():
            request.session["active_company_id"] = int(company_id)
            return redirect("erp_core:dashboard")
        else:
            messages.error(request, "Invalid company selection.")

    return render(request, "erp_core/select_company.html", {"roles": roles})


@login_required
def switch_company(request, company_id):
    """Called from the topbar company switcher."""
    exists = UserCompanyRole.objects.filter(
        user=request.user,
        company_id=company_id,
        is_active=True,
    ).exists()

    if exists:
        request.session["active_company_id"] = company_id
        messages.success(request, "Company switched.")
    else:
        messages.error(request, "You don't have access to that company.")

    return redirect(request.META.get("HTTP_REFERER", "erp_core:dashboard"))


@login_required
def dashboard(request):
    company = request.current_company
    enabled_modules = CompanyModule.objects.filter(
        company=company, is_enabled=True
    ).values_list("module", flat=True)

    return render(request, "erp_core/dashboard.html", {
        "company": company,
        "enabled_modules": list(enabled_modules),
    })