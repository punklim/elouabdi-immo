from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import set_language

from biens.sitemaps import SITEMAPS

admin.site.site_header = "El Ouabdi Immobilier – Administration"
admin.site.site_title = "El Ouabdi Immobilier"
admin.site.index_title = "Gestion du site"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

# Pages publiques : français sans préfixe, arabe sous /ar/
# Le changement de langue doit lui aussi être sous /ar/ pour retrouver la page équivalente en français
urlpatterns += i18n_patterns(
    path("i18n/langue/", set_language, name="set_language"),
    path("", include("biens.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
