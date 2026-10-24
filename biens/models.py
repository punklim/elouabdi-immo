import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


def _loc(obj, champ):
    """Renvoie le champ en arabe si on est sur /ar/ et qu'il est rempli, sinon en français."""
    if get_language() == "ar":
        valeur = getattr(obj, f"{champ}_ar", "")
        if valeur:
            return valeur
    return getattr(obj, champ)


class Ville(models.Model):
    nom = models.CharField("Nom", max_length=100, unique=True)
    nom_ar = models.CharField("Nom en arabe", max_length=100, blank=True, default="")
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "ville"
        verbose_name_plural = "villes"

    def __str__(self):
        return self.nom

    @property
    def nom_affiche(self):
        return _loc(self, "nom")


class Equipement(models.Model):
    nom = models.CharField("Nom", max_length=80, unique=True)
    nom_ar = models.CharField("Nom en arabe", max_length=80, blank=True, default="")

    class Meta:
        ordering = ["nom"]
        verbose_name = "équipement"
        verbose_name_plural = "équipements"

    def __str__(self):
        return self.nom

    @property
    def nom_affiche(self):
        return _loc(self, "nom")


class Agent(models.Model):
    nom = models.CharField("Nom complet", max_length=120)
    fonction = models.CharField("Fonction", max_length=120, blank=True, default="")
    bio = models.TextField("Présentation", blank=True, default="")
    telephone = models.CharField("Téléphone", max_length=30)
    whatsapp = models.CharField("WhatsApp", max_length=30, blank=True)
    email = models.EmailField("E-mail", blank=True)
    photo = models.ImageField(upload_to="agents/", blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "conseiller"
        verbose_name_plural = "conseillers"

    def __str__(self):
        return self.nom


class Bien(models.Model):
    class Transaction(models.TextChoices):
        VENTE = "vente", _("À vendre")
        LOCATION = "location", _("À louer")

    class TypeBien(models.TextChoices):
        APPARTEMENT = "appartement", _("Appartement")
        VILLA = "villa", _("Villa")
        RIAD = "riad", _("Riad")
        TERRAIN = "terrain", _("Terrain")
        LOCAL = "local", _("Local commercial")
        BUREAU = "bureau", _("Bureau")

    class Statut(models.TextChoices):
        DISPONIBLE = "disponible", _("Disponible")
        RESERVE = "reserve", _("Réservé")
        VENDU = "vendu", _("Vendu")
        LOUE = "loue", _("Loué")

    titre = models.CharField("Titre", max_length=180)
    titre_ar = models.CharField("Titre en arabe", max_length=180, blank=True, default="")
    slug = models.SlugField(unique=True)
    reference = models.CharField("Référence", max_length=30, unique=True)
    transaction = models.CharField(max_length=10, choices=Transaction.choices)
    type_bien = models.CharField("Type de bien", max_length=20, choices=TypeBien.choices)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.DISPONIBLE)
    prix = models.DecimalField("Prix (MAD)", max_digits=12, decimal_places=0,
                               help_text="Prix de vente, ou loyer mensuel pour une location.")
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT, related_name="biens")
    quartier = models.CharField(max_length=120, blank=True)
    adresse = models.CharField("Adresse / secteur", max_length=200, blank=True)
    surface = models.PositiveIntegerField("Surface (m²)")
    chambres = models.PositiveSmallIntegerField(default=0)
    salles_de_bain = models.PositiveSmallIntegerField(default=0)
    etage = models.PositiveSmallIntegerField("Étage", null=True, blank=True)
    annee_construction = models.PositiveSmallIntegerField("Année de construction", null=True, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField("Description en arabe", blank=True, default="")
    equipements = models.ManyToManyField(Equipement, blank=True, related_name="biens")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    video_url = models.URLField("Lien vidéo / visite virtuelle", blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="biens")
    a_la_une = models.BooleanField("Afficher à la une", default=False)
    publie = models.BooleanField("Publié sur le site", default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "bien"
        verbose_name_plural = "biens"

    def __str__(self):
        return f"{self.reference} – {self.titre}"

    def get_absolute_url(self):
        return reverse("bien_detail", args=[self.slug])

    @property
    def titre_affiche(self):
        return _loc(self, "titre")

    @property
    def description_affichee(self):
        return _loc(self, "description")


class PhotoBien(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="biens/")
    legende = models.CharField("Légende", max_length=120, blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]
        verbose_name = "photo"
        verbose_name_plural = "photos"


class Demande(models.Model):
    class Origine(models.TextChoices):
        CONTACT = "contact", "Contact"
        VISITE = "visite", "Demande de visite"
        ESTIMATION = "estimation", "Estimation de bien"

    origine = models.CharField(max_length=12, choices=Origine.choices, default=Origine.CONTACT)
    bien = models.ForeignKey(Bien, on_delete=models.SET_NULL, null=True, blank=True, related_name="demandes")
    nom = models.CharField(max_length=120)
    telephone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    traitee = models.BooleanField("Traitée", default=False)
    note_interne = models.TextField("Note interne", blank=True, default="")
    recue_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recue_le"]
        verbose_name = "demande client"
        verbose_name_plural = "demandes clients"

    def __str__(self):
        return f"{self.nom} – {self.get_origine_display()}"


class Article(models.Model):
    titre = models.CharField(max_length=200)
    titre_ar = models.CharField("Titre en arabe", max_length=200, blank=True, default="")
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="blog/", blank=True)
    resume = models.CharField("Résumé", max_length=300)
    resume_ar = models.CharField("Résumé en arabe", max_length=300, blank=True, default="")
    contenu = models.TextField()
    contenu_ar = models.TextField("Contenu en arabe", blank=True, default="")
    publie = models.BooleanField("Publié", default=True)
    publie_le = models.DateTimeField("Date de publication", default=timezone.now)

    class Meta:
        ordering = ["-publie_le"]
        verbose_name = "article"
        verbose_name_plural = "articles du blog"

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])

    @property
    def titre_affiche(self):
        return _loc(self, "titre")

    @property
    def resume_affiche(self):
        return _loc(self, "resume")

    @property
    def contenu_affiche(self):
        return _loc(self, "contenu")
class Alerte(models.Model):
    """Alerte e-mail : prévient le visiteur quand un nouveau bien correspond à sa recherche."""
    email = models.EmailField()
    transaction = models.CharField(max_length=10, choices=Bien.Transaction.choices, blank=True)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, null=True, blank=True)
    type_bien = models.CharField(max_length=20, choices=Bien.TypeBien.choices, blank=True)
    budget_max = models.PositiveIntegerField("Budget max (MAD)", null=True, blank=True)
    langue = models.CharField(max_length=5, default="fr")
    actif = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "alerte e-mail"
        verbose_name_plural = "alertes e-mail"

    def __str__(self):
        return self.email

    def correspond(self, bien):
        if self.transaction and bien.transaction != self.transaction:
            return False
        if self.ville_id and bien.ville_id != self.ville_id:
            return False
        if self.type_bien and bien.type_bien != self.type_bien:
            return False
        if self.budget_max and bien.prix > self.budget_max:
            return False
        return True


class Avis(models.Model):
    nom = models.CharField("Nom", max_length=100)
    ville = models.CharField("Ville", max_length=100)
    note = models.IntegerField("Note (1-5)", default=5, choices=[(i, str(i)) for i in range(1, 6)])
    commentaire = models.TextField("Commentaire")
    date_creation = models.DateTimeField("Date", auto_now_add=True)
    est_approuve = models.BooleanField("Approuvé", default=False)

    class Meta:
        verbose_name = "avis client"
        verbose_name_plural = "avis clients"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} - {self.note}/5"