#!/bin/bash
# Sauvegarde quotidienne de la base et des photos (garde 14 jours).
# Installer : sudo apt install sqlite3 ; puis chmod +x et ajouter à crontab -e :
#   30 3 * * * /srv/elouabdi_immo/deploy/sauvegarde.sh
set -e
DEST=/srv/sauvegardes/$(date +%F)
mkdir -p "$DEST"
sqlite3 /srv/elouabdi_immo/db.sqlite3 ".backup '$DEST/db.sqlite3'"
tar czf "$DEST/media.tar.gz" -C /srv/elouabdi_immo media
find /srv/sauvegardes -mindepth 1 -maxdepth 1 -mtime +14 -exec rm -rf {} +
