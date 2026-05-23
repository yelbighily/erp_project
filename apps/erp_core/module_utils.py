# This is the central helper everything else calls. 
from functools import lru_cache
from django.core.cache import cache


def module_enabled(company, module_name: str) -> bool:
    """
    Returns True if the given module is enabled for the company.
    Cached per company+module for 60 seconds to avoid repeated DB hits.
    """
    if not company:
        return False

    cache_key = f"module_enabled:{company.id}:{module_name}"
    result = cache.get(cache_key)

    if result is None:
        result = company.modules.filter(
            module=module_name,
            is_enabled=True
        ).exists()
        cache.set(cache_key, result, timeout=60)

    return result


def enabled_modules(company) -> list:
    """Returns list of all enabled module names for the company."""
    if not company:
        return []

    cache_key = f"enabled_modules:{company.id}"
    result = cache.get(cache_key)

    if result is None:
        result = list(
            company.modules.filter(is_enabled=True)
            .values_list("module", flat=True)
        )
        cache.set(cache_key, result, timeout=60)

    return result


def invalidate_module_cache(company_id):
    """
    Call this whenever a CompanyModule record is saved or deleted.
    Clears all module cache entries for the company.
    """
    from .models import CompanyModule
    modules = [c[0] for c in CompanyModule.MODULE_CHOICES]
    for module_name in modules:
        cache.delete(f"module_enabled:{company_id}:{module_name}")
    cache.delete(f"enabled_modules:{company_id}")