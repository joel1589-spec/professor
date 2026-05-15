# Professor Market - Django Render Ready

Site vitrine + boutique digitale pour un professeur/écrivain.

## Déploiement Render

Build Command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_demo
```

Start Command:
```bash
gunicorn professor_market.wsgi:application
```

Variables Render:
```env
SECRET_KEY=auto-generated
DEBUG=False
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
FEDAPAY_SECRET_KEY=...
FEDAPAY_PUBLIC_KEY=...
FEDAPAY_ENVIRONMENT=sandbox
```

Admin: `/admin-pro/`

Créer un superuser localement:
```bash
python manage.py createsuperuser
```
