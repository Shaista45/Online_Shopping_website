
# 🛍️ Online Shopping Website

A full-stack e-commerce web application built with Django 🐍.
This project allows users to browse products, manage carts & wishlists, and place orders, 
while providing admins with tools to manage products, users, and orders.




## ✨ Features
### 👤 User Features

* 🔐 Authentication – Register/Login securely.

* 🛒 Shopping Cart – Add, update, and remove items.

* 💖 Wishlist – Save favorite products for later.

* 📦 Order Management – Track order history & details.

* 📱 Responsive UI – Works seamlessly on desktop & mobile.

 ## 🛠️ Admin Features

* 🏬 Product Management – Add, edit, or delete products.

* 📊 Order Management – Manage customer orders.

* 👥 User Management – Manage accounts & permissions.


## 🛠️ Technologies Used

* **Backend**: Django (Python)
* **Frontend**: HTML, CSS, JavaScript
* **Database**: SQLite
* **Version Control**: Git


## 📦 Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Shaista45/Online_Shopping_website.git
   cd Online_Shopping_website
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` in your browser to view the application.

## 🔐 Admin Access
 * username= admin
 * password=admin123

To access the admin dashboard:

1. **Create a Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

   Follow the prompts to set up the admin credentials.

2. **Login**:

   Navigate to `http://127.0.0.1:8000/admin/` and log in using the superuser credentials.
   

## 📄 License

This project is licensed under the MIT License 

-------

