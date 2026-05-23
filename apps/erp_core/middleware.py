from django.shortcuts import redirect
from django.urls import reverse
from .models import Company, UserCompanyRole

EXEMPT_PATHS = ["/auth/", "/admin/", "/static/", "/media/"]


class CurrentCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if any(request.path.startswith(p) for p in EXEMPT_PATHS):
            return self.get_response(request)

        company_id = request.session.get("active_company_id")

        if not company_id:
            roles = UserCompanyRole.objects.filter(
                user=request.user, is_active=True
            ).select_related("company")

            if roles.count() == 1:
                role = roles.first()
                request.session["active_company_id"] = role.company.id
                request.current_company = role.company
                request.user_role = role.role
            else:
                if request.path != reverse("erp_core:select_company"):
                    return redirect("erp_core:select_company")
                request.current_company = None
                request.user_role = None
                return self.get_response(request)
        else:
            try:
                role = UserCompanyRole.objects.select_related("company").get(
                    user=request.user,
                    company_id=company_id,
                    is_active=True,
                )
                request.current_company = role.company
                request.user_role = role.role
            except UserCompanyRole.DoesNotExist:
                del request.session["active_company_id"]
                return redirect("erp_core:select_company")

        # Attach enabled modules to request for use in any template
        # Import here to avoid circular imports at module load time
        from .module_utils import enabled_modules
        request.enabled_modules = enabled_modules(request.current_company)

        return self.get_response(request)