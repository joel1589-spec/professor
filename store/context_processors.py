from .models import SiteSetting

def site_settings(request):
    settings = SiteSetting.objects.first()
    cart = request.session.get('cart', {})
    cart_count = sum(int(v) for v in cart.values()) if cart else 0
    return {'site': settings, 'cart_count': cart_count}
