from flask import Flask, request, jsonify, abort
from config import app, db
from flask_migrate import Migrate
from models import Product, User, Transaction
from flask_bcrypt import Bcrypt
import datetime

bcrypt = Bcrypt(app)

migrate = Migrate(app, db)

@app.route('/')
def index():
    return '<h1>Project Group 5</h1>'
# Products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        sku=data['sku'],
        description=data.get('description'),
        quantity=data['quantity'],
        price=data['price'],
        supplier=data.get('supplier')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get_or_404(id)
    product.name = data['name']
    product.sku = data['sku']
    product.description = data.get('description')
    product.quantity = data['quantity']
    product.price = data['price']
    product.supplier = data.get('supplier')
    db.session.commit()
    return jsonify(product.to_dict())

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

#transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@app.route('/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    return jsonify(transaction.to_dict())

@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    new_transaction = Transaction(
        user_id=data['user_id'],
        product_id=data['product_id'],
        quantity=data['quantity'],
        total_price=data['total_price']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify(new_transaction.to_dict()), 201

@app.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    data = request.get_json()
    transaction = Transaction.query.get_or_404(id)
    transaction.user_id = data['user_id']
    transaction.product_id = data['product_id']
    transaction.quantity = data['quantity']
    transaction.total_price = data['total_price']
    db.session.commit()
    return jsonify(transaction.to_dict())

@app.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return '', 204


#users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        # Return a list of all users
        users = User.query.all()
        return jsonify([user.serialize for user in users])
    elif request.method == 'POST':
        # Create a new user
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        companyName = data.get('companyName')
        country = data.get('country')
        city = data.get('city')

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists"}), 400

        new_user = User(
            email=email,
            companyName=companyName,
            country=country,
            city=city
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Login successful", "user_id": user.id})
    else:
        return jsonify({"message": "Invalid email or password"}), 401



if __name__ == '_main_':
    app.run(port=5000, debug=True)