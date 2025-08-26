from django.core.management.base import BaseCommand
from boutique.models import Category, Product

class Command(BaseCommand):
    help = 'Load sample data for the boutique'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            ('Clothing', 'Fashionable clothing items'),
            ('Accessories', 'Stylish accessories'),
            ('Footwear', 'Comfortable and trendy footwear'),
        ]
        
        for name, description in categories:
            Category.objects.get_or_create(name=name, defaults={'description': description})
        
        # Create sample products
        clothing = Category.objects.get(name='Clothing')
        accessories = Category.objects.get(name='Accessories')
        footwear = Category.objects.get(name='Footwear')
        
        products = [
            {
                'name': 'Classic White Shirt',
                'description': 'A timeless classic white shirt made from premium cotton.',
                'price': 89.99,
                'category': clothing,
                'stock': 50,
                'featured': True
            },
            {
                'name': 'Leather Handbag',
                'description': 'Elegant leather handbag with multiple compartments.',
                'price': 129.99,
                'category': accessories,
                'stock': 30,
                'featured': True
            },
            {
                'name': 'Running Shoes',
                'description': 'Comfortable running shoes with extra cushioning.',
                'price': 149.99,
                'category': footwear,
                'stock': 40,
                'on_sale': True,
                'sale_price': 119.99
            },
            {
                'name': 'Summer Dress',
                'description': 'Light and breezy summer dress perfect for warm weather.',
                'price': 79.99,
                'category': clothing,
                'stock': 25,
                'on_sale': True,
                'sale_price': 59.99
            },
        ]
        
        for product_data in products:
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))