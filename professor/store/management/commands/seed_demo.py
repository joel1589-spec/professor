from django.core.management.base import BaseCommand
from store.models import SiteSetting, Category, Book, Service

class Command(BaseCommand):
    help='Crée les contenus de démonstration'
    def handle(self,*args,**kwargs):
        SiteSetting.objects.get_or_create(id=1)
        cat,_=Category.objects.get_or_create(name='Poésie', defaults={'slug':'poesie'})
        Book.objects.get_or_create(title='Échos de confiance', defaults={
            'slug':'echos-de-confiance',
            'category':cat,
            'description':'Recueil de poèmes sur l’espérance, la résilience, l’Afrique, la femme, la jeunesse et le travail.',
            'price':2500,
            'format':'PDF',
            'is_featured':True,
            'is_active':True,
        })
        Service.objects.get_or_create(title='Correction et accompagnement pédagogique', defaults={'description':'Accompagnement pour mémoires, articles, textes littéraires et supports pédagogiques.', 'price_note':'Sur devis'})
        Service.objects.get_or_create(title='Conférence / intervention', defaults={'description':'Interventions sur la lecture, l’écriture, la culture, la jeunesse et l’éducation.', 'price_note':'Sur devis'})
        self.stdout.write(self.style.SUCCESS('Contenus créés.'))
