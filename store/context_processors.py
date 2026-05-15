from .models import SiteSetting


def site_settings(request):
    site = SiteSetting.objects.first()
    cart = request.session.get('cart', {}) if hasattr(request, 'session') else {}
    cart_count = sum(int(qty) for qty in cart.values()) if cart else 0
    return {'site': site, 'cart_count': cart_count}
