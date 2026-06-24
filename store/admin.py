from django.contrib import admin
from .models import SiteSetting, Category, Book, Service, Order, OrderItem, ContactMessage

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline', 'email', 'phone')
    fieldsets = (
        (None, {'fields': ('site_name', 'tagline', 'hero_title', 'hero_text', 'biography', 'profile_photo')}),
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
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'author', 'category', 'description', 'price', 'format')}),
        ('Fichiers', {'fields': ('cover', 'digital_file')}),
        ('Publication', {'fields': ('is_featured', 'is_active')}),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_note', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    # 🆕 Ajout du champ poster dans l'admin
    fieldsets = (
        (None, {'fields': ('title', 'description', 'price_note')}),
        ('Affiche / Image', {'fields': ('poster',)}),
        ('Publication', {'fields': ('is_active',)}),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'quantity', 'unit_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'payment_method', 'status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('download_token', 'created_at')
    inlines = [OrderItemInline]

@admin.action(description="Marquer comme lu")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)

@admin.action(description="Marquer comme non lu")
def mark_as_unread(modeladmin, request, queryset):
    queryset.update(is_read=False)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    actions = [mark_as_read, mark_as_unread]
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    fields = ('is_read', 'name', 'email', 'subject', 'message', 'created_at')