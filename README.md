# El Ouabdi Immobilier – site web (Django)

## Lancer en local
    python -m venv .venv
    .venv\Scripts\activate          (Windows)   |   source .venv/bin/activate (Mac/Linux)
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py charger_demo   (facultatif : données de démonstration ; --vider pour les supprimer)
    python manage.py runserver

- Site : http://127.0.0.1:8000/  (arabe : /ar/)
- Administration : http://127.0.0.1:8000/admin/

## Où modifier quoi
- Infos de l'agence (nom, téléphone, WhatsApp, e-mail, adresse) : `config/agence.py`
- Couleurs et styles : `static/css/site.css` (variables en haut)
- Pages : dossier `templates/`
- Traductions arabes : `locale/ar/LC_MESSAGES/django.po` (puis `python manage.py compilemessages`, qui demande l'outil gettext)
- Mise en ligne : `DEPLOIEMENT.md`
