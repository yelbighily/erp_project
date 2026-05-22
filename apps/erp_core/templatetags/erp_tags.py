from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, request, url_name):
    """Returns 'active' if the current URL matches the given url_name."""
    try:
        return "active" if request.path == reverse(url_name) else ""
    except NoReverseMatch:
        return ""


@register.simple_tag
def module_enabled(company, module_name):
    """Returns True if the module is enabled for the company."""
    if not company:
        return False
    return company.modules.filter(module=module_name, is_enabled=True).exists()


@register.inclusion_tag("base/_sidebar.html", takes_context=True)
def sidebar(context):
    return context


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

        if company and company.modules.filter(
            module=self.module_name, is_enabled=True
        ).exists():
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)


@register.tag("if_module_enabled")
def do_if_module_enabled(parser, token):
    """
    {% if_module_enabled request.current_company 'crm' %}
      ... show CRM menu items ...
    {% endif %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            f"{bits[0]} requires exactly 2 arguments: company and module_name"
        )
    _, company_expr, module_name = bits
    nodelist_true = parser.parse(("endif",))
    parser.delete_first_token()
    return ModuleEnabledNode(company_expr, module_name, nodelist_true, template.NodeList())