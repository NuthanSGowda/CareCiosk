from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import json
import logging
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a random string in production

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'arise',  # Updated with your MySQL root password
    'database': 'medicine_kiosk'
}

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def standardize_filename(name, extension):
    # Convert to lowercase, replace spaces with underscores, remove invalid chars
    clean_name = re.sub(r'[^a-z0-9\s-]', '', name.lower()).replace(' ', '_')
    return f"{clean_name}{extension}"

@app.route('/')
def home():
    query = request.args.get('query', '')
    search_type = request.args.get('search_type', 'name')
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if query:
        if search_type == 'name':
            sql = "SELECT * FROM medicines WHERE name LIKE %s"
            cursor.execute(sql, ('%' + query + '%',))
        else:
            sql = "SELECT * FROM medicines WHERE category LIKE %s"
            cursor.execute(sql, ('%' + query + '%',))
    else:
        sql = "SELECT * FROM medicines"
        cursor.execute(sql)
    
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if 'cart' not in session:
        session['cart'] = {}
    
    return render_template('index.html', medicines=medicines, query=query, search_type=search_type)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            logger.debug(f"Found user: {user['username']}, checking password")
            if user['password'] == password:
                user_obj = User(user['id'], user['username'], user['role'])
                login_user(user_obj)
                flash('Logged in successfully!', 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('home'))
            else:
                logger.debug(f"Password mismatch for user: {username}")
        else:
            logger.debug(f"No user found for username: {username}")
        
        cursor.close()
        conn.close()
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('signup.html')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, password, role)
                )
                conn.commit()
                flash(f'Account created for {username}', 'success')
                return redirect(url_for('admin'))
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Database error: {e}", 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/add_to_cart/<int:medicine_id>', methods=['POST'])
@login_required
def add_to_cart(medicine_id):
    quantity = int(request.form.get('quantity', 1))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, name, price, stock, image_path FROM medicines WHERE id = %s", (medicine_id,))
        medicine = cursor.fetchone()
        
        if medicine and medicine['stock'] >= quantity:
            new_stock = medicine['stock'] - quantity
            cursor.execute("UPDATE medicines SET stock = %s WHERE id = %s", (new_stock, medicine_id))
            conn.commit()
            
            cart = session.get('cart', {})
            price = float(medicine['price'])
            if str(medicine_id) in cart:
                cart[str(medicine_id)]['quantity'] += quantity
            else:
                cart[str(medicine_id)] = {
                    'name': medicine['name'],
                    'price': price,
                    'quantity': quantity,
                    'image_path': medicine['image_path']
                }
            session['cart'] = cart
        else:
            flash('Insufficient stock or medicine not found', 'error')
        
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Database error: {e}", 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<medicine_id>', methods=['POST'])
@login_required
def remove_from_cart(medicine_id):
    cart = session.get('cart', {})
    if medicine_id in cart:
        quantity = cart[medicine_id]['quantity']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE medicines SET stock = stock + %s WHERE id = %s", (quantity, medicine_id))
            conn.commit()
            del cart[medicine_id]
            session['cart'] = cart
            flash('Item removed from cart', 'success')
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Database error: {e}", 'error')
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0.0
    
    for medicine_id, item in cart.items():
        price = float(item['price'])
        quantity = item['quantity']
        subtotal = price * quantity
        cart_items.append({
            'id': medicine_id,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal,
            'image_path': item['image_path']
        })
        total += subtotal
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/purchase', methods=['POST'])
@login_required
def purchase():
    if 'cart' in session and session['cart']:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cart = session['cart']
            cart_items = [
                {
                    'id': medicine_id,
                    'name': item['name'],
                    'price': float(item['price']),
                    'quantity': item['quantity'],
                    'image_path': item['image_path']
                } for medicine_id, item in cart.items()
            ]
            total = sum(item['price'] * item['quantity'] for item in cart_items)
            cursor.execute(
                "INSERT INTO orders (user_id, medicines, total) VALUES (%s, %s, %s)",
                (current_user.id, json.dumps(cart_items), total)
            )
            conn.commit()
            session['cart'] = {}
            session.modified = True
            return jsonify({'success': True, 'message': 'Purchase completed successfully'})
        except mysql.connector.Error as e:
            conn.rollback()
            return jsonify({'success': False, 'message': f"Database error: {e}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({'success': False, 'message': 'Cart is empty'})

@app.route('/orders')
@login_required
def orders():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, order_date, medicines, total FROM orders WHERE user_id = %s ORDER BY order_date DESC", (current_user.id,))
    orders = cursor.fetchall()
    for order in orders:
        order['medicines'] = json.loads(order['medicines'])
    cursor.close()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orders WHERE user_id = %s", (current_user.id,))
        conn.commit()
        flash('Order history cleared successfully', 'success')
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Database error: {e}", 'error')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('orders'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST' and 'restock_quantity' in request.form:
        medicine_id = request.form.get('medicine_id')
        restock_quantity = request.form.get('restock_quantity', type=int)
        
        if restock_quantity and restock_quantity > 0:
            try:
                cursor.execute("UPDATE medicines SET stock = stock + %s WHERE id = %s", (restock_quantity, medicine_id))
                conn.commit()
                flash('Stock updated successfully', 'success')
            except mysql.connector.Error as e:
                conn.rollback()
                flash(f"Database error: {e}", 'error')
    
    cursor.execute("SELECT id, name, stock FROM medicines")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin.html', medicines=medicines)

@app.route('/admin/add_medicine', methods=['POST'])
@login_required
def add_medicine():
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price', type=float)
    stock = request.form.get('stock', type=int)
    file = request.files.get('image')
    
    if not all([name, category, price, stock is not None]):
        flash('All fields except image are required', 'error')
        return redirect(url_for('admin'))
    
    if price <= 0:
        flash('Price must be positive', 'error')
        return redirect(url_for('admin'))
    
    if stock < 0:
        flash('Stock cannot be negative', 'error')
        return redirect(url_for('admin'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id FROM medicines WHERE name = %s", (name,))
        if cursor.fetchone():
            flash('Medicine name already exists', 'error')
            return redirect(url_for('admin'))
        
        image_path = ''
        if file and allowed_file(file.filename):
            # Use medicine name for filename
            extension = os.path.splitext(file.filename)[1].lower()
            filename = standardize_filename(name, extension)
            # Ensure unique filename
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                filename = f"{base}_{counter}{ext}"  # Fixed: Changed 'logaext' to 'ext'
                counter += 1
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
        
        cursor.execute(
            "INSERT INTO medicines (name, category, price, stock, image_path) VALUES (%s, %s, %s, %s, %s)",
            (name, category, price, stock, image_path)
        )
        conn.commit()
        flash(f'Medicine {name} added successfully', 'success')
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Database error: {e}", 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/remove_medicine/<int:medicine_id>', methods=['POST'])
@login_required
def remove_medicine(medicine_id):
    if current_user.role != 'admin':
        flash('Access denied: Admins only', 'error')
        return redirect(url_for('home'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if medicine exists and get image_path
        cursor.execute("SELECT name, image_path FROM medicines WHERE id = %s", (medicine_id,))
        medicine = cursor.fetchone()
        
        if not medicine:
            flash('Medicine not found', 'error')
            return redirect(url_for('admin'))
        
        # Delete the medicine
        cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
        conn.commit()
        
        # Remove from session cart if present
        if 'cart' in session and str(medicine_id) in session['cart']:
            del session['cart'][str(medicine_id)]
            session.modified = True
        
        # Delete associated image file if it exists
        if medicine['image_path']:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], medicine['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        flash(f"Medicine {medicine['name']} removed successfully", 'success')
    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Database error: {e}", 'error')
    except OSError as e:
        flash(f"Error deleting image: {e}", 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)