# Déploiement Render

## Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

## Start Command
```bash
gunicorn professor_market.wsgi:application
```

## Variables Render
```env
DEBUG=0
SECRET_KEY=une-cle-longue-et-secrete
ALLOWED_HOSTS=.onrender.com
FEDAPAY_SECRET_KEY=
FEDAPAY_PUBLIC_KEY=
FEDAPAY_ENVIRONMENT=sandbox
```

Pour la production réelle, ajoute une base PostgreSQL sur Render puis lie `DATABASE_URL`.
