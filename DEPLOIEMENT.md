# Mise en ligne du site (serveur Ubuntu + nom de domaine + HTTPS)

Guide pour un serveur privé virtuel (VPS) Ubuntu 22.04 ou 24.04. Remplacez `monsite.ma` par votre domaine.

## 0. Ce qu'il faut avoir
- Un VPS Ubuntu avec accès SSH, et son adresse IP.
- Un nom de domaine (.ma ou autre) acheté chez un bureau d'enregistrement.
- Un compte e-mail d'envoi (SMTP) : celui de l'hébergeur de messagerie du domaine, ou un service d'envoi.

## 1. Domaine (DNS)
Chez le bureau d'enregistrement, créer deux enregistrements de type **A** : `monsite.ma` et `www.monsite.ma`, vers l'IP du serveur. La propagation peut prendre de quelques minutes à quelques heures.

## 2. Préparer le serveur
```
sudo apt update && sudo apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx sqlite3
sudo mkdir -p /srv/elouabdi_immo
```
Envoyer le projet dans `/srv/elouabdi_immo` (git, `scp` ou `rsync`), **sans** le dossier `.venv`.

## 3. Installer le projet
```
cd /srv/elouabdi_immo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env        # remplir TOUTES les valeurs (voir .env.example)
```
Puis, en chargeant le fichier `.env` :
```
set -a; source .env; set +a
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py createsuperuser
sudo chown -R www-data:www-data /srv/elouabdi_immo
```
Ne lancez pas `charger_demo` en production.

## 4. Lancer le site (Gunicorn)
```
sudo cp deploy/gunicorn.service /etc/systemd/system/elouabdi.service
sudo systemctl daemon-reload && sudo systemctl enable --now elouabdi
sudo systemctl status elouabdi            # doit afficher "active (running)"
```

## 5. Nginx puis HTTPS
```
sudo cp deploy/nginx.conf /etc/nginx/sites-available/elouabdi   # remplacer monsite.ma dans le fichier
sudo ln -s /etc/nginx/sites-available/elouabdi /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d monsite.ma -d www.monsite.ma
```
Certbot installe le certificat HTTPS et le renouvelle automatiquement. Ouvrez ensuite `https://monsite.ma`.

## 6. E-mails
Les variables `EMAIL_*` du fichier `.env` activent l'envoi réel (demandes des clients, alertes e-mail). Après modification : `sudo systemctl restart elouabdi`.
Test : envoyer une demande depuis la page Contact et vérifier la réception à l'adresse `email` de `config/agence.py`. Pour éviter les spams, configurez SPF et DKIM chez votre fournisseur d'e-mail.

## 7. Sauvegardes
Copier `deploy/sauvegarde.sh`, le rendre exécutable et l'ajouter au `crontab -e` (instructions dans le fichier). Pensez aussi à copier régulièrement `/srv/sauvegardes` hors du serveur.

## 8. Mettre à jour le site plus tard
```
cd /srv/elouabdi_immo && set -a; source .env; set +a
# (envoyer les nouveaux fichiers)
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart elouabdi
```

## 9. Liste de contrôle avant le lancement
- [ ] `config/agence.py` complété (téléphone, WhatsApp, e-mail, adresse).
- [ ] Vraies annonces et vraies photos ajoutées dans l'administration ; biens de démonstration supprimés.
- [ ] Textes de l'accueil, de « À propos » et des conseillers relus.
- [ ] Mentions légales et politique de confidentialité rédigées et validées (identité de l'agence, numéros d'inscription, protection des données personnelles).
- [ ] Formulaires et alertes testés de bout en bout, en français et en arabe.
- [ ] Site déclaré dans Google Search Console (envoyer `https://monsite.ma/sitemap.xml`) et fiche Google Business Profile créée.
- [ ] Mot de passe administrateur solide ; `DJANGO_DEBUG=0`.
