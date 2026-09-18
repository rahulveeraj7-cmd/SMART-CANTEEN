from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "smart_canteen_secret_key"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",   # Keep your actual MySQL password here
        database="smart_canteen"
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        college_id = request.form["college_id"].strip()
        password = request.form["password"]
        user_type = request.form["user_type"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE college_id = %s
            AND user_type = %s
            """,
            (college_id, user_type)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            session["college_id"] = user["college_id"]
            session["user_type"] = user["user_type"]

            if user["user_type"] == "student":

                session["student_name"] = user.get(
                    "student_name",
                    ""
                )

                return redirect(url_for("student"))

            elif user["user_type"] == "faculty":

                return redirect(url_for("faculty"))

            elif user["user_type"] == "admin":

                return redirect(url_for("admin"))

        return render_template(
            "login.html",
            error="Invalid ID, password, or user type."
        )

    return render_template("login.html")


# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/student")
def student():

    if (
        "college_id" not in session
        or session.get("user_type") != "student"
    ):
        return redirect(url_for("login"))

    return render_template(
        "student.html",
        student_name=session.get("student_name", "")
    )


# =========================
# STUDENT ORDERS
# =========================

@app.route("/student_orders")
def student_orders():

    if (
        "college_id" not in session
        or session.get("user_type") != "student"
    ):
        return redirect(url_for("login"))

    college_id = session["college_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            college_id,
            food_item,
            quantity,
            total_price,
            order_time,
            status,
            estimated_time
        FROM orders
        WHERE college_id = %s
        ORDER BY order_time DESC, id DESC
        """,
        (college_id,)
    )

    orders = cursor.fetchall()

    for order in orders:

        if order["total_price"] is not None:
            order["total_price"] = float(order["total_price"])

        if order["order_time"] is not None:
            order["order_time"] = order["order_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        cursor.execute(
            """
            SELECT
                id,
                order_id,
                food_item,
                quantity,
                price,
                status
            FROM order_items
            WHERE order_id = %s
            ORDER BY id ASC
            """,
            (order["id"],)
        )

        items = cursor.fetchall()

        for item in items:

            if item["price"] is not None:
                item["price"] = float(item["price"])

        order["items"] = items

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "orders": orders
    })


# =========================
# FACULTY DASHBOARD
# =========================

@app.route("/faculty")
def faculty():

    if (
        "college_id" not in session
        or session.get("user_type") != "faculty"
    ):
        return redirect(url_for("login"))

    return render_template("faculty.html")


# =========================
# FACULTY ORDERS
# =========================

@app.route("/faculty_orders")
def faculty_orders():

    if (
        "college_id" not in session
        or session.get("user_type") != "faculty"
    ):
        return redirect(url_for("login"))

    college_id = session["college_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            college_id,
            food_item,
            quantity,
            total_price,
            order_time,
            status,
            estimated_time
        FROM orders
        WHERE college_id = %s
        ORDER BY order_time DESC, id DESC
        """,
        (college_id,)
    )

    orders = cursor.fetchall()

    for order in orders:

        if order["total_price"] is not None:
            order["total_price"] = float(order["total_price"])

        if order["order_time"] is not None:
            order["order_time"] = order["order_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        cursor.execute(
            """
            SELECT
                id,
                order_id,
                food_item,
                quantity,
                price,
                status
            FROM order_items
            WHERE order_id = %s
            ORDER BY id ASC
            """,
            (order["id"],)
        )

        items = cursor.fetchall()

        for item in items:

            if item["price"] is not None:
                item["price"] = float(item["price"])

        order["items"] = items

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "orders": orders
    })


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return redirect(url_for("login"))

    return render_template("admin.html")


# ==========================================================
# MENU
# ==========================================================

@app.route("/menu")
def menu():

    if "college_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            name,
            category,
            price,
            available
        FROM menu_items
        WHERE available = TRUE
        ORDER BY category, id
        """
    )

    menu_items = cursor.fetchall()

    for item in menu_items:

        if item["price"] is not None:
            item["price"] = float(item["price"])

    cursor.close()
    conn.close()

    return render_template(
        "menu.html",
        menu_items=menu_items
    )


# ==========================================================
# ADMIN MENU MANAGEMENT
# ==========================================================

@app.route("/admin_menu")
def admin_menu():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            name,
            category,
            price,
            available
        FROM menu_items
        ORDER BY category, id
        """
    )

    menu_items = cursor.fetchall()

    for item in menu_items:

        if item["price"] is not None:
            item["price"] = float(item["price"])

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "menu_items": menu_items
    })


# ==========================================================
# ADD MENU ITEM
# ==========================================================

@app.route("/admin_menu/add", methods=["POST"])
def add_menu_item():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    price = data.get("price")

    if not name or not category or price in [None, ""]:

        return jsonify({
            "success": False,
            "message": "Name, category and price are required."
        }), 400

    try:

        price = float(price)

        if price < 0:
            raise ValueError

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Invalid price."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO menu_items
        (
            name,
            category,
            price,
            available
        )
        VALUES
        (
            %s,
            %s,
            %s,
            TRUE
        )
        """,
        (name, category, price)
    )

    conn.commit()

    new_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Menu item added successfully.",
        "id": new_id
    })


# ==========================================================
# EDIT MENU ITEM
# ==========================================================

@app.route("/admin_menu/edit/<int:item_id>", methods=["POST"])
def edit_menu_item(item_id):

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    price = data.get("price")

    if not name or not category or price in [None, ""]:

        return jsonify({
            "success": False,
            "message": "Name, category and price are required."
        }), 400

    try:

        price = float(price)

        if price < 0:
            raise ValueError

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Invalid price."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id
        FROM menu_items
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if not item:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    cursor.execute(
        """
        UPDATE menu_items
        SET
            name = %s,
            category = %s,
            price = %s
        WHERE id = %s
        """,
        (
            name,
            category,
            price,
            item_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Menu item updated successfully."
    })


# ==========================================================
# CHANGE MENU ITEM AVAILABILITY
# ==========================================================

@app.route("/admin_menu/toggle/<int:item_id>", methods=["POST"])
def toggle_menu_item(item_id):

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            available
        FROM menu_items
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if not item:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    new_status = not bool(item["available"])

    cursor.execute(
        """
        UPDATE menu_items
        SET available = %s
        WHERE id = %s
        """,
        (
            new_status,
            item_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "available": new_status,
        "message": (
            "Item marked as available."
            if new_status
            else "Item marked as unavailable."
        )
    })


# ==========================================================
# DELETE MENU ITEM
# ==========================================================

@app.route("/admin_menu/delete/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id
        FROM menu_items
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if not item:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    cursor.execute(
        """
        DELETE FROM menu_items
        WHERE id = %s
        """,
        (item_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Menu item deleted successfully."
    })


# ==========================================================
# CART
# ==========================================================

@app.route("/cart")
def cart():

    if (
        "college_id" not in session
        or session.get("user_type") not in [
            "student",
            "faculty"
        ]
    ):
        return redirect(url_for("login"))

    return render_template("cart.html")


# ==========================================================
# PLACE ORDER
# ==========================================================

@app.route("/place_order", methods=["POST"])
def place_order():

    if (
        "college_id" not in session
        or session.get("user_type") not in [
            "student",
            "faculty"
        ]
    ):
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    if not data or "cart" not in data:

        return jsonify({
            "success": False,
            "message": "Cart is empty."
        }), 400

    cart_items = data["cart"]

    if not cart_items:

        return jsonify({
            "success": False,
            "message": "Cart is empty."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    total_price = 0
    total_quantity = 0
    validated_items = []

    try:

        for item in cart_items:

            item_id = item.get("id")
            quantity = item.get("quantity")

            if not item_id or not quantity:
                continue

            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                continue

            if quantity <= 0:
                continue

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    price,
                    available
                FROM menu_items
                WHERE id = %s
                """,
                (item_id,)
            )

            menu_item = cursor.fetchone()

            if not menu_item:
                continue

            if not menu_item["available"]:

                conn.rollback()
                cursor.close()
                conn.close()

                return jsonify({
                    "success": False,
                    "message": (
                        menu_item["name"]
                        + " is currently unavailable."
                    )
                }), 400

            price = float(menu_item["price"])

            item_total = price * quantity

            total_price += item_total
            total_quantity += quantity

            validated_items.append({
                "food_item": menu_item["name"],
                "quantity": quantity,
                "price": price
            })

        if not validated_items:

            conn.rollback()
            cursor.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "No valid items in cart."
            }), 400

        # Create ONE main order
        cursor.execute(
            """
            INSERT INTO orders
            (
                college_id,
                food_item,
                quantity,
                total_price,
                status,
                estimated_time
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'Pending',
                NULL
            )
            """,
            (
                session["college_id"],
                "Multiple Items",
                total_quantity,
                total_price
            )
        )

        order_id = cursor.lastrowid

        # Insert each food item
        for item in validated_items:

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    food_item,
                    quantity,
                    price,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'Pending'
                )
                """,
                (
                    order_id,
                    item["food_item"],
                    item["quantity"],
                    item["price"]
                )
            )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Order placed successfully.",
            "order_id": order_id
        })

    except Exception as e:

        conn.rollback()

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Failed to place order."
        }), 500


# ==========================================================
# ADMIN ACTIVE ORDERS
# ==========================================================

@app.route("/admin_orders")
def admin_orders():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            college_id,
            total_price,
            order_time,
            status,
            estimated_time
        FROM orders
        WHERE status NOT IN ('Completed', 'Cancelled')
        ORDER BY
            CASE
                WHEN status = 'Pending' THEN 0
                WHEN status = 'Preparing' THEN 1
                WHEN status = 'Ready' THEN 2
                ELSE 3
            END,
            order_time ASC,
            id ASC
        """
    )

    orders = cursor.fetchall()

    for order in orders:

        if order["total_price"] is not None:
            order["total_price"] = float(order["total_price"])

        if order["order_time"] is not None:
            order["order_time"] = order["order_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        cursor.execute(
            """
            SELECT
                id,
                order_id,
                food_item,
                quantity,
                price,
                status
            FROM order_items
            WHERE order_id = %s
            ORDER BY id ASC
            """,
            (order["id"],)
        )

        items = cursor.fetchall()

        for item in items:

            if item["price"] is not None:
                item["price"] = float(item["price"])

        order["items"] = items

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "orders": orders
    })


# ==========================================================
# UPDATE MAIN ORDER
# ==========================================================

@app.route("/update_order", methods=["POST"])
def update_order():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    order_id = data.get("order_id")
    status = data.get("status")
    estimated_time = data.get("estimated_time")

    if not order_id:

        return jsonify({
            "success": False,
            "message": "Order ID is required."
        }), 400

    allowed_statuses = [
        "Pending",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled"
    ]

    if status and status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message": "Invalid order status."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id
        FROM orders
        WHERE id = %s
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    if not order:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    if status:

        cursor.execute(
            """
            UPDATE orders
            SET
                status = %s,
                estimated_time = %s
            WHERE id = %s
            """,
            (
                status,
                estimated_time,
                order_id
            )
        )

        cursor.execute(
            """
            UPDATE order_items
            SET status = %s
            WHERE order_id = %s
            """,
            (
                status,
                order_id
            )
        )

    else:

        cursor.execute(
            """
            UPDATE orders
            SET estimated_time = %s
            WHERE id = %s
            """,
            (
                estimated_time,
                order_id
            )
        )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Order updated successfully."
    })


# ==========================================================
# UPDATE INDIVIDUAL ORDER ITEM
# ==========================================================

@app.route("/update_order_item", methods=["POST"])
def update_order_item():

    if (
        "college_id" not in session
        or session.get("user_type") != "admin"
    ):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    item_id = data.get("item_id")
    status = data.get("status")

    if not item_id or not status:

        return jsonify({
            "success": False,
            "message": "Item ID and status are required."
        }), 400

    allowed_statuses = [
        "Pending",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled"
    ]

    if status not in allowed_statuses:

        return jsonify({
            "success": False,
            "message": "Invalid status."
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT order_id
        FROM order_items
        WHERE id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if not item:

        cursor.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Order item not found."
        }), 404

    order_id = item["order_id"]

    # Update item status
    cursor.execute(
        """
        UPDATE order_items
        SET status = %s
        WHERE id = %s
        """,
        (
            status,
            item_id
        )
    )

    # Get all item statuses
    cursor.execute(
        """
        SELECT status
        FROM order_items
        WHERE order_id = %s
        """,
        (order_id,)
    )

    items = cursor.fetchall()

    statuses = [
        item["status"]
        for item in items
    ]

    # Determine overall order status
    if statuses and all(
        item_status == "Completed"
        for item_status in statuses
    ):

        overall_status = "Completed"

    elif statuses and all(
        item_status == "Cancelled"
        for item_status in statuses
    ):

        overall_status = "Cancelled"

    elif any(
        item_status in ["Ready", "Completed"]
        for item_status in statuses
    ):

        overall_status = "Ready"

    elif any(
        item_status == "Preparing"
        for item_status in statuses
    ):

        overall_status = "Preparing"

    else:

        overall_status = "Pending"

    cursor.execute(
        """
        UPDATE orders
        SET status = %s
        WHERE id = %s
        """,
        (
            overall_status,
            order_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Order item updated successfully.",
        "order_status": overall_status
    })


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)