from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Product, User, Order, OrderItem
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@main.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@main.route('/cart/add/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    
    # If product is already in cart, increment quantity
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        # Otherwise, add it to the cart
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'quantity': 1
        }
    
    session['cart'] = cart
    flash(f'{product.name} has been added to your cart!', 'success')
    return redirect(url_for('main.index'))

@main.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@main.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')
    return redirect(url_for('main.view_cart'))

@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Find user or create a new one
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email)
            db.session.add(user)
            db.session.commit() # Commit to get user.id

        total = sum(item['price'] * item['quantity'] for item in cart.values())
        
        # Create new order
        new_order = Order(user_id=user.id, total=total)
        db.session.add(new_order)
        db.session.commit() # Commit to get order.id

        # Create order items
        for product_id, item_data in cart.items():
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=int(product_id),
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Clear the cart
        session.pop('cart', None)

        flash('Your order has been placed successfully!', 'success')
        return render_template('checkout.html', order_placed=True, order=new_order)

    return render_template('checkout.html', order_placed=False)
