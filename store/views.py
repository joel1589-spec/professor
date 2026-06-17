from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, Http404
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

from .models import Book, Service, Category, Order, OrderItem
from .forms import CheckoutForm, ContactForm


# ── Panier ────────────────────────────────────────────────────────────────

def _cart(request):
    return request.session.setdefault('cart', {})

def _cart_items(request):
    cart = _cart(request); items = []; total = 0
    books = Book.objects.filter(id__in=cart.keys(), is_active=True)
    for b in books:
        qty = max(1, int(cart.get(str(b.id), 1)))
        sub = b.price * qty; total += sub
        items.append({'book': b, 'qty': qty, 'subtotal': sub})
    return items, total


# ── Pages publiques ───────────────────────────────────────────────────────

def home(request):
    featured = Book.objects.filter(is_active=True, is_featured=True)[:4]
    latest   = Book.objects.filter(is_active=True).order_by('-created_at')[:6]
    services = Service.objects.filter(is_active=True)[:4]
    return render(request, 'store/home.html', {'featured': featured, 'latest': latest, 'services': services})

def biography(request):
    return render(request, 'store/biography.html')

def books(request):
    q = request.GET.get('q', '').strip(); cat = request.GET.get('cat', '')
    qs = Book.objects.filter(is_active=True).order_by('-created_at')
    if q:   qs = qs.filter(title__icontains=q)
    if cat: qs = qs.filter(category__slug=cat)
    return render(request, 'store/books.html', {'books': qs, 'categories': Category.objects.all(), 'q': q, 'cat': cat})

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    return render(request, 'store/book_detail.html', {'book': book})

def services(request):
    return render(request, 'store/services.html', {'services': Service.objects.filter(is_active=True)})

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _cart(request); cart[str(book.id)] = cart.get(str(book.id), 0) + 1
    request.session.modified = True
    messages.success(request, 'Document ajouté au panier.')
    return redirect('cart')

def remove_from_cart(request, book_id):
    cart = _cart(request); cart.pop(str(book_id), None); request.session.modified = True
    messages.success(request, 'Document retiré du panier.')
    return redirect('cart')

def cart(request):
    items, total = _cart_items(request)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


# ── FedaPay ───────────────────────────────────────────────────────────────

def _fedapay_headers():
    return {
        'Authorization': f"Bearer {settings.FEDAPAY_SECRET_KEY}",
        'Content-Type':  'application/json',
    }

def _fedapay_base():
    env = getattr(settings, 'FEDAPAY_ENVIRONMENT', 'sandbox')
    return settings.FEDAPAY_API_BASE.get(env, settings.FEDAPAY_API_BASE['sandbox'])

def _create_fedapay_transaction(order, callback_url, return_url):
    """Crée une transaction FedaPay et retourne (payment_url, transaction_id)."""
    name_parts = order.full_name.strip().split()
    firstname  = name_parts[0]
    lastname   = ' '.join(name_parts[1:]) if len(name_parts) > 1 else name_parts[0]

    payload = {
        "description":   f"Commande #{order.id} – Estino Le Passionné",
        "amount":        order.total,
        "currency":      {"iso": "XOF"},
        "callback_url":  callback_url,   # webhook machine-to-machine (POST)
        "return_url":    return_url,     # retour navigateur client (GET)
        "customer": {
            "email":     order.email,
            "firstname": firstname,
            "lastname":  lastname,
            "phone_number": {
                "number":  order.phone.strip().replace(' ', ''),
                "country": "BJ",
            },
        },
    }

    resp = requests.post(
        f'{_fedapay_base()}/transactions',
        json=payload,
        headers=_fedapay_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    txn = data.get('v1/transaction') or data.get('transaction') or data
    txn_id = txn.get('id') or txn.get('klass_id')

    # Générer le token pour le checkout hébergé FedaPay
    token_resp = requests.post(
        f'{_fedapay_base()}/transactions/{txn_id}/token',
        headers=_fedapay_headers(),
        timeout=60,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    payment_url = token_data.get('url') or token_data.get('payment_url')
    return payment_url, txn_id


def _get_fedapay_transaction_status(txn_id):
    """
    Interroge directement l'API FedaPay pour connaître le statut réel
    d'une transaction. Retourne le statut en minuscules ou None si erreur.
    """
    try:
        resp = requests.get(
            f'{_fedapay_base()}/transactions/{txn_id}',
            headers=_fedapay_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        txn = data.get('v1/transaction') or data.get('transaction') or data
        return str(txn.get('status', '')).lower()
    except Exception:
        return None


def _extract_txn_id(order):
    """
    Extrait l'ID de transaction FedaPay depuis order.note.
    Format stocké : 'fedapay_txn_id=12345'
    """
    if not order.note:
        return None
    for part in order.note.split(';'):
        part = part.strip()
        if part.startswith('fedapay_txn_id='):
            value = part.split('=', 1)[1].strip()
            return value if value else None
    return None


# ── Checkout ──────────────────────────────────────────────────────────────

def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('books')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method', '')

            # Créer la commande (NEW pour Mobile Money, PAID pour les autres)
            status_initial = 'NEW' if payment_method == 'MOBILE_MONEY' else 'PAID'
            order = Order.objects.create(total=total, status=status_initial, **form.cleaned_data)
            for it in items:
                OrderItem.objects.create(
                    order=order, book=it['book'],
                    quantity=it['qty'], unit_price=it['book'].price,
                )

            # Mobile Money → FedaPay
            if payment_method == 'MOBILE_MONEY':
                try:
                    # callback_url  → webhook POST envoyé par FedaPay serveur-à-serveur
                    # return_url    → redirection navigateur après paiement côté client
                    callback_url = request.build_absolute_uri(
                        reverse('fedapay_callback', kwargs={'token': order.download_token})
                    )
                    return_url = request.build_absolute_uri(
                        reverse('fedapay_return', kwargs={'token': order.download_token})
                    )
                    payment_url, txn_id = _create_fedapay_transaction(order, callback_url, return_url)
                    # Stocker l'ID de transaction dans order.note
                    order.note = f'fedapay_txn_id={txn_id}'
                    order.save(update_fields=['note'])
                    request.session['cart'] = {}
                    request.session.modified = True
                    return redirect(payment_url)

                except Exception as exc:
                    order.status = 'CANCELLED'
                    order.save(update_fields=['status'])
                    messages.error(request, f'Erreur FedaPay : {exc}. Veuillez réessayer.')
                    return redirect('checkout')

            # Autres méthodes de paiement
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('checkout_success', token=order.download_token)

    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {
        'form': form, 'items': items, 'total': total,
    })


# ── CORRECTIF 1 : csrf_exempt + lecture JSON ──────────────────────────────
@csrf_exempt
def fedapay_callback(request, token):
    """
    Double rôle :
    - POST  → webhook serveur-à-serveur envoyé par FedaPay  → répond "OK"
    - GET   → FedaPay redirige parfois aussi le navigateur ici avec ?status=&id=
              → on lit les paramètres et on redirige vers la bonne page
    """
    order = get_object_or_404(Order, download_token=token)

    # ── CAS GET : navigateur redirigé ici par FedaPay ──────────────────
    if request.method == 'GET':
        # Si déjà PAID (webhook arrivé en avance), aller directement au succès
        if order.status == 'PAID':
            return redirect('checkout_success', token=order.download_token)

        # Vérifier le vrai statut via l'API FedaPay (plus fiable que le paramètre GET)
        txn_id = _extract_txn_id(order)
        api_status = _get_fedapay_transaction_status(txn_id) if txn_id else None
        # Fallback sur le paramètre GET ?status= si l'API ne répond pas
        effective_status = api_status or request.GET.get('status', '').lower()

        if effective_status in ('approved', 'completed'):
            order.status = 'PAID'
            order.save(update_fields=['status'])
            return redirect('checkout_success', token=order.download_token)
        elif effective_status in ('declined', 'cancelled'):
            if order.status != 'PAID':
                order.status = 'CANCELLED'
                order.save(update_fields=['status'])
            messages.error(request, 'Le paiement a été refusé ou annulé. Veuillez réessayer.')
            return redirect('checkout')
        else:
            # Statut ambigu / pending → page de succès (affiche l'état réel de la commande)
            return redirect('checkout_success', token=order.download_token)

    # ── CAS POST : webhook machine-à-machine ───────────────────────────
    status = ''
    try:
        body = json.loads(request.body)
        # Structure possible : {"transaction": {"status": "approved"}} ou {"status": "approved"}
        if isinstance(body, dict):
            txn = body.get('transaction') or body.get('v1/transaction') or body
            status = str(txn.get('status', '')).lower()
    except (json.JSONDecodeError, AttributeError):
        # Fallback : tenter request.POST au cas où
        status = request.POST.get('status', '').lower()

    # Si le statut du webhook n'est pas clair, interroger l'API directement
    if status not in ('approved', 'completed', 'declined', 'cancelled'):
        txn_id = _extract_txn_id(order)
        if txn_id:
            status = _get_fedapay_transaction_status(txn_id) or ''

    if status in ('approved', 'completed'):
        order.status = 'PAID'
        order.save(update_fields=['status'])
    elif status in ('declined', 'cancelled'):
        if order.status != 'PAID':  # ne pas écraser un PAID déjà enregistré
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])

    # Toujours répondre 200 pour que FedaPay sache que le webhook est reçu
    return HttpResponse('OK')


# ── CORRECTIF 2 : extraction correcte du txn_id + polling robuste ────────
def fedapay_return(request, token):
    """
    return_url : le navigateur du client arrive ici après le paiement FedaPay.
    On interroge l'API FedaPay pour connaître le vrai statut de la transaction.
    """
    order = get_object_or_404(Order, download_token=token)

    # Si la commande est déjà PAID (webhook arrivé avant le retour navigateur)
    if order.status == 'PAID':
        return redirect('checkout_success', token=order.download_token)

    # Extraire l'ID de transaction (CORRECTIF : utilise la fonction dédiée)
    txn_id = _extract_txn_id(order)

    if txn_id:
        api_status = _get_fedapay_transaction_status(txn_id)

        if api_status in ('approved', 'completed'):
            order.status = 'PAID'
            order.save(update_fields=['status'])

        elif api_status in ('declined', 'cancelled'):
            if order.status != 'PAID':
                order.status = 'CANCELLED'
                order.save(update_fields=['status'])
            messages.error(request, 'Le paiement a été refusé ou annulé. Veuillez réessayer.')
            return redirect('checkout')

        elif api_status in ('pending', 'waiting_payment', None):
            # Statut encore en attente : afficher la page de succès avec état "en attente"
            # Le webhook mettra à jour la commande en arrière-plan
            pass

    # Rediriger vers la page de succès (affichera l'état réel de la commande)
    return redirect('checkout_success', token=order.download_token)


def checkout_success(request, token):
    order = get_object_or_404(Order, download_token=token)
    return render(request, 'store/success.html', {'order': order})


def download_file(request, token, item_id):
    order = get_object_or_404(Order, download_token=token, status__in=['PAID', 'DELIVERED'])
    item  = get_object_or_404(OrderItem, id=item_id, order=order)
    if not item.book.digital_file:
        raise Http404('Fichier indisponible')
    return FileResponse(
        item.book.digital_file.open('rb'),
        as_attachment=True,
        filename=item.book.digital_file.name.split('/')[-1],
    )


# ── Contact ───────────────────────────────────────────────────────────────

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message envoyé. Nous vous répondrons rapidement.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})


def favicon(request):
    return HttpResponse(status=204)
