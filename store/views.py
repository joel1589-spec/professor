import json
import requests
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import CheckoutForm, ContactForm
from .models import Book, Category, Order, OrderItem, Service


def _cart(request):
    return request.session.setdefault('cart', {})


def _cart_items(request):
    cart = _cart(request)
    ids = [int(k) for k in cart.keys() if str(k).isdigit()]
    books = Book.objects.filter(id__in=ids, is_active=True)
    items, total = [], 0
    for book in books:
        qty = max(1, int(cart.get(str(book.id), 1)))
        subtotal = book.price * qty
        total += subtotal
        items.append({'book': book, 'qty': qty, 'subtotal': subtotal})
    return items, total


def home(request):
    featured = Book.objects.filter(is_active=True, is_featured=True)[:4]
    latest = Book.objects.filter(is_active=True)[:6]
    services = Service.objects.filter(is_active=True)[:4]
    return render(request, 'store/home.html', {'featured': featured, 'latest': latest, 'services': services})


def biography(request):
    return render(request, 'store/biography.html')


def books(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '').strip()
    qs = Book.objects.filter(is_active=True)
    if q:
        qs = qs.filter(title__icontains=q)
    if cat:
        qs = qs.filter(category__slug=cat)
    return render(request, 'store/books.html', {'books': qs, 'categories': Category.objects.all(), 'q': q, 'cat': cat})


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    return render(request, 'store/book_detail.html', {'book': book})


def services(request):
    return render(request, 'store/services.html', {'services': Service.objects.filter(is_active=True)})


@require_POST
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_active=True)
    cart = _cart(request)
    cart[str(book.id)] = int(cart.get(str(book.id), 0)) + 1
    request.session.modified = True
    messages.success(request, 'Document ajouté au panier.')
    return redirect('cart')


def remove_from_cart(request, book_id):
    cart = _cart(request)
    cart.pop(str(book_id), None)
    request.session.modified = True
    messages.success(request, 'Document retiré du panier.')
    return redirect('cart')


def cart(request):
    items, total = _cart_items(request)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


def _fedapay_headers():
    if not settings.FEDAPAY_SECRET_KEY:
        raise RuntimeError('FEDAPAY_SECRET_KEY n’est pas configurée sur Render.')
    return {'Authorization': f'Bearer {settings.FEDAPAY_SECRET_KEY}', 'Content-Type': 'application/json'}


def _fedapay_base():
    return settings.FEDAPAY_API_BASE.get(settings.FEDAPAY_ENVIRONMENT, settings.FEDAPAY_API_BASE['sandbox'])


def _create_fedapay_transaction(order, callback_url, return_url):
    parts = order.full_name.strip().split()
    firstname = parts[0] if parts else 'Client'
    lastname = ' '.join(parts[1:]) if len(parts) > 1 else firstname
    phone = order.phone.replace(' ', '').replace('+', '')

    payload = {
        'description': f'Commande #{order.id} - Professor Market',
        'amount': order.total,
        'currency': {'iso': 'XOF'},
        'callback_url': callback_url,
        'return_url': return_url,
        'customer': {
            'email': order.email,
            'firstname': firstname,
            'lastname': lastname,
            'phone_number': {'number': phone, 'country': 'TG'},
        },
    }
    response = requests.post(f'{_fedapay_base()}/transactions', json=payload, headers=_fedapay_headers(), timeout=45)
    response.raise_for_status()
    data = response.json()
    txn = data.get('v1/transaction') or data.get('transaction') or data
    txn_id = txn.get('id') or txn.get('klass_id')
    if not txn_id:
        raise RuntimeError('Transaction FedaPay créée, mais ID introuvable.')

    token_response = requests.post(f'{_fedapay_base()}/transactions/{txn_id}/token', headers=_fedapay_headers(), timeout=45)
    token_response.raise_for_status()
    token_data = token_response.json()
    payment_url = token_data.get('url') or token_data.get('payment_url')
    if not payment_url:
        raise RuntimeError('URL de paiement FedaPay introuvable.')
    return payment_url, str(txn_id)


def _get_fedapay_transaction_status(txn_id):
    if not txn_id:
        return None
    try:
        response = requests.get(f'{_fedapay_base()}/transactions/{txn_id}', headers=_fedapay_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        txn = data.get('v1/transaction') or data.get('transaction') or data
        return str(txn.get('status', '')).lower()
    except Exception:
        return None


def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('books')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            status = 'NEW'
            order = Order.objects.create(total=total, status=status, **form.cleaned_data)
            for item in items:
                OrderItem.objects.create(order=order, book=item['book'], quantity=item['qty'], unit_price=item['book'].price)

            request.session['cart'] = {}
            request.session.modified = True

            if payment_method == 'MOBILE_MONEY':
                try:
                    callback_url = request.build_absolute_uri(reverse('fedapay_callback', kwargs={'token': order.download_token}))
                    return_url = request.build_absolute_uri(reverse('fedapay_return', kwargs={'token': order.download_token}))
                    payment_url, txn_id = _create_fedapay_transaction(order, callback_url, return_url)
                    order.payment_reference = txn_id
                    order.save(update_fields=['payment_reference'])
                    return redirect(payment_url)
                except Exception as exc:
                    messages.error(request, f'Paiement indisponible : {exc}')
                    return redirect('checkout_success', token=order.download_token)

            messages.success(request, 'Commande enregistrée. Le vendeur vous contactera pour le paiement manuel.')
            return redirect('checkout_success', token=order.download_token)
    else:
        form = CheckoutForm()

    return render(request, 'store/checkout.html', {'form': form, 'items': items, 'total': total})


@csrf_exempt
def fedapay_callback(request, token):
    order = get_object_or_404(Order, download_token=token)
    status = ''
    if request.method == 'POST':
        try:
            body = json.loads(request.body or b'{}')
            txn = body.get('transaction') or body.get('v1/transaction') or body
            status = str(txn.get('status', '')).lower()
        except Exception:
            status = request.POST.get('status', '').lower()
    else:
        status = request.GET.get('status', '').lower()

    if status not in ('approved', 'completed', 'declined', 'cancelled'):
        status = _get_fedapay_transaction_status(order.payment_reference) or ''

    if status in ('approved', 'completed'):
        order.status = 'PAID'
        order.save(update_fields=['status'])
    elif status in ('declined', 'cancelled') and order.status != 'PAID':
        order.status = 'CANCELLED'
        order.save(update_fields=['status'])

    if request.method == 'GET':
        return redirect('checkout_success', token=order.download_token)
    return HttpResponse('OK')


def fedapay_return(request, token):
    order = get_object_or_404(Order, download_token=token)
    if order.status != 'PAID':
        status = _get_fedapay_transaction_status(order.payment_reference)
        if status in ('approved', 'completed'):
            order.status = 'PAID'
            order.save(update_fields=['status'])
        elif status in ('declined', 'cancelled'):
            order.status = 'CANCELLED'
            order.save(update_fields=['status'])
    return redirect('checkout_success', token=order.download_token)


def checkout_success(request, token):
    order = get_object_or_404(Order, download_token=token)
    return render(request, 'store/success.html', {'order': order})


def download_file(request, token, item_id):
    order = get_object_or_404(Order, download_token=token, status__in=['PAID', 'DELIVERED'])
    item = get_object_or_404(OrderItem, id=item_id, order=order)
    if not item.book.digital_file:
        raise Http404('Fichier indisponible')
    return FileResponse(item.book.digital_file.open('rb'), as_attachment=True, filename=item.book.digital_file.name.split('/')[-1])


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
