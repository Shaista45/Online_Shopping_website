# shaista45/online_shopping_website/Online_Shopping_website-138fd2c2a9d203638ceba42d49eb07cdb4f95a2d/boutique/views.py

from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from .models import Product, Category, Customer, Order, OrderItem, NewsletterSubscriber
from .forms import ProductForm, NewsletterForm, UserRegisterForm, UserUpdateForm, CustomerUpdateForm, UserLoginForm, CategoryForm
from .mongodb_utils import (
    add_to_wishlist_mongo, get_wishlist_mongo, remove_from_wishlist_mongo,
    add_to_cart_mongo, get_cart_mongo, get_cart_count_mongo,
    update_cart_quantity_mongo, remove_from_cart_mongo, clear_cart_mongo
)
import json
from datetime import datetime

def is_admin(user):
    return user.is_staff
 

from django.shortcuts import render
from .models import Product, Category


def product_list(request):
    # Get filters from request
    search_query = request.GET.get('search', '')
    # selected_category = request.GET.get('category', '')
    selected_category = request.GET.get('category')
    selected_price = request.GET.get('price', '')
    sort_by = request.GET.get('sort', '')
    on_sale = request.GET.get('on_sale', '')

    # Start with all products
    products = Product.objects.all()

    # Apply search filter
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Apply category filter
    if selected_category:
        products = products.filter(category_id=selected_category)

    # Apply price filter
    if selected_price:
        if '-' in selected_price:
            min_price, max_price = selected_price.split('-')
            products = products.filter(price__gte=min_price, price__lte=max_price)
        elif '+' in selected_price:
            min_price = selected_price.replace('+', '')
            products = products.filter(price__gte=min_price)

    # On sale filter
    if on_sale:
        products = products.filter(on_sale=True)

    # Sorting
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'price-low':
        products = products.order_by('price')
    elif sort_by == 'price-high':
        products = products.order_by('-price')
    elif sort_by == 'featured':
        products = products.filter(featured=True)

    # Pagination
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Categories
    categories = Category.objects.all()

    # Cart & wishlist product IDs
    cart_product_ids = set()
    wishlist_product_ids = set()
    if request.user.is_authenticated:
        try:
            cart_items = get_cart_mongo(request.user.id) or []
            cart_product_ids = set(str(item.get('product_id')) for item in cart_items if item.get('product_id'))
            wishlist_items = get_wishlist_mongo(request.user.id) or []
            wishlist_product_ids = set(str(item.get('product_id')) for item in wishlist_items if item.get('product_id'))
        except Exception as e:
            messages.error(request, 'Error fetching cart or wishlist items.')
            print(f"Error fetching cart or wishlist: {e}")

    return render(request, 'boutique/product_list.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': sort_by,
        'selected_price': selected_price,
        'search_query': search_query,
        'on_sale': on_sale,
        'cart_product_ids': cart_product_ids,
        'wishlist_product_ids': wishlist_product_ids
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    in_wishlist = False
    
    if request.user.is_authenticated:
        try:
            wishlist_items = get_wishlist_mongo(request.user.id)
            # Handle case where wishlist_items might be None
            if wishlist_items:
                in_wishlist = any(str(item.get('product_id')) == str(product_id) for item in wishlist_items)
        except Exception as e:
            print(f"Error getting wishlist: {e}")
            in_wishlist = False
    
    return render(request, 'boutique/product_detail.html', {
        'product': product,
        'in_wishlist': in_wishlist
    })

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        wishlist_items = get_wishlist_mongo(request.user.id) or []
        
        # Check if product is already in wishlist
        product_in_wishlist = any(str(item.get('product_id')) == str(product_id) for item in wishlist_items)
        
        if product_in_wishlist:
            remove_from_wishlist_mongo(request.user.id, str(product_id))
            return JsonResponse({'status': 'removed', 'message': 'Product removed from wishlist'})
        else:
            add_to_wishlist_mongo(request.user.id, str(product_id), product.name)
            return JsonResponse({'status': 'added', 'message': 'Product added to wishlist'})
    
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

@login_required
@require_POST
def toggle_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        wishlist_items = get_wishlist_mongo(request.user.id) or []

        # Check if product is already in wishlist
        product_in_wishlist = any(str(item.get('product_id')) == str(product_id) for item in wishlist_items)

        if product_in_wishlist:
            remove_from_wishlist_mongo(request.user.id, str(product_id))
            return JsonResponse({'status': 'removed', 'message': 'Product removed from wishlist'})
        else:
            add_to_wishlist_mongo(request.user.id, str(product_id), product.name)
            return JsonResponse({'status': 'added', 'message': 'Product added to wishlist'})

    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

# Order detail view
@login_required
# def order_detail(request, order_id):
#     try:
#         order = Order.objects.get(id=order_id, customer=request.user.customer)
#     except (Order.DoesNotExist, Customer.DoesNotExist):
#         raise Http404("Order not found.")
#     order_items = order.items.select_related('product').all()
#     return render(request, 'boutique/order_detail.html', {
#         'order': order,
#         'order_items': order_items
#     })
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()   # Assuming related_name="items" in OrderItem model
    return render(request, 'boutique/order_detail.html', {
        'order': order,
        'order_items': order_items
    })



@login_required
def view_wishlist(request):
    try:
        wishlist_items = get_wishlist_mongo(request.user.id) or []
        product_ids = [item.get('product_id') for item in wishlist_items if item.get('product_id')]
        
        # Convert string IDs to integers for the database query
        product_ids_int = []
        for pid in product_ids:
            try:
                product_ids_int.append(int(pid))
            except (ValueError, TypeError):
                continue
        
        products = Product.objects.filter(id__in=product_ids_int)
        
        return render(request, 'boutique/wishlist.html', {
            'wishlist_items': products
        })
    except Exception as e:
        messages.error(request, f'Error loading wishlist: {str(e)}')
        return render(request, 'boutique/wishlist.html', {
            'wishlist_items': []
        })

@login_required
def view_cart(request):
    try:
        cart_items = get_cart_mongo(request.user.id) or []
        cart_total = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)
        
        # Get product details for cart items
        product_ids = [item.get('product_id') for item in cart_items if item.get('product_id')]
        
        # Convert string IDs to integers for the database query
        product_ids_int = []
        for pid in product_ids:
            try:
                product_ids_int.append(int(pid))
            except (ValueError, TypeError):
                continue
        
        products = Product.objects.filter(id__in=product_ids_int)
        
        # Combine MongoDB cart data with product details
        cart_with_details = []
        for item in cart_items:
            try:
                product_id_str = str(item.get('product_id'))
                product = next((p for p in products if str(p.id) == product_id_str), None)
                if product:
                    cart_with_details.append({
                        'product': product,
                        'quantity': item.get('quantity', 1),
                        'price': float(item.get('price', 0)),
                        'total': float(item.get('price', 0)) * item.get('quantity', 1)
                    })
            except Exception as e:
                print(f"Error processing cart item: {e}")
                continue
        
        return render(request, 'boutique/cart.html', {
            'cart_items': cart_with_details,
            'cart_total': cart_total
        })
    except Exception as e:
        messages.error(request, f'Error loading cart: {str(e)}')
        return render(request, 'boutique/cart.html', {
            'cart_items': [],
            'cart_total': 0
        })

@login_required
@require_POST
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        cart_items = get_cart_mongo(request.user.id) or []

        # Check if product already in cart
        product_in_cart = any(str(item.get('product_id')) == str(product_id) for item in cart_items)

        if product_in_cart:
            remove_from_cart_mongo(request.user.id, str(product_id))
            return JsonResponse({'status': 'removed', 'message': 'Product removed from cart'})
        else:
            # Passing quantity=1 and product.price
            add_to_cart_mongo(
                request.user.id,
                str(product_id),
                product.name,
                quantity=1,
                price=product.price
            )
            return JsonResponse({'status': 'added', 'message': 'Product added to cart'})

    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

@login_required
@require_POST
def update_cart(request, product_id):
    try:
        action = request.POST.get('action')
        cart_items = get_cart_mongo(request.user.id) or []
        
        for item in cart_items:
            if str(item.get('product_id')) == str(product_id):
                if action == 'increase':
                    item['quantity'] = item.get('quantity', 1) + 1
                elif action == 'decrease' and item.get('quantity', 1) > 1:
                    item['quantity'] = item.get('quantity', 1) - 1
                
                # Update the item in MongoDB
                update_cart_quantity_mongo(
                    request.user.id, 
                    str(product_id), 
                    item.get('quantity', 1)
                )
                break
        
        return JsonResponse({'status': 'success', 'message': 'Cart updated'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error updating cart: {str(e)}'})

@login_required
@require_POST
def remove_from_cart(request, product_id):
    try:
        remove_from_cart_mongo(request.user.id, str(product_id))
        return JsonResponse({'status': 'success', 'message': 'Product removed from cart'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error removing from cart: {str(e)}'})

@login_required
def checkout(request):
    if request.method == 'POST':
        try:
            # Process the order
            customer, created = Customer.objects.get_or_create(user=request.user)
            cart_items = get_cart_mongo(request.user.id) or []
            
            if not cart_items:
                messages.error(request, 'Your cart is empty')
                return redirect('view_cart')
            
            total_amount = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount,
                shipping_address=request.POST.get('shipping_address', ''),
                payment_method=request.POST.get('payment_method', 'card')
            )
            
            # Create order items
            for item in cart_items:
                try:
                    product_id = item.get('product_id')
                    if product_id:
                        product = Product.objects.get(id=int(product_id))
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.get('quantity', 1),
                            price=item.get('price', 0)
                        )
                except (Product.DoesNotExist, ValueError, TypeError) as e:
                    print(f"Error creating order item: {e}")
                    continue
            
            # Clear cart
            clear_cart_mongo(request.user.id)
            
            messages.success(request, f'Order #{order.id} has been placed successfully!')
            return render(request, 'boutique/order_confirmation.html', {'order': order})
        
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('view_cart')
    
    try:
        cart_items = get_cart_mongo(request.user.id) or []
        if not cart_items:
            messages.error(request, 'Your cart is empty')
            return redirect('view_cart')
        
        return render(request, 'boutique/checkout.html')
    except Exception as e:
        messages.error(request, f'Error loading checkout: {str(e)}')
        return redirect('view_cart')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create or update customer profile
            customer, created = Customer.objects.get_or_create(user=user)
            customer.phone = form.cleaned_data.get('phone', '')
            customer.newsletter_subscribed = form.cleaned_data.get('newsletter_subscribed', True)
            customer.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'boutique/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        # Use form for validation but handle authentication manually
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'boutique/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page if specified
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'boutique/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('product_list')

@login_required
def profile(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        # Create customer profile if it doesn't exist
        customer = Customer.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        customer_form = CustomerUpdateForm(request.POST, instance=customer)
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        customer_form = CustomerUpdateForm(instance=customer)
    
    orders = Order.objects.filter(customer=customer).order_by('-order_date')

    # Get cart and wishlist counts from MongoDB
    cart_items = get_cart_mongo(request.user.id)
    cart_items_count = len(cart_items) if cart_items else 0
    wishlist_items = get_wishlist_mongo(request.user.id)
    wishlist_count = len(wishlist_items) if wishlist_items else 0

    return render(request, 'boutique/profile.html', {
        'user_form': user_form,
        'customer_form': customer_form,
        'orders': orders,
        'cart_items_count': cart_items_count,
        'wishlist_count': wishlist_count
    })

@require_POST
def subscribe_newsletter(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email, 
                defaults={'is_active': True}
            )
            
            if not created:
                subscriber.is_active = True
                subscriber.save()
            
            return JsonResponse({'status': 'success', 'message': 'Subscribed successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid email address'})

# Admin views
@staff_member_required
def custom_admin_dashboard(request):
    return render(request, "admin_dashboard.html", {})

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    recent_orders = Order.objects.select_related('customer__user').order_by('-order_date')[:5]

    products = Product.objects.all()
    return render(request, 'boutique/admin/dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'products': products
    })
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})
#function for admin_add_catogry
@user_passes_test(is_admin)
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            # redirect to the category list page instead of dashboard
            return redirect('admin_view_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'boutique/admin/add_category.html', {'form': form})


#function to view customers data
@user_passes_test(is_admin)
def admin_view_customers(request):
    customers = Customer.objects.all()
    
    # Enrich customer data with additional information
    enriched_customers = []
    for customer in customers:
        # Get order count using reverse relationship
        order_count = customer.order_set.count()
        
        # Get wishlist count from MongoDB
        wishlist_items = get_wishlist_mongo(customer.user.id)
        wishlist_count = len(wishlist_items) if wishlist_items else 0
        
        # Get cart count from MongoDB
        cart_count = get_cart_count_mongo(customer.user.id)
        
        enriched_customers.append({
            'customer': customer,
            'order_count': order_count,
            'wishlist_count': wishlist_count,
            'cart_count': cart_count
        })
    
    return render(request, 'boutique/admin/view_customers.html', {'customers': enriched_customers})

@user_passes_test(is_admin)
def admin_view_categories(request):
    categories = Category.objects.all()
    return render(request, 'boutique/admin/view_categories.html', {'categories': categories})

@user_passes_test(is_admin)
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_view_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'boutique/admin/edit_category.html', {'form': form, 'category': category})

@login_required
def view_customers(request):
    customers = Customer.objects.all()
    return render(request, "boutique/admin/view_customers.html", {"customers": customers})



@user_passes_test(is_admin)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, "boutique/customer_detail.html", {"customer": customer})


@user_passes_test(is_admin)
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_view_categories')
    return render(request, 'boutique/admin/delete_category.html', {'category': category})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'boutique/order_confirmation.html', context)

@login_required
def order_history(request):
    # Get orders for the current user
    orders = Order.objects.filter(customer__user=request.user).order_by('-order_date')
    
    context = {
        'orders': orders,
    }
    return render(request, 'boutique/order_history.html', context)

@login_required
def order_detail(request, order_id):
    # Get specific order for the current user
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'boutique/order_detail.html', context)

@user_passes_test(is_admin)
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    categories = Category.objects.all()
    return render(request, 'boutique/admin/edit_product.html', {'form': form, 'categories': categories, 'product': product})


@user_passes_test(is_admin)
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'boutique/admin/delete_product.html', {'product': product})


@user_passes_test(is_admin)
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    return render(request, 'boutique/admin/add_product.html', {'form': form, 'categories': categories})

@user_passes_test(is_admin)
def admin_send_newsletter(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if not subject or not content:
            messages.error(request, 'Please provide both subject and content')
            return render(request, 'boutique/admin/send_newsletter.html')
        
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        subscriber_emails = [s.email for s in subscribers]
        
        # In a real application, you would use a task queue for this
        # send_mail(
        #     subject,
        #     content,
        #     settings.DEFAULT_FROM_EMAIL,
        #     subscriber_emails,
        #     fail_silently=False,
        # )
        
        messages.success(request, f'Newsletter would be sent to {len(subscriber_emails)} subscribers!')
        return redirect('admin_dashboard')
    
    return render(request, 'boutique/admin/send_newsletter.html')

# API endpoints
def api_product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'sale_price': str(product.sale_price) if product.sale_price else None,
            'on_sale': product.on_sale,
            'description': product.description,
            'image': product.image.url if product.image else '',
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

@login_required
def api_cart_count(request):
    try:
        count = get_cart_count_mongo(request.user.id) or 0
        return JsonResponse({'count': count})
    except Exception as e:
        return JsonResponse({'count': 0})

# Debug view (remove in production)
def debug_view(request):
    users = User.objects.all()
    output = "<h1>Users in Database:</h1><ul>"
    for user in users:
        output += f"<li>{user.username} - {user.email} - Staff: {user.is_staff} - Active: {user.is_active}</li>"
    output += "</ul>"
    return HttpResponse(output)

# Add to views.py
@login_required
def debug_cart(request):
    """Debug view to see cart contents"""
    cart_items = get_cart_mongo(request.user.id) or []
    output = f"<h1>Cart for user {request.user.id}</h1>"
    output += f"<p>Cart count: {get_cart_count_mongo(request.user.id)}</p>"
    output += "<h2>Cart items:</h2><ul>"
    
    for item in cart_items:
        output += f"<li>Product ID: {item.get('product_id')}, Name: {item.get('product_name')}, Quantity: {item.get('quantity')}, Price: {item.get('price')}</li>"
    
    output += "</ul>"
    
    # Check MongoDB connection
    try:
        from .mongodb_utils import get_mongodb_connection
        db = get_mongodb_connection()
        if db:
            output += "<p>MongoDB connection: OK</p>"
            # Check if cart collection exists
            collections = db.list_collection_names()
            output += f"<p>Collections: {', '.join(collections)}</p>"
        else:
            output += "<p>MongoDB connection: Using memory fallback</p>"
    except Exception as e:
        output += f"<p>MongoDB connection error: {e}</p>"
    
    return HttpResponse(output)
    