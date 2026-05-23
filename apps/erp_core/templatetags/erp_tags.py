from django import template
from django.urls import reverse, NoReverseMatch
from apps.erp_core.module_utils import module_enabled as _module_enabled

register = template.Library()


@register.simple_tag
def module_enabled(company, module_name):
    """
    Returns True/False for use in {% if %} blocks.
    Usage: {% module_enabled company 'crm' as crm_on %}
    """
    return _module_enabled(company, module_name)


@register.simple_tag(takes_context=True)
def active_class(context, request, url_name):
    """Returns 'active' CSS class if current path matches url_name."""
    try:
        return "active" if request.path == reverse(url_name) else ""
    except NoReverseMatch:
        return ""


class ModuleEnabledNode(template.Node):
    def __init__(self, company_expr, module_name, nodelist_true, nodelist_false):
        self.company_expr = template.Variable(company_expr)
        self.module_name = module_name.strip("'\"")
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        try:
            company = self.company_expr.resolve(context)
        except template.VariableDoesNotExist:
            return self.nodelist_false.render(context)

        if _module_enabled(company, self.module_name):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


@register.tag("if_module_enabled")
def do_if_module_enabled(parser, token):
    """
    Block tag — renders content only if module is enabled.

    Usage:
        {% if_module_enabled request.current_company 'crm' %}
          <a href="...">Leads</a>
        {% endif %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            f"{bits[0]} requires exactly 2 arguments"
        )
    _, company_expr, module_name = bits
    nodelist_true = parser.parse(("endif",))
    parser.delete_first_token()
    return ModuleEnabledNode(
        company_expr, module_name, nodelist_true, template.NodeList()
    )