from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, NewsletterSubscriber
# boutique/admin.py
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = "Elegant Boutique Admin"
    site_title = "Boutique Admin Portal"
    index_title = "Welcome to the Admin Dashboard"

my_admin_site = MyAdminSite(name='myadmin')

# Register your models on my_admin_site instead of admin.site
my_admin_site.register(Category)
my_admin_site.register(Product)
my_admin_site.register(Customer)
my_admin_site.register(Order)
my_admin_site.register(OrderItem)
my_admin_site.register(NewsletterSubscriber)

# -------------------------------
# CATEGORY ADMIN
# -------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


# -------------------------------
# PRODUCT ADMIN
# -------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'on_sale', 'created_at']
    list_filter = ['category', 'on_sale', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'on_sale']
    readonly_fields = ['created_at', 'updated_at']


# -------------------------------
# CUSTOMER ADMIN
# -------------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'email_verified', 'newsletter_subscribed']
    search_fields = ['user__username', 'user__email', 'phone']


# -------------------------------
# ORDER ADMIN
# -------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_date', 'status', 'total_amount']
    list_filter = ['status', 'order_date']
    search_fields = ['customer__user__username', 'id']


# -------------------------------
# ORDER ITEM ADMIN
# -------------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']


# -------------------------------
# NEWSLETTER SUBSCRIBER ADMIN
# -------------------------------
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
