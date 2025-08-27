from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
import json

def get_mongodb_connection():
    """Get MongoDB connection"""
    try:
        client = MongoClient(
            host=settings.MONGODB['host'],
            port=settings.MONGODB['port']
        )
        # Test the connection
        client.admin.command('ismaster')
        return client[settings.MONGODB['db']]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        # Fallback to a simple dictionary-based storage for development
        return None

# Simple in-memory storage fallback for development
memory_storage = {
    'cart': {},
    'wishlist': {}
}

def add_to_cart_mongo(user_id, product_id, product_name, quantity, price):
    """Add product to cart in MongoDB or fallback to memory"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            cart_data = {
                'user_id': user_id,
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'price': float(price),
                'added_date': datetime.now().isoformat()
            }
            collection = db['cart']
            # Remove existing item for this user and product
            collection.delete_one({'user_id': user_id, 'product_id': product_id})
            # Insert new item
            return collection.insert_one(cart_data)
        else:
            # Fallback to memory storage
            if user_id not in memory_storage['cart']:
                memory_storage['cart'][user_id] = {}
            memory_storage['cart'][user_id][product_id] = {
                'product_name': product_name,
                'quantity': quantity,
                'price': float(price),
                'added_date': datetime.now().isoformat()
            }
            return True
    except Exception as e:
        print(f"Error adding to cart: {e}")
        # Fallback to memory storage
        if user_id not in memory_storage['cart']:
            memory_storage['cart'][user_id] = {}
        memory_storage['cart'][user_id][product_id] = {
            'product_name': product_name,
            'quantity': quantity,
            'price': float(price),
            'added_date': datetime.now().isoformat()
        }
        return True

def get_cart_mongo(user_id):
    """Get user's cart from MongoDB or fallback to memory"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['cart']
            return list(collection.find({'user_id': user_id}))
        else:
            # Fallback to memory storage
            if user_id in memory_storage['cart']:
                cart_items = []
                for product_id, item in memory_storage['cart'][user_id].items():
                    cart_items.append({
                        'user_id': user_id,
                        'product_id': product_id,
                        'product_name': item['product_name'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'added_date': item['added_date']
                    })
                return cart_items
            return []
    except Exception as e:
        print(f"Error getting cart: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['cart']:
            cart_items = []
            for product_id, item in memory_storage['cart'][user_id].items():
                cart_items.append({
                    'user_id': user_id,
                    'product_id': product_id,
                    'product_name': item['product_name'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'added_date': item['added_date']
                })
            return cart_items
        return []


def get_cart_count_mongo(user_id):
    """Get cart item count for user"""
    try:
        cart_items = get_cart_mongo(user_id)
        return len(cart_items) if cart_items else 0
    except Exception as e:
        print(f"Error getting cart count: {e}")
        return 0

def update_cart_quantity_mongo(user_id, product_id, quantity):
    """Update cart item quantity"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['cart']
            return collection.update_one(
                {'user_id': user_id, 'product_id': product_id},
                {'$set': {'quantity': quantity}}
            )
        else:
            # Fallback to memory storage
            if user_id in memory_storage['cart'] and product_id in memory_storage['cart'][user_id]:
                memory_storage['cart'][user_id][product_id]['quantity'] = quantity
            return True
    except Exception as e:
        print(f"Error updating cart quantity: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['cart'] and product_id in memory_storage['cart'][user_id]:
            memory_storage['cart'][user_id][product_id]['quantity'] = quantity
        return True

def remove_from_cart_mongo(user_id, product_id):
    """Remove product from cart in MongoDB"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['cart']
            return collection.delete_one({'user_id': user_id, 'product_id': product_id})
        else:
            # Fallback to memory storage
            if user_id in memory_storage['cart'] and product_id in memory_storage['cart'][user_id]:
                del memory_storage['cart'][user_id][product_id]
            return True
    except Exception as e:
        print(f"Error removing from cart: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['cart'] and product_id in memory_storage['cart'][user_id]:
            del memory_storage['cart'][user_id][product_id]
        return True

def clear_cart_mongo(user_id):
    """Clear user's cart"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['cart']
            return collection.delete_many({'user_id': user_id})
        else:
            # Fallback to memory storage
            if user_id in memory_storage['cart']:
                memory_storage['cart'][user_id] = {}
            return True
    except Exception as e:
        print(f"Error clearing cart: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['cart']:
            memory_storage['cart'][user_id] = {}
        return True

# Similar fixes for wishlist functions
def add_to_wishlist_mongo(user_id, product_id, product_name):
    """Add product to wishlist in MongoDB"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            wishlist_data = {
                'user_id': user_id,
                'product_id': product_id,
                'product_name': product_name,
                'added_date': datetime.now().isoformat()
            }
            collection = db['wishlist']
            # Remove existing item for this user and product
            collection.delete_one({'user_id': user_id, 'product_id': product_id})
            # Insert new item
            return collection.insert_one(wishlist_data)
        else:
            # Fallback to memory storage
            if user_id not in memory_storage['wishlist']:
                memory_storage['wishlist'][user_id] = {}
            memory_storage['wishlist'][user_id][product_id] = {
                'product_name': product_name,
                'added_date': datetime.now().isoformat()
            }
            return True
    except Exception as e:
        print(f"Error adding to wishlist: {e}")
        # Fallback to memory storage
        if user_id not in memory_storage['wishlist']:
            memory_storage['wishlist'][user_id] = {}
        memory_storage['wishlist'][user_id][product_id] = {
            'product_name': product_name,
            'added_date': datetime.now().isoformat()
        }
        return True

def get_wishlist_mongo(user_id):
    """Get user's wishlist from MongoDB"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['wishlist']
            return list(collection.find({'user_id': user_id}))
        else:
            # Fallback to memory storage
            if user_id in memory_storage['wishlist']:
                wishlist_items = []
                for product_id, item in memory_storage['wishlist'][user_id].items():
                    wishlist_items.append({
                        'user_id': user_id,
                        'product_id': product_id,
                        'product_name': item['product_name'],
                        'added_date': item['added_date']
                    })
                return wishlist_items
            return []
    except Exception as e:
        print(f"Error getting wishlist: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['wishlist']:
            wishlist_items = []
            for product_id, item in memory_storage['wishlist'][user_id].items():
                wishlist_items.append({
                    'user_id': user_id,
                    'product_id': product_id,
                    'product_name': item['product_name'],
                    'added_date': item['added_date']
                })
            return wishlist_items
        return []

def remove_from_wishlist_mongo(user_id, product_id):
    """Remove product from wishlist in MongoDB"""
    try:
        db = get_mongodb_connection()
        if db is not None:
            collection = db['wishlist']
            return collection.delete_one({'user_id': user_id, 'product_id': product_id})
        else:
            # Fallback to memory storage
            if user_id in memory_storage['wishlist'] and product_id in memory_storage['wishlist'][user_id]:
                del memory_storage['wishlist'][user_id][product_id]
            return True
    except Exception as e:
        print(f"Error removing from wishlist: {e}")
        # Fallback to memory storage
        if user_id in memory_storage['wishlist'] and product_id in memory_storage['wishlist'][user_id]:
            del memory_storage['wishlist'][user_id][product_id]
        return True