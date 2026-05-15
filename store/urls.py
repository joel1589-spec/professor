from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('biographie/', views.biography, name='biography'),
    path('livres/', views.books, name='books'),
    path('livres/<slug:slug>/', views.book_detail, name='book_detail'),
    path('services/', views.services, name='services'),
    path('panier/', views.cart, name='cart'),
    path('panier/ajouter/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/retirer/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('commande/', views.checkout, name='checkout'),
    path('commande/succes/<uuid:token>/', views.checkout_success, name='checkout_success'),
    path('commande/fedapay-callback/<uuid:token>/', views.fedapay_callback, name='fedapay_callback'),
    path('commande/fedapay-retour/<uuid:token>/', views.fedapay_return, name='fedapay_return'),
    path('telechargement/<uuid:token>/<int:item_id>/', views.download_file, name='download_file'),
    path('contact/', views.contact, name='contact'),
    path('favicon.ico', views.favicon, name='favicon'),
]
