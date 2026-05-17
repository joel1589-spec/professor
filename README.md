# Site Professeur / Chercheur / Écrivain

## Installation locale
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Admin : `/admin-pro/`

## Important
- Le public n’a pas besoin de créer un compte.
- Les livres/documents se gèrent dans l’administration : titre, prix, couverture, fichier PDF/Word.
- La photo du professeur se met dans `Site setting > profile_photo`.
- Le paiement est en mode démo pour déploiement rapide. Remplacer les clés dans `professor_market/settings.py`.

## Si tu avais déjà lancé une ancienne version
Supprime `db.sqlite3`, puis relance :
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```
