# boutique/managers.py
from djongo import models

class ProductManager(models.DjongoManager):
    def get_products_by_category(self, category_name):
        return self.filter(category__name=category_name)
    
    def get_featured_products(self):
        return self.filter(featured=True)
    
    def search_products(self, query):
        return self.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query)
        )
    
    def get_products_on_sale(self):
        return self.filter(on_sale=True)

# Update the Product model to use the custom manager
class Product(models.Model):
    # ... fields as before ...
    objects = ProductManager()
    
    class Meta:
        db_table = 'product'
        ordering = ['-created_at']