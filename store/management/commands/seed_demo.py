from django.core.management.base import BaseCommand
from store.models import SiteSetting, Category, Book, Service


class Command(BaseCommand):
    help = 'Crée les données de démonstration si la base est vide.'

    def handle(self, *args, **options):
        SiteSetting.objects.get_or_create(id=1)
        cat_books, _ = Category.objects.get_or_create(name='Livres', defaults={'slug': 'livres'})
        cat_docs, _ = Category.objects.get_or_create(name='Supports de cours', defaults={'slug': 'supports-de-cours'})
        samples = [
            ('Échos de confiance', cat_books, 2500, 'Un recueil inspirant autour de la confiance, de la parole et de la persévérance.'),
            ('Guide pédagogique', cat_docs, 3000, 'Un document pratique pour accompagner les apprenants dans leur progression.'),
            ('Poésie et transmission', cat_books, 2000, 'Textes littéraires et réflexions sur la transmission du savoir.'),
        ]
        for title, category, price, description in samples:
            Book.objects.get_or_create(title=title, defaults={'category': category, 'price': price, 'description': description, 'is_featured': True})
        services = [
            ('Correction et relecture', 'Correction professionnelle de documents, mémoires, articles et manuscrits.', 'Sur devis'),
            ('Cours particuliers', 'Accompagnement pédagogique personnalisé selon le niveau de l’apprenant.', 'À partir de 5 000 FCFA'),
            ('Conférences et ateliers', 'Interventions éducatives, littéraires et culturelles pour écoles ou organisations.', 'Sur devis'),
        ]
        for title, description, price_note in services:
            Service.objects.get_or_create(title=title, defaults={'description': description, 'price_note': price_note})
        self.stdout.write(self.style.SUCCESS('Données de démonstration prêtes.'))
