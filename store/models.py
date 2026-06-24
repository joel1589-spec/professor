from django.db import models
from django.utils.text import slugify
import uuid

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=160, default='Estino Le Passionné')
    tagline = models.CharField(max_length=220, default='Professeur • Chercheur • Écrivain')
    phone = models.CharField(max_length=60, blank=True, default='(+228) 93 11 10 18 / 97 12 41 63')
    whatsapp = models.CharField(max_length=60, blank=True, default='+22893111018')
    email = models.EmailField(blank=True, default='leseditionstriomphetg@gmail.com')
    address = models.CharField(max_length=220, default='Lomé, Togo')
    hero_title = models.CharField(max_length=220, default='Livres, recherches et services pédagogiques')
    hero_text = models.TextField(default='Découvrez les ouvrages, recueils, documents, supports de cours et prestations intellectuelles d’un professeur, chercheur et écrivain engagé pour la connaissance.')
    biography = models.TextField(default="Estino Le Passionné, de son vrai nom AFE Komi, est né à Atakpamé. Il a obtenu sa Licence en Anglais à l’Université de Lomé. Ainsi, il est aussi professeur d’anglais et Ewé. Sa passion pour la lecture depuis le collège a mûri en lui le goût de l’écriture. Son recueil de poème “Échos de confiance” vient confirmer son génie créateur, un faiseur de la poésie. Il est aussi animateur télé, radio et gestionnaire d’un site en ligne.")
    profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    
    def __str__(self):
        return self.site_name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    def save(self, *a, **k):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*a, **k)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    FORMAT_CHOICES = [('PDF', 'PDF'), ('DOCX', 'Word'), ('BOTH', 'PDF + Word')]
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.CharField(max_length=120, default='Estino Le Passionné')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text='Prix en FCFA')
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='PDF')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    digital_file = models.FileField(upload_to='documents/', blank=True, null=True, help_text='Fichier PDF ou Word à livrer après paiement')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *a, **k):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*a, **k)
    
    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    price_note = models.CharField(max_length=120, blank=True, default='Sur devis')
    is_active = models.BooleanField(default=True)
    # 🆕 Affiche du service
    poster = models.ImageField(
        upload_to='services/posters/',
        blank=True,
        null=True,
        help_text='Affiche ou image de promotion pour ce service'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Order(models.Model):
    STATUS = [('NEW', 'Nouvelle'), ('PAID', 'Payée'), ('DELIVERED', 'Livrée'), ('CANCELLED', 'Annulée')]
    PAYMENT = [('MOBILE_MONEY', 'Mobile Money'), ('PAYPAL', 'PayPal'), ('CARD', 'Carte bancaire'), ('MANUAL', 'Paiement manuel')]
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=60)
    city = models.CharField(max_length=120, blank=True)
    payment_method = models.CharField(max_length=30, choices=PAYMENT)
    status = models.CharField(max_length=20, choices=STATUS, default='NEW')
    total = models.PositiveIntegerField(default=0)
    download_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    
    def __str__(self):
        return f'Commande #{self.id} - {self.full_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()
    
    def subtotal(self):
        return self.quantity * self.unit_price

class ContactMessage(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.subject