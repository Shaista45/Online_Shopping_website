from django.urls import path, include
from . import views
from boutique.admin import my_admin_site 

urlpatterns = [
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.profile, name='profile'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('debug/cart/', views.debug_cart, name='debug_cart'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/products/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin/products/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin/categories/add/', views.admin_add_category, name='admin_add_category'),
    path('admin/categories/edit/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),
    path('admin/categories/delete/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/categories/', views.admin_view_categories, name='admin_view_categories'),
    path('admin/customers/', views.admin_view_customers, name='admin_view_customers'),
    path("admin/customers/", views.view_customers, name="view_customers"),
    path('admin/customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Only include the Django admin if you want it at /django-admin/
    # path("django-admin/", my_admin_site.urls),
    path('admin/newsletter/send/', views.admin_send_newsletter, name='admin_send_newsletter'),
    
    # API endpoints
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/cart/count/', views.api_cart_count, name='api_cart_count'),
]