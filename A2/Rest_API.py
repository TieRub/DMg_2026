import os
from datetime import date
import datetime as dt
from typing import List
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy import String, Integer, Date, ForeignKey

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
db_root_user = os.environ.get('MARIADB_USER', 'root')
db_root_password = os.environ.get('MARIADB_PASSWORD', 'password')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mariadb+mariadbconnector://{db_root_user}:{db_root_password}@db:3306/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


class Customer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")


class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    orderDate: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    positions: Mapped[List["OrderPosition"]] = relationship(
        back_populates="order", cascade="all, delete", passive_deletes=True
    )


class OrderPosition(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    buyingPrice: Mapped[int] = mapped_column(Integer, nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    
    order: Mapped["Order"] = relationship(back_populates="positions")
    product: Mapped["Product"] = relationship(back_populates="positions")


class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    positions: Mapped[List["OrderPosition"]] = relationship(back_populates="product")


with app.app_context():
    db.create_all()


@app.route("/customers", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def operations_on_customers():
    if request.method == "GET":
        customers = db.session.query(Customer).all()
        return jsonify([{"id": c.id, "name": c.name, "orders": [{"id": o.id} for o in c.orders]} for c in customers]), 200
        
    elif request.method == "POST":
        data_list = request.get_json(silent=True) or []
        new_customers = [Customer(name=d["name"]) for d in data_list if "name" in d]
        db.session.add_all(new_customers)
        db.session.commit()
        return jsonify([{"id": c.id, "name": c.name, "orders": []} for c in new_customers]), 201
        
    elif request.method == "PUT":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            c = db.session.get(Customer, d.get("id"))
            if c:
                c.name = d["name"]
                updated.append(c)
        db.session.commit()
        return jsonify([{"id": c.id, "name": c.name} for c in updated]), 200
        
    elif request.method == "PATCH":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            c = db.session.get(Customer, d.get("id"))
            if c and "name" in d:
                c.name = d["name"]
                updated.append(c)
        db.session.commit()
        return jsonify([{"id": c.id, "name": c.name} for c in updated]), 200
        
    elif request.method == "DELETE":
        data_list = request.get_json(silent=True) or []
        for d in data_list:
            c = db.session.get(Customer, d.get("id"))
            if c:
                db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Data deleted"}), 200
    

@app.route("/customers/<int:customer_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer is None:
        return jsonify({"error": "Customer not found"}), 404
        
    if request.method == "GET":
        return jsonify({
            "id": customer.id, 
            "name": customer.name, 
            "orders": [{"id": o.id} for o in customer.orders]
        }), 200
        
    elif request.method == "PUT":
        customer_data = request.get_json()
        customer.name = customer_data["name"]
        db.session.commit()
        return jsonify({
            "id": customer.id, 
            "name": customer.name, 
            "orders": [{"id": o.id} for o in customer.orders]
        }), 200
        
    elif request.method == "PATCH":
        customer_data = request.get_json()
        if "name" in customer_data:
            customer.name = customer_data["name"]
        db.session.commit()
        return jsonify({
            "id": customer.id, 
            "name": customer.name, 
            "orders": [{"id": o.id} for o in customer.orders]
        }), 200
        
    elif request.method == "DELETE":
        db.session.delete(customer)
        db.session.commit()
        return "data deleted", 200




from datetime import date
from flask import request, jsonify

import datetime as dt  # Konflikte vermeiden durch Alias dt
from flask import request, jsonify

@app.route("/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def operations_on_orders():
    if request.method == "GET":
        orders = db.session.query(Order).all()
        return jsonify([{
            "id": o.id, 
            "orderDate": o.orderDate.isoformat() if o.orderDate else None,
            "customer_id": o.customer_id,
            "positions": [{"id": p.id, "quantity": p.quantity, "buyingPrice": p.buyingPrice, "product_id": p.product_id} for p in o.positions]
        } for o in orders]), 200
        
    elif request.method == "POST":
        data_list = request.get_json(silent=True) or []
        new_orders = []
        for d in data_list:
            # Verwendung des eindeutigen Alias 'dt'
            o_date = dt.date.fromisoformat(d["orderDate"]) if "orderDate" in d else dt.date.today()
            new_orders.append(Order(orderDate=o_date, customer_id=d["customer_id"]))
        db.session.add_all(new_orders)
        db.session.commit()
        return jsonify([{"id": o.id, "orderDate": o.orderDate.isoformat(), "customer_id": o.customer_id} for o in new_orders]), 200

    elif request.method == "PUT":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            o = db.session.get(Order, d.get("id"))
            if o:
                o.orderDate = dt.date.fromisoformat(d["orderDate"]) if "orderDate" in d else o.orderDate
                o.customer_id = d.get("customer_id", o.customer_id)
                updated.append(o)
        db.session.commit()
        return jsonify([{"id": o.id, "orderDate": o.orderDate.isoformat(), "customer_id": o.customer_id} for o in updated]), 200

    elif request.method == "PATCH":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            o = db.session.get(Order, d.get("id"))
            if o:
                if "orderDate" in d:
                    o.orderDate = dt.date.fromisoformat(d["orderDate"])
                if "customer_id" in d:
                    o.customer_id = d["customer_id"]
                updated.append(o)
        db.session.commit()
        return jsonify([{"id": o.id, "orderDate": o.orderDate.isoformat(), "customer_id": o.customer_id} for o in updated]), 200

    elif request.method == "DELETE":
        data_list = request.get_json(silent=True) or []
        for d in data_list:
            o = db.session.get(Order, d.get("id"))
            if o:
                db.session.delete(o)
        db.session.commit()
        return "data deleted", 200


@app.route("/orders/<int:order_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_order(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        return "Order not found", 404
        
    if request.method == "GET":
        return jsonify({
            "id": order.id, 
            "orderDate": order.orderDate.isoformat() if order.orderDate else None,
            "customer_id": order.customer_id,
            "positions": [{
                "id": p.id, 
                "quantity": p.quantity, 
                "buyingPrice": p.buyingPrice, 
                "product_id": p.product_id, 
                "order_id": p.order_id
            } for p in order.positions]
        }), 200
        
    elif request.method == "PUT":
        order_data = request.get_json()
        if "orderDate" in order_data:
            order.orderDate = date.fromisoformat(order_data["orderDate"])
        order.customer_id = order_data.get("customer_id")
        db.session.commit()
        return jsonify({
            "id": order.id, 
            "orderDate": order.orderDate.isoformat() if order.orderDate else None,
            "customer_id": order.customer_id
        }), 200
        
    elif request.method == "PATCH":
        order_data = request.get_json()
        if "orderDate" in order_data:
            order.orderDate = date.fromisoformat(order_data["orderDate"])
        if "customer_id" in order_data:
            order.customer_id = order_data["customer_id"]
        db.session.commit()
        return jsonify({
            "id": order.id, 
            "orderDate": order.orderDate.isoformat() if order.orderDate else None,
            "customer_id": order.customer_id
        }), 200
        
    elif request.method == "DELETE":
        db.session.delete(order)
        db.session.commit()
        return "data deleted", 200



@app.route("/orders/<int:order_id>/positions", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def operations_on_order_positions(order_id):
    if request.method == "GET":
        positions = db.session.query(OrderPosition).filter_by(order_id=order_id).all()
        return jsonify([{"id": p.id, "quantity": p.quantity, "buyingPrice": p.buyingPrice, "product_id": p.product_id, "order_id": p.order_id} for p in positions]), 200
        
    elif request.method == "POST":
        data_list = request.get_json(silent=True) or []
        new_positions = []
        for d in data_list:
            new_positions.append(OrderPosition(
                quantity=d.get("quantity"),
                buyingPrice=d.get("buyingPrice"),
                product_id=d.get("product_id"),
                order_id=order_id
            ))
        db.session.add_all(new_positions)
        db.session.commit()
        return jsonify([{"id": p.id, "quantity": p.quantity, "buyingPrice": p.buyingPrice} for p in new_positions]), 201

    elif request.method == "PUT":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            p = db.session.get(OrderPosition, d.get("id"))
            if p:
                p.quantity = d.get("quantity")
                p.buyingPrice = d.get("buyingPrice")
                p.product_id = d.get("product_id")
                updated.append(p)
        db.session.commit()
        return jsonify([{"id": p.id, "quantity": p.quantity} for p in updated]), 200

    elif request.method == "PATCH":
        data_list = request.get_json(silent=True) or []
        updated = []
        for d in data_list:
            p = db.session.get(OrderPosition, d.get("id"))
            if p:
                if "quantity" in d: p.quantity = d["quantity"]
                if "buyingPrice" in d: p.buyingPrice = d["buyingPrice"]
                if "product_id" in d: p.product_id = d["product_id"]
                updated.append(p)
        db.session.commit()
        return jsonify([{"id": p.id, "quantity": p.quantity} for p in updated]), 200

    elif request.method == "DELETE":
        data_list = request.get_json(silent=True) or []
        for d in data_list:
            p = db.session.get(OrderPosition, d.get("id"))
            if p:
                db.session.delete(p)
        db.session.commit()
        return jsonify({"message": "Data deleted"}), 200
    

@app.route("/orders/<int:order_id>/positions/<int:position_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_single_position(order_id, position_id):
    main_position = db.session.get(OrderPosition, position_id)
    if main_position is None:
        return jsonify({"error": "Position not found"}), 404

    if request.method == "GET":
        return jsonify({
            "id": main_position.id,
            "quantity": main_position.quantity,
            "buyingPrice": main_position.buyingPrice,
            "product_id": main_position.product_id,
            "order_id": main_position.order_id
        }), 200

    elif request.method == "PUT":
        body_data = request.get_json(silent=True)
        updated_positions = []

        if isinstance(body_data, list):
            for pos_data in body_data:
                pos = db.session.get(OrderPosition, pos_data.get("id"))
                if pos:
                    pos.quantity = pos_data.get("quantity")
                    pos.buyingPrice = pos_data.get("buyingPrice")
                    pos.product_id = pos_data.get("product_id")
                    pos.order_id = pos_data.get("order_id", order_id)
                    updated_positions.append(pos)
        elif isinstance(body_data, dict):
            main_position.quantity = body_data.get("quantity")
            main_position.buyingPrice = body_data.get("buyingPrice")
            main_position.product_id = body_data.get("product_id")
            main_position.order_id = body_data.get("order_id", order_id)
            updated_positions.append(main_position)

        db.session.commit()
        return jsonify([{
            "id": p.id,
            "quantity": p.quantity,
            "buyingPrice": p.buyingPrice,
            "product_id": p.product_id,
            "order_id": p.order_id
        } for p in updated_positions]), 200

    elif request.method == "PATCH":
        body_data = request.get_json(silent=True)
        updated_positions = []

        if isinstance(body_data, list):
            for pos_data in body_data:
                pos = db.session.get(Position, pos_data.get("id"))
                if pos:
                    if "quantity" in pos_data:
                        pos.quantity = pos_data["quantity"]
                    if "buyingPrice" in pos_data:
                        pos.buyingPrice = pos_data["buyingPrice"]
                    if "product_id" in pos_data:
                        pos.product_id = pos_data["product_id"]
                    if "order_id" in pos_data:
                        pos.order_id = pos_data["order_id"]
                    updated_positions.append(pos)
        elif isinstance(body_data, dict):
            if "quantity" in body_data:
                main_position.quantity = body_data["quantity"]
            if "buyingPrice" in body_data:
                main_position.buyingPrice = body_data["buyingPrice"]
            if "product_id" in body_data:
                main_position.product_id = body_data["product_id"]
            if "order_id" in body_data:
                main_position.order_id = body_data["order_id"]
            updated_positions.append(main_position)

        db.session.commit()
        return jsonify([{
            "id": p.id,
            "quantity": p.quantity,
            "buyingPrice": p.buyingPrice,
            "product_id": p.product_id,
            "order_id": p.order_id
        } for p in updated_positions]), 200

    elif request.method == "DELETE":
        db.session.delete(main_position)
        db.session.commit()
        return "data deleted", 200



@app.route("/products", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def operations_on_products():
    if request.method == "GET":
        products = db.session.query(Product).all()
        return jsonify([{
            "id": p.id, 
            "title": p.title, 
            "price": p.price
        } for p in products]), 200
        
    elif request.method == "POST":
        product_list = request.get_json(silent=True) or []
        products = []
        for p_data in product_list:
            if "title" in p_data and "price" in p_data:
                products.append(Product(
                    title=p_data["title"], 
                    price=p_data["price"]
                ))
        db.session.add_all(products)
        db.session.commit()
        return jsonify([{
            "id": p.id, 
            "title": p.title, 
            "price": p.price
        } for p in products]), 201
        
    elif request.method == "PUT":
        product_list = request.get_json(silent=True) or []
        updated_products = []
        for p_data in product_list:
            product = db.session.get(Product, p_data.get("id"))
            if product:
                product.title = p_data["title"]
                product.price = p_data["price"]
                updated_products.append(product)
        db.session.commit()
        return jsonify([{
            "id": p.id, 
            "title": p.title, 
            "price": p.price
        } for p in updated_products]), 200
        
    elif request.method == "PATCH":
        product_list = request.get_json(silent=True) or []
        updated_products = []
        for p_data in product_list:
            product = db.session.get(Product, p_data.get("id"))
            if product:
                if "title" in p_data:
                    product.title = p_data["title"]
                if "price" in p_data:
                    product.price = p_data["price"]
                updated_products.append(product)
        db.session.commit()
        return jsonify([{
            "id": p.id, 
            "title": p.title, 
            "price": p.price
        } for p in updated_products]), 200
        
    elif request.method == "DELETE":
        product_list = request.get_json(silent=True) or []
        for p_data in product_list:
            product = db.session.get(Product, p_data.get("id"))
            if product:
                db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Products deleted"}), 200

    return jsonify({"error": "Method not allowed"}), 405


@app.route("/products/<int:product_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def operations_on_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
        
    if request.method == "GET":
        return jsonify({
            "id": product.id, 
            "title": product.title, 
            "price": product.price
        }), 200
        
    elif request.method == "PUT":
        product_data = request.get_json()
        product.title = product_data["title"]
        product.price = product_data["price"]
        db.session.commit()
        return jsonify({
            "id": product.id, 
            "title": product.title, 
            "price": product.price
        }), 200
        
    elif request.method == "PATCH":
        product_data = request.get_json()
        if "title" in product_data:
            product.title = product_data["title"]
        if "price" in product_data:
            product.price = product_data["price"]
        db.session.commit()
        return jsonify({
            "id": product.id, 
            "title": product.title, 
            "price": product.price
        }), 200
        
    elif request.method == "DELETE":
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)    