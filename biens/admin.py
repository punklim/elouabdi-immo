import csv
import re

from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timesince import timesince

from .models import Agent, Alerte, Article, Bien, Demande, Equipement, PhotoBien, Ville, Avis
from .stats import stats_data


# --- Classe personnalisée pour l'admin (avec statistiques) ---
class CustomAdminSite(AdminSite):
    site_header = "El Ouabdi Immobilier"
    site_title = "El Ouabdi Admin"
    index_title = "Tableau de bord"

    def index(self, request, extra_context=None):
        # Les chiffres de l'accueil sont calculés dans le gabarit (balise {% dashboard %}, voir stats.py).
        # Les graphiques détaillés restent disponibles sur la page « Statistiques ».
        return super().index(request, extra_context)

    def approuver_avis(self, request, pk):
        """Bouton « Approuver » du tableau de bord (POST uniquement)."""
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        if not request.user.has_perm("biens.change_avis"):
            raise PermissionDenied
        n = Avis.objects.filter(pk=pk).update(est_approuve=True)
        if n:
            messages.success(request, "Avis approuvé : il est maintenant visible sur le site.")
        return redirect("admin:index")

    def get_urls(self):
        # Page « Statistiques » : adresse /admin/statistiques/ (nom de route : admin:statistiques)
        from django.urls import path
        from .stats import statistiques_view
        return [
            path("statistiques/", self.admin_view(statistiques_view), name="statistiques"),
            path("avis/<int:pk>/approuver/", self.admin_view(self.approuver_avis), name="avis_approuver"),
        ] + super().get_urls()


# On dit à Django d'utiliser cette classe
admin.site.__class__ = CustomAdminSite


def _chiffres(texte):
    return "".join(c for c in texte if c.isdigit())


def _numero_whatsapp(telephone):
    """Numéro au format international sans « + » (0612345678 -> 212612345678)."""
    brut = telephone.strip()
    chiffres = _chiffres(brut)
    if brut.startswith("+"):
        return chiffres
    if chiffres.startswith("00"):
        return chiffres[2:]
    if chiffres.startswith("0") and len(chiffres) == 10:
        return "212" + chiffres[1:]
    return chiffres


def _cellule(valeur):
    """Valeur sûre pour Excel : une saisie visiteur comme « =1+1 » ne doit jamais devenir une formule."""
    texte = "" if valeur is None else str(valeur)
    if texte[:1] in ("=", "+", "-", "@", "\t", "\r") and not re.fullmatch(r"[+\-]?[\d\s().\-]+", texte):
        texte = "'" + texte
    return texte


def _telephone_csv(telephone):
    """Garde le 0 initial dans Excel (0612345678) : seul un numéro formé de chiffres est écrit ainsi."""
    brut = re.sub(r"[\s.\-()]", "", telephone or "")
    if re.fullmatch(r"\+?\d{6,15}", brut):
        return f'="{brut}"'
    return _cellule(telephone)


def _reponse_csv(nom_fichier, entetes, lignes):
    """CSV lisible directement par Excel en français (séparateur « ; », UTF-8 avec BOM)."""
    reponse = HttpResponse(content_type="text/csv; charset=utf-8")
    reponse["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    reponse.write("\ufeff")
    ecrivain = csv.writer(reponse, delimiter=";")
    ecrivain.writerow(entetes)
    for ligne in lignes:
        ecrivain.writerow(ligne)
    return reponse


# --- Les autres admins ---
class PhotoInline(admin.TabularInline):
    model = PhotoBien
    extra = 3


class TranchePrixFilter(admin.SimpleListFilter):
    """Filtre par tranche de prix (loyers mensuels et prix de vente séparés)."""
    title = "tranche de prix"
    parameter_name = "tranche"

    TRANCHES = {
        "loc_5k": ("Location : moins de 5 000 MAD", {"transaction": "location", "prix__lt": 5000}),
        "loc_10k": ("Location : 5 000 à 10 000 MAD", {"transaction": "location", "prix__gte": 5000, "prix__lt": 10000}),
        "loc_plus": ("Location : plus de 10 000 MAD", {"transaction": "location", "prix__gte": 10000}),
        "vente_1m": ("Vente : moins de 1 M MAD", {"transaction": "vente", "prix__lt": 1000000}),
        "vente_3m": ("Vente : 1 à 3 M MAD", {"transaction": "vente", "prix__gte": 1000000, "prix__lt": 3000000}),
        "vente_plus": ("Vente : plus de 3 M MAD", {"transaction": "vente", "prix__gte": 3000000}),
    }

    def lookups(self, request, model_admin):
        return [(cle, libelle) for cle, (libelle, _) in self.TRANCHES.items()]

    def queryset(self, request, queryset):
        if self.value() in self.TRANCHES:
            return queryset.filter(**self.TRANCHES[self.value()][1])
        return queryset


@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display = ("reference", "miniature", "titre", "transaction", "type_bien", "ville", "prix_mad",
                    "statut", "a_la_une", "publie", "voir")
    list_filter = ("transaction", "type_bien", "statut", "ville", "a_la_une", "publie", TranchePrixFilter)
    list_editable = ("statut", "a_la_une", "publie")
    search_fields = ("reference", "titre", "quartier", "adresse")
    prepopulated_fields = {"slug": ("titre",)}
    filter_horizontal = ("equipements",)
    inlines = [PhotoInline]
    actions = ["publier", "depublier", "mettre_a_la_une", "retirer_de_la_une"]
    fieldsets = (
        ("Informations générales", {"fields": ("titre", "slug", "reference", "transaction", "type_bien", "statut", "prix")}),
        ("Localisation", {"fields": ("ville", "quartier", "adresse", "latitude", "longitude")}),
        ("Caractéristiques", {"fields": ("surface", "chambres", "salles_de_bain", "etage", "annee_construction", "equipements")}),
        ("Présentation", {"fields": ("description", "video_url", "agent")}),
        ("Version arabe (facultatif)", {"fields": ("titre_ar", "description_ar")}),
        ("Publication", {"fields": ("a_la_une", "publie")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("ville").prefetch_related("photos")

    @admin.display(description="Photo")
    def miniature(self, obj):
        photo = next(iter(obj.photos.all()), None)
        if not photo or not photo.image:
            return "–"
        try:
            url = photo.image.url
        except Exception:
            return "–"
        return format_html(
            '<img src="{}" alt="" style="width:56px;height:42px;object-fit:cover;border-radius:6px;">', url)

    @admin.display(description="Prix", ordering="prix")
    def prix_mad(self, obj):
        texte = f"{int(obj.prix):,}".replace(",", " ") + " MAD"
        if obj.transaction == Bien.Transaction.LOCATION:
            texte += " / mois"
        return texte

    @admin.display(description="Site")
    def voir(self, obj):
        try:
            url = obj.get_absolute_url()
        except Exception:
            return "–"
        return format_html('<a href="{}" target="_blank" rel="noopener">Voir</a>', url)

    @admin.action(description="Publier sur le site")
    def publier(self, request, queryset):
        n = queryset.update(publie=True)
        self.message_user(request, f"{n} bien(s) publié(s) sur le site.", messages.SUCCESS)

    @admin.action(description="Retirer du site (dépublier)")
    def depublier(self, request, queryset):
        n = queryset.update(publie=False)
        self.message_user(request, f"{n} bien(s) retiré(s) du site.", messages.SUCCESS)

    @admin.action(description="Mettre à la une")
    def mettre_a_la_une(self, request, queryset):
        n = queryset.update(a_la_une=True)
        self.message_user(request, f"{n} bien(s) mis à la une.", messages.SUCCESS)

    @admin.action(description="Retirer de la une")
    def retirer_de_la_une(self, request, queryset):
        n = queryset.update(a_la_une=False)
        self.message_user(request, f"{n} bien(s) retiré(s) de la une.", messages.SUCCESS)


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ("nom", "contact", "origine", "bien", "recue_le", "depuis", "statut")
    list_filter = ("statut", "origine")
    list_editable = ("statut",)
    search_fields = ("nom", "telephone", "email")
    readonly_fields = ("recue_le",)
    exclude = ("traitee",)  # déduit automatiquement du statut
    list_select_related = ("bien",)
    actions = ["marquer_traitees", "marquer_en_cours", "marquer_non_traitees", "exporter_csv"]

    @admin.display(description="Contact")
    def contact(self, obj):
        tel = "".join(c for c in obj.telephone if c.isdigit() or c == "+")
        wa = _numero_whatsapp(obj.telephone)
        return format_html(
            '{} · <a href="tel:{}">Appeler</a> · '
            '<a href="https://wa.me/{}" target="_blank" rel="noopener">WhatsApp</a>',
            obj.telephone, tel, wa)

    @admin.display(description="Reçue depuis", ordering="recue_le")
    def depuis(self, obj):
        duree = timesince(obj.recue_le).split(",")[0].replace("\xa0", " ")
        en_retard = (not obj.traitee) and (timezone.now() - obj.recue_le).total_seconds() > 48 * 3600
        if en_retard:
            return format_html('<span style="color:#E8896F;font-weight:600;">{} (en retard)</span>', duree)
        return duree

    @admin.action(description="Marquer comme traitées")
    def marquer_traitees(self, request, queryset):
        n = queryset.update(statut=Demande.Statut.TRAITEE, traitee=True)
        self.message_user(request, f"{n} demande(s) marquée(s) comme traitée(s).", messages.SUCCESS)

    @admin.action(description="Marquer « En cours »")
    def marquer_en_cours(self, request, queryset):
        n = queryset.update(statut=Demande.Statut.EN_COURS, traitee=False)
        self.message_user(request, f"{n} demande(s) passée(s) « En cours ».", messages.SUCCESS)

    @admin.action(description="Remettre à « Nouveau »")
    def marquer_non_traitees(self, request, queryset):
        n = queryset.update(statut=Demande.Statut.NOUVEAU, traitee=False)
        self.message_user(request, f"{n} demande(s) remise(s) à « Nouveau ».", messages.SUCCESS)

    @admin.action(description="Exporter en CSV (Excel)")
    def exporter_csv(self, request, queryset):
        lignes = []
        for d in queryset.select_related("bien").order_by("-recue_le"):
            lignes.append([
                timezone.localtime(d.recue_le).strftime("%d/%m/%Y %H:%M"),
                _cellule(d.nom), _telephone_csv(d.telephone), _cellule(d.email),
                d.get_origine_display(), _cellule(d.bien.reference if d.bien_id else ""),
                d.get_statut_display(), _cellule(d.message), _cellule(d.note_interne),
            ])
        return _reponse_csv(
            f"demandes-{timezone.localdate():%Y-%m-%d}.csv",
            ["Reçue le", "Nom", "Téléphone", "E-mail", "Origine", "Bien (réf.)", "Statut", "Message", "Note interne"],
            lignes)


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
    list_display = ("email", "transaction", "ville_nom", "type_bien", "budget_max", "langue", "actif", "cree_le")
    list_filter = ("actif", "transaction", "langue")
    search_fields = ("email",)
    readonly_fields = ("token", "cree_le")
    actions = ["exporter_csv"]

    @admin.action(description="Exporter en CSV (Excel)")
    def exporter_csv(self, request, queryset):
        lignes = [[
            timezone.localtime(a.cree_le).strftime("%d/%m/%Y %H:%M"),
            _cellule(a.email), a.get_transaction_display(), a.ville.nom if a.ville_id else "",
            a.get_type_bien_display(), a.budget_max or "", a.langue, "Oui" if a.actif else "Non",
        ] for a in queryset.select_related("ville").order_by("-cree_le")]
        return _reponse_csv(
            f"alertes-{timezone.localdate():%Y-%m-%d}.csv",
            ["Créée le", "E-mail", "Transaction", "Ville", "Type de bien", "Budget max (MAD)", "Langue", "Active"],
            lignes)

    def ville_nom(self, obj):
        """Affiche le nom de la ville ou un tiret si la ville est vide."""
        return obj.ville.nom if obj.ville else "-"
    ville_nom.short_description = "Ville"


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
    actions = ["approuver", "masquer"]

    @admin.action(description="Approuver les avis sélectionnés")
    def approuver(self, request, queryset):
        n = queryset.update(est_approuve=True)
        self.message_user(request, f"{n} avis approuvé(s).", messages.SUCCESS)

    @admin.action(description="Masquer les avis sélectionnés")
    def masquer(self, request, queryset):
        n = queryset.update(est_approuve=False)
        self.message_user(request, f"{n} avis masqué(s).", messages.SUCCESS)