from django.core.management.base import BaseCommand
from django.utils.text import slugify

from biens.models import Agent, Article, Bien, Equipement, Ville

VILLES_AR = {"Casablanca": "الدار البيضاء", "Rabat": "الرباط", "Marrakech": "مراكش", "Tanger": "طنجة", "Agadir": "أكادير"}
EQUIPEMENTS = [("Ascenseur", "مصعد"), ("Parking", "موقف سيارات"), ("Balcon", "شرفة"),
               ("Climatisation", "تكييف"), ("Cuisine équipée", "مطبخ مجهز"), ("Sécurité 24h/24", "حراسة على مدار الساعة")]
TYPES_AR = {"appartement": "شقة", "villa": "فيلا", "terrain": "أرض", "bureau": "مكتب"}

BIENS = [
    ("DEMO-001", "Appartement 3 pièces", "vente", "appartement", 1450000, "Casablanca", "Maârif", 98, 2, 2, 3, True),
    ("DEMO-002", "Villa avec jardin", "location", "villa", 22000, "Marrakech", "Palmeraie", 320, 4, 3, None, True),
    ("DEMO-003", "Terrain constructible", "vente", "terrain", 2200000, "Rabat", "Souissi", 500, 0, 0, None, True),
    ("DEMO-004", "Appartement standing", "location", "appartement", 8500, "Casablanca", "Gauthier", 85, 2, 1, 5, False),
    ("DEMO-005", "Bureau open space", "location", "bureau", 12000, "Tanger", "Centre-ville", 120, 0, 1, 2, False),
    ("DEMO-006", "Villa moderne", "vente", "villa", 5200000, "Agadir", "Founty", 400, 5, 4, None, False),
]

ARTICLES = [
    ("demo-conseils-achat", "5 conseils avant d’acheter un appartement",
     "نصائح قبل شراء شقة",
     "Les points essentiels à vérifier avant de vous engager.",
     "النقاط الأساسية التي يجب التحقق منها قبل الالتزام.",
     "1. Définissez votre budget en incluant les frais annexes.\n\n2. Visitez le bien plusieurs fois, à des heures différentes.\n\n3. Vérifiez les documents du bien avec un professionnel.\n\n4. Comparez les prix du quartier.\n\n5. Simulez votre crédit pour connaître votre mensualité.\n\n(Article de démonstration : remplacez-le depuis l’administration.)",
     "١. حدّد ميزانيتك مع احتساب المصاريف الإضافية.\n\n٢. زر العقار عدة مرات وفي أوقات مختلفة.\n\n٣. تحقّق من وثائق العقار مع مختص.\n\n٤. قارن الأسعار في الحي.\n\n٥. احسب قرضك لمعرفة القسط الشهري.\n\n(مقال تجريبي: يمكنك استبداله من لوحة الإدارة.)"),
    ("demo-preparer-location", "Louer son bien : bien se préparer",
     "تأجير عقارك: كيف تستعد جيدًا",
     "Quelques conseils pour mettre votre bien en location sereinement.",
     "بعض النصائح لتأجير عقارك بكل اطمئنان.",
     "Un bien propre, bien photographié et au juste prix se loue plus vite. Rassemblez vos documents, faites estimer le loyer et confiez la gestion des visites à un professionnel.\n\n(Article de démonstration : remplacez-le depuis l’administration.)",
     "العقار النظيف، الجيد التصوير والمعروض بسعر مناسب يُؤجَّر أسرع. اجمع وثائقك، واطلب تقدير الكراء، وأوكل تنظيم الزيارات إلى مختص.\n\n(مقال تجريبي: يمكنك استبداله من لوحة الإدارة.)"),
]


class Command(BaseCommand):
    help = "Crée des biens et articles de démonstration (références DEMO-xxx). Option --vider pour les supprimer."

    def add_arguments(self, parser):
        parser.add_argument("--vider", action="store_true", help="Supprime les données de démonstration")

    def handle(self, *args, **opts):
        if opts["vider"]:
            n1, _ = Bien.objects.filter(reference__startswith="DEMO-").delete()
            n2, _ = Article.objects.filter(slug__startswith="demo-").delete()
            Agent.objects.filter(nom="Conseiller démo").delete()
            self.stdout.write(f"{n1 + n2} objet(s) supprimé(s).")
            return
        equip = [Equipement.objects.get_or_create(nom=n, defaults={"nom_ar": a})[0] for n, a in EQUIPEMENTS]
        agent, _ = Agent.objects.get_or_create(nom="Conseiller démo", defaults={
            "telephone": "+212 6 00 00 00 00", "fonction": "Conseiller immobilier",
            "bio": "Présentation du conseiller à rédiger depuis l’administration."})
        for ref, titre, trans, typ, prix, ville, quartier, surf, ch, sdb, etage, une in BIENS:
            v, _ = Ville.objects.get_or_create(nom=ville, defaults={"slug": slugify(ville), "nom_ar": VILLES_AR[ville]})
            bien, created = Bien.objects.get_or_create(reference=ref, defaults=dict(
                titre=f"{titre} – {quartier}", titre_ar=f"{TYPES_AR[typ]} – {quartier}",
                slug=slugify(f"{titre}-{quartier}-{ref}"),
                transaction=trans, type_bien=typ, prix=prix, ville=v, quartier=quartier,
                surface=surf, chambres=ch, salles_de_bain=sdb, etage=etage, a_la_une=une, agent=agent,
                description="Bien de démonstration : remplacez-le par vos vraies annonces depuis l'administration.",
                description_ar="عقار تجريبي: استبدله بإعلاناتك الحقيقية من لوحة الإدارة.",
            ))
            if created:
                bien.equipements.set(equip[:4])
        for slug, t, t_ar, r, r_ar, c, c_ar in ARTICLES:
            Article.objects.get_or_create(slug=slug, defaults=dict(
                titre=t, titre_ar=t_ar, resume=r, resume_ar=r_ar, contenu=c, contenu_ar=c_ar))
        self.stdout.write(self.style.SUCCESS("Données de démonstration créées."))
