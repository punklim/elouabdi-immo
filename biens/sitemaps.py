from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, Bien


class PagesSitemap(Sitemap):
    i18n = True
    alternates = True

    def items(self):
        return ["accueil", "liste", "estimation", "contact", "agents", "blog", "a_propos", "simulateur", "mentions_legales", "confidentialite"]

    def location(self, item):
        return reverse(item)


class BienSitemap(Sitemap):
    i18n = True
    alternates = True

    def items(self):
        return Bien.objects.filter(publie=True)

    def lastmod(self, obj):
        return obj.modifie_le


class ArticleSitemap(Sitemap):
    i18n = True
    alternates = True

    def items(self):
        return Article.objects.filter(publie=True)

    def lastmod(self, obj):
        return obj.publie_le


SITEMAPS = {"pages": PagesSitemap, "biens": BienSitemap, "blog": ArticleSitemap}
