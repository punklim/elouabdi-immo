"""Statistiques pour le tableau de bord de l'administration (ne nécessite aucune migration)."""
from datetime import date

from django.contrib import admin
from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.formats import date_format

from .models import Alerte, Avis, Bien, Demande, Ville

MOIS_COURTS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
               "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]


def _douze_mois():
    """Les 12 derniers mois, du plus ancien au mois en cours (1er jour de chaque mois)."""
    auj = timezone.localdate()
    mois = []
    for i in range(11, -1, -1):
        m, a = auj.month - i, auj.year
        while m <= 0:
            m += 12
            a -= 1
        mois.append(date(a, m, 1))
    return mois


def _par_mois(queryset, champ_date, mois):
    lignes = (queryset.filter(**{f"{champ_date}__date__gte": mois[0]})
              .annotate(m=TruncMonth(champ_date)).values("m").annotate(n=Count("id")))
    comptes = {(l["m"].year, l["m"].month): l["n"] for l in lignes}
    return [comptes.get((d.year, d.month), 0) for d in mois]


def _repartition(queryset, champ, libelles=None):
    lignes = queryset.values(champ).annotate(n=Count("id")).order_by("-n")
    libelles = libelles or {}
    return {
        "labels": [str(libelles.get(l[champ], l[champ])) for l in lignes],
        "data": [l["n"] for l in lignes],
    }


def stats_data():
    mois = _douze_mois()
    biens, demandes = Bien.objects.all(), Demande.objects.all()
    villes = (Ville.objects.annotate(n=Count("biens")).filter(n__gt=0).order_by("-n")[:8])
    return {
        "mois": [date_format(d, "N y") for d in mois],
        "demandes_par_mois": _par_mois(demandes, "recue_le", mois),
        "biens_par_mois": _par_mois(biens, "cree_le", mois),
        "types": _repartition(biens, "type_bien", dict(Bien.TypeBien.choices)),
        "transactions": _repartition(biens, "transaction", dict(Bien.Transaction.choices)),
        "statuts": _repartition(biens, "statut", dict(Bien.Statut.choices)),
        "origines": _repartition(demandes, "origine", dict(Demande.Origine.choices)),
        "villes": {"labels": [v.nom for v in villes], "data": [v.n for v in villes]},
        "kpi": {
            "biens": biens.count(),
            "publies": biens.filter(publie=True).count(),
            "conclus": biens.filter(statut__in=[Bien.Statut.VENDU, Bien.Statut.LOUE]).count(),
            "demandes": demandes.count(),
            "a_traiter": demandes.filter(traitee=False).count(),
            "alertes": Alerte.objects.filter(actif=True).count(),
        },
    }


# ---------------------------------------------------------------------------
# Page d'accueil de l'administration (maquette « Bonjour … »)
# ---------------------------------------------------------------------------
def _initiales(nom):
    parties = nom.split()
    if not parties:
        return "?"
    if len(parties) == 1:
        return parties[0][:2].upper()
    return (parties[0][0] + parties[-1][0]).upper()


def _nom_court(nom):
    """« Samira Khaldi » -> « Samira K. »"""
    parties = nom.split()
    if len(parties) <= 1:
        return nom
    return f"{parties[0]} {parties[-1][0].upper()}."


def _libelle_demande(d):
    if d.origine == Demande.Origine.VISITE:
        if d.bien_id:
            return f"Visite · {d.bien.get_type_bien_display()}"
        return "Visite"
    if d.origine == Demande.Origine.ESTIMATION:
        return "Estimation"
    return "Contact"


def dashboard_data():
    """Chiffres de la page d'accueil de l'admin (cartes, graphique 6 mois, dernières demandes)."""
    debut_mois = timezone.localdate().replace(day=1)
    biens, demandes = Bien.objects.all(), Demande.objects.all()
    avis = Avis.objects.filter(est_approuve=True)

    total = biens.count()
    publies = biens.filter(publie=True).count()
    note = avis.aggregate(m=Avg("note"))["m"]

    mois = _douze_mois()[-6:]
    valeurs = _par_mois(demandes, "recue_le", mois)
    maxi = max(valeurs)
    barres = []
    for i, (d, n) in enumerate(zip(mois, valeurs)):
        pct = max(6, round(n * 100 / maxi)) if maxi else 6
        barres.append({
            "label": MOIS_COURTS[d.month - 1],
            "n": n,
            "pct": pct,
            "courant": i == len(mois) - 1,
        })

    dernieres = []
    for d in demandes.select_related("bien")[:4]:
        dernieres.append({
            "id": d.pk,
            "initiales": _initiales(d.nom),
            "nom": _nom_court(d.nom),
            "libelle": _libelle_demande(d),
            "traitee": d.traitee,
        })

    return {
        "biens": total,
        "biens_mois": biens.filter(cree_le__date__gte=debut_mois).count(),
        "publies": publies,
        "pct_en_ligne": round(publies * 100 / total) if total else 0,
        "demandes": demandes.count(),
        "a_traiter": demandes.filter(traitee=False).count(),
        "avis": avis.count(),
        "note_moyenne": f"{note:.1f}".replace(".", ",") if note is not None else "–",
        "barres": barres,
        "dernieres": dernieres,
    }


def statistiques_view(request):
    contexte = {**admin.site.each_context(request), "title": "Statistiques", "stats": stats_data(), "kpi": True}
    return TemplateResponse(request, "admin/statistiques.html", contexte)