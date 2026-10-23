from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Agent, Alerte, Article, Bien, Demande, Equipement, PhotoBien, Ville, Avis
from .stats import stats_data

import json

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone


# --- Classe personnalisée pour l'admin (avec statistiques) ---
class CustomAdminSite(AdminSite):
    site_header = "El Ouabdi Immobilier"
    site_title = "El Ouabdi Admin"
    index_title = "Tableau de bord"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_biens'] = Bien.objects.count()
        extra_context['biens_publies'] = Bien.objects.filter(publie=True).count()
        extra_context['demandes_en_attente'] = Demande.objects.filter(traitee=False).count()
        extra_context['total_avis'] = Avis.objects.filter(est_approuve=True).count()
        extra_context['dernieres_demandes'] = Demande.objects.order_by('-recue_le')[:5]
        extra_context['derniers_biens'] = Bien.objects.order_by('-cree_le')[:5]
        extra_context['stats'] = stats_data()  # graphiques du tableau de bord
        return super().index(request, extra_context)

    def get_urls(self):
        # Page « Statistiques » : adresse /admin/statistiques/ (nom de route : admin:statistiques)
        from django.urls import path
        from .stats import statistiques_view
        return [path("statistiques/", self.admin_view(statistiques_view), name="statistiques")] + super().get_urls()

# On dit à Django d'utiliser cette classe
admin.site.__class__ = CustomAdminSite

# --- Les autres admins ---
class PhotoInline(admin.TabularInline):
    model = PhotoBien
    extra = 3

@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display = ("reference", "titre", "transaction", "type_bien", "ville", "prix", "statut", "a_la_une", "publie")
    list_filter = ("transaction", "type_bien", "statut", "ville", "a_la_une", "publie")
    list_editable = ("statut", "a_la_une", "publie")
    search_fields = ("reference", "titre", "quartier", "adresse")
    prepopulated_fields = {"slug": ("titre",)}
    filter_horizontal = ("equipements",)
    inlines = [PhotoInline]
    fieldsets = (
        ("Informations générales", {"fields": ("titre", "slug", "reference", "transaction", "type_bien", "statut", "prix")}),
        ("Localisation", {"fields": ("ville", "quartier", "adresse", "latitude", "longitude")}),
        ("Caractéristiques", {"fields": ("surface", "chambres", "salles_de_bain", "etage", "annee_construction", "equipements")}),
        ("Présentation", {"fields": ("description", "video_url", "agent")}),
        ("Version arabe (facultatif)", {"fields": ("titre_ar", "description_ar")}),
        ("Publication", {"fields": ("a_la_une", "publie")}),
    )

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ("nom", "telephone", "origine", "bien", "recue_le", "traitee")
    list_filter = ("origine", "traitee")
    list_editable = ("traitee",)
    search_fields = ("nom", "telephone", "email")
    readonly_fields = ("recue_le",)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "publie_le", "publie")
    list_editable = ("publie",)
    prepopulated_fields = {"slug": ("titre",)}
    fieldsets = (
        (None, {"fields": ("titre", "slug", "image", "resume", "contenu", "publie", "publie_le")}),
        ("Version arabe (facultatif)", {"fields": ("titre_ar", "resume_ar", "contenu_ar")}),
    )

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ("email", "transaction", "ville", "type_bien", "budget_max", "langue", "actif", "cree_le")
    list_filter = ("actif", "transaction", "langue")
    search_fields = ("email",)
    readonly_fields = ("token", "cree_le")

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom", "nom_ar")
    prepopulated_fields = {"slug": ("nom",)}

@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ("nom", "nom_ar")

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("nom", "fonction", "telephone", "actif")
    list_editable = ("actif",)

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'note', 'est_approuve', 'date_creation')
    list_filter = ('note', 'est_approuve', 'ville')
    list_editable = ('est_approuve',)
    search_fields = ('nom', 'commentaire')
