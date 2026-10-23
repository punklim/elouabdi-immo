from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .alertes import envoyer_confirmation
from .forms import AlerteForm, DemandeForm
from .models import Agent, Alerte, Article, Bien, Demande, Ville, Avis


def _publies():
    return Bien.objects.filter(publie=True).select_related("ville", "agent").prefetch_related("photos")


def _articles():
    return Article.objects.filter(publie=True, publie_le__lte=timezone.now())


def _notifier(demande):
    """Prévient l'agence (en français) à chaque nouvelle demande."""
    corps = (
        f"Type : {demande.get_origine_display()}\n"
        f"Nom : {demande.nom}\nTéléphone : {demande.telephone}\nE-mail : {demande.email}\n"
        f"Bien : {demande.bien or '-'}\n\n{demande.message}"
    )
    send_mail(f"Nouvelle demande : {demande.get_origine_display()}", corps, None,
              [settings.AGENCE["email"]], fail_silently=True)


def _formulaire(request, template, origine, succes):
    form = DemandeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        demande = form.save(commit=False)
        demande.origine = origine
        demande.save()
        _notifier(demande)
        messages.success(request, succes)
        return redirect(request.path)
    return render(request, template, {"form": form})


def accueil(request):
    base = _publies()
    a_la_une = list(base.filter(a_la_une=True)[:3]) or list(base[:3])
    categories = [
        {"code": code, "label": label, "total": base.filter(type_bien=code).count()}
        for code, label in Bien.TypeBien.choices
    ]
    avis_approuves = Avis.objects.filter(est_approuve=True)[:6]
    
    return render(request, "accueil.html", {
        "a_la_une": a_la_une,
        "categories": categories,
        "articles": _articles()[:3],
        "villes": Ville.objects.all(),
        "types": Bien.TypeBien.choices,
        "sel": {"transaction": "vente"},
        "avis": avis_approuves,
    })


def liste(request):
    p = request.GET
    qs = _publies()
    if p.get("transaction") in dict(Bien.Transaction.choices):
        qs = qs.filter(transaction=p["transaction"])
    ville_obj = Ville.objects.filter(slug=p["ville"]).first() if p.get("ville") else None
    if ville_obj:
        qs = qs.filter(ville=ville_obj)
    if p.get("type") in dict(Bien.TypeBien.choices):
        qs = qs.filter(type_bien=p["type"])
    if p.get("budget", "").isdigit():
        qs = qs.filter(prix__lte=int(p["budget"]))
    if p.get("chambres", "").isdigit():
        qs = qs.filter(chambres__gte=int(p["chambres"]))
    qs = qs.order_by({"prix": "prix", "-prix": "-prix"}.get(p.get("tri"), "-cree_le"))
    page = Paginator(qs, 9).get_page(p.get("page"))
    params = p.copy()
    params.pop("page", None)
    return render(request, "liste.html", {
        "page": page,
        "total": page.paginator.count,
        "params": params.urlencode(),
        "villes": Ville.objects.all(),
        "ville_obj": ville_obj,
        "types": Bien.TypeBien.choices,
        "sel": p,
    })


def bien_detail(request, slug):
    bien = get_object_or_404(_publies(), slug=slug)
    form = DemandeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        demande = form.save(commit=False)
        demande.origine = Demande.Origine.VISITE
        demande.bien = bien
        demande.save()
        _notifier(demande)
        messages.success(request, _("Merci ! Votre demande a bien été envoyée, nous vous rappelons très vite."))
        return redirect(bien)
    carte = None
    if bien.latitude and bien.longitude:
        lat, lng = float(bien.latitude), float(bien.longitude)
        carte = (f"https://www.openstreetmap.org/export/embed.html?bbox={lng-0.008},{lat-0.005},"
                 f"{lng+0.008},{lat+0.005}&layer=mapnik&marker={lat},{lng}")
    similaires = (_publies().filter(transaction=bien.transaction, type_bien=bien.type_bien)
                  .exclude(pk=bien.pk)[:3])
    return render(request, "detail.html", {"bien": bien, "form": form, "carte": carte, "similaires": similaires})


def estimation(request):
    return _formulaire(request, "estimation.html", Demande.Origine.ESTIMATION,
                       _("Merci ! Nous vous contactons rapidement pour estimer votre bien."))


def contact(request):
    return _formulaire(request, "contact.html", Demande.Origine.CONTACT,
                       _("Merci ! Votre message a bien été envoyé."))


def a_propos(request):
    return render(request, "a_propos.html")


def agents(request):
    equipe = Agent.objects.filter(actif=True).annotate(nb=Count("biens", filter=Q(biens__publie=True)))
    return render(request, "agents.html", {"equipe": equipe})


def blog_liste(request):
    page = Paginator(_articles(), 6).get_page(request.GET.get("page"))
    return render(request, "blog_liste.html", {"page": page})


def blog_detail(request, slug):
    return render(request, "blog_detail.html", {"article": get_object_or_404(_articles(), slug=slug)})


def simulateur(request):
    prix = request.GET.get("prix", "")
    return render(request, "simulateur.html", {"prix": prix if prix.isdigit() else ""})


@require_POST
def alerte_creer(request):
    suite = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(suite, allowed_hosts={request.get_host()}):
        suite = "/"
    form = AlerteForm(request.POST)
    if form.is_valid():
        alerte = form.save(commit=False)
        alerte.langue = get_language() or "fr"
        alerte.save()
        envoyer_confirmation(alerte)
        messages.success(request, _("Alerte activée ! Vous recevrez un e-mail dès qu’un nouveau bien correspond à votre recherche."))
    else:
        messages.error(request, _("Impossible d’activer l’alerte : vérifiez votre adresse e-mail."))
    return redirect(suite)


def alerte_supprimer(request, token):
    alerte = get_object_or_404(Alerte, token=token)
    alerte.actif = False
    alerte.save(update_fields=["actif"])
    messages.success(request, _("Vous êtes désinscrit(e) : vous ne recevrez plus d’e-mails pour cette alerte."))
    return redirect("accueil")


def mentions_legales(request):
    return render(request, "mentions_legales.html")


def confidentialite(request):
    return render(request, "confidentialite.html")


# --- Favoris ---
@require_POST
def toggle_favori(request, bien_id):
    favoris = request.session.get('favoris', [])
    if bien_id in favoris:
        favoris.remove(bien_id)
        action = "retiré"
    else:
        favoris.append(bien_id)
        action = "ajouté"
    request.session['favoris'] = favoris
    return JsonResponse({"status": "ok", "action": action, "count": len(favoris)})


def mes_favoris(request):
    favoris_ids = request.session.get('favoris', [])
    biens = Bien.objects.filter(id__in=favoris_ids, publie=True)
    return render(request, 'favoris.html', {'biens': biens})

def ville_detail(request, slug):
    ville = get_object_or_404(Ville, slug=slug)
    biens = _publies().filter(ville=ville)
    return render(request, 'ville_detail.html', {'ville': ville, 'biens': biens})