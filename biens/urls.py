from django.urls import path

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("biens/", views.liste, name="liste"),
    path("biens/<slug:slug>/", views.bien_detail, name="bien_detail"),
    path("estimation/", views.estimation, name="estimation"),
    path("contact/", views.contact, name="contact"),
    path("a-propos/", views.a_propos, name="a_propos"),
    path("agents/", views.agents, name="agents"),
    path("blog/", views.blog_liste, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("simulateur-credit/", views.simulateur, name="simulateur"),
    path("mentions-legales/", views.mentions_legales, name="mentions_legales"),
    path("confidentialite/", views.confidentialite, name="confidentialite"),
    path("alerte/creer/", views.alerte_creer, name="alerte_creer"),
    path("alerte/supprimer/<uuid:token>/", views.alerte_supprimer, name="alerte_supprimer"),
    path("immobilier/<slug:slug>/", views.ville_detail, name="ville_detail"),
    
    # --- Favoris ---
    path("favoris/<int:bien_id>/toggle/", views.toggle_favori, name="toggle_favori"),
    path("favoris/", views.mes_favoris, name="mes_favoris"),
]