from django import forms
from .models import ContactMessage
class CheckoutForm(forms.Form):
    full_name=forms.CharField(label='Nom complet', max_length=160)
    email=forms.EmailField(label='Adresse email')
    phone=forms.CharField(label='Téléphone / WhatsApp', max_length=60)
    city=forms.CharField(label='Ville', max_length=120, required=False)
    payment_method=forms.ChoiceField(label='Mode de paiement', choices=[('MOBILE_MONEY','Mobile Money'),('PAYPAL','PayPal'),('CARD','Carte bancaire'),('MANUAL','Paiement manuel')])
    note=forms.CharField(label='Note', widget=forms.Textarea, required=False)
class ContactForm(forms.ModelForm):
    class Meta:
        model=ContactMessage
        fields=['name','email','subject','message']
        labels={'name':'Nom','email':'Email','subject':'Sujet','message':'Message'}
