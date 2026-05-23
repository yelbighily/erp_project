"""This protects individual views. If someone manually types /inventory/items/ but Inventory is disabled 
for their company, they get a clean error instead of a crash"""

from functools import wraps
from django.shortcuts import render
from django.http import HttpResponseForbidden
from .module_utils import module_enabled


def require_module(module_name):
    """
    View decorator — returns 403 if the module is not enabled
    for the current company.

    Usage:
        @require_module('inventory')
        def item_list(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not module_enabled(request.current_company, module_name):
                return render(
                    request,
                    "erp_core/module_disabled.html",
                    {
                        "module_name": module_name,
                        "company": request.current_company,
                    },
                    status=403,
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator