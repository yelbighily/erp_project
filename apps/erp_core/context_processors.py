def erp_context(request):
    """
    Injects ERP globals into every template context.
    """
    return {
        "current_company": getattr(request, "current_company", None),
        "user_role":       getattr(request, "user_role", None),
        "enabled_modules": getattr(request, "enabled_modules", []),
    }