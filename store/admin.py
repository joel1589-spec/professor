from django.contrib import admin
from .models import SiteSetting, Category, Book, Service, Order, OrderItem, ContactMessage


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline', 'email', 'phone')
    fieldsets = (
        ('Identité', {'fields': ('site_name', 'tagline', 'hero_title', 'hero_text', 'biography', 'profile_photo')}),
        ('Contacts', {'fields': ('phone', 'whatsapp', 'email', 'address')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'format', 'is_featured', 'is_active', 'created_at')
    list_filter = ('format', 'is_featured', 'is_active', 'category')
    search_fields = ('title', 'author', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_note', 'is_active')
    search_fields = ('title', 'description')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'quantity', 'unit_price', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'payment_method', 'status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'payment_reference')
    readonly_fields = ('download_token', 'created_at')
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
