from django import template

from ..stats import dashboard_data, stats_data

register = template.Library()


@register.inclusion_tag("admin/_stats_charts.html")
def stats_charts(kpi=True):
    """Graphiques de statistiques : {% load stats_tags %} puis {% stats_charts %}
    (ou {% stats_charts kpi=False %} pour masquer les chiffres clés, déjà présents sur le tableau de bord)."""
    return {"stats": stats_data(), "kpi": kpi}


@register.simple_tag
def dashboard():
    """Données de la page d'accueil de l'admin : {% dashboard as d %}."""
    return dashboard_data()