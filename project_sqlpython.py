import mysql.connector
class EcommerceApp:
    #constructor
    def __init__(self):
        self.current_user = None  # (this function is for login)Stores: {'id': int, 'name': str, 'role': str} jo login hai usko store karega 
                                  #starting me no login so current user is none 
    # ================= CLI MENUS =================
    def run(self):
        while True:                   #menu will run again and again until user exit
            if not self.current_user:                     #if user is not login
                print("\n===============================")
                print("   E-COMMERCE SYSTEM (CLI)     ")
                print("===============================")
                print("1. Browse Catalog")
                print("2. Login")
                print("3. Register")
                print("4. Exit")
                choice = input("Select an option (1-4): ").strip()

                if choice == '1':
                    self.view_products()
                elif choice == '2':
                    self.login()
                elif choice == '3':
                    self.register()
            else:                                    #if user is login
                
                #print(f"current_user {self.current_user}")
                print(f"\n--- Logged in as: {self.current_user['name']} [{self.current_user['role'].upper()}] ---")
                print("1. Browse Catalog")
                print("2. Add Item to Cart")
                print("3. View Cart")
                print("4. Checkout")
                print("5. Order History")
                
                if self.current_user['role'] == 'admin':
                    print("6. [Admin] Add New Product")
                    print("7. [Admin] View All Customer Orders")
                print("0. Logout")                  #ye customer,admin dono ke liye print hoga

                choice = input("Select an option: ").strip()  #in choice we have taken string'1' thats why input datatype

                if choice == '1':
                    self.view_products()
                elif choice == '2':
                    self.add_to_cart()
                elif choice == '3':
                    self.view_cart()
                elif choice == '4':
                    self.checkout()
                elif choice == '5':
                    self.view_order_history()
                elif choice=='0':
                    self.logout()
                elif choice=='6':
                    self.admin_add_product()
    def get_db(self):
         conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
         return conn
            
  # ================= CATALOG & CART =================
    def view_products(self):       # Database open => SELECT*... => Data fetch => print product
        print("\n" + "="*70)
        print(f"{'ID':<5}{'Product Name':<30}{'Category':<15}{'Price (INR)':<12}{'Stock':<8}")
        print("="*70)
        #conn = mysql.connector.connect(host="localhost",user="root",password="root",database="cli_ecommerce_db")
        conn=self.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY id ASC")
        products = cursor.fetchall()
        cursor.close()
        conn.close()

        if not products:
            print("Catalog is empty.")
            return

        for p in products:
            print(f"{p['id']:<5}{p['name']:<30}{p['category']:<15}₹{float(p['price']):<11.2f}{p['stock']:<8}")
        print("="*70)
# ================= AUTHENTICATION =================
    def register(self):
        print("\n--- Register New User ---")
        name = input("Enter Full Name: ").strip()
        email = input("Enter Email: ").strip()
        #pwd = getpass.getpass("Enter Password: ")
        pwd=input("enter password")

        if not name or not email or not pwd:
            print("[!] All fields are required.")
            return

        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")

        cursor = conn.cursor(dictionary=True)
        try:                                                                   #first it will check email
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print("[!] Email is already registered. Please login.")
                return

            #hashed = hash_password(pwd)
            cursor.execute(                                                          #after email checking
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, 'abc')
            )
            conn.commit()
            print("[+] Registration successful! You can now login.")
        except mysql.connector.Error as err:
            print(f"[!] Database Error: {err}")
        finally:
            cursor.close()
            conn.close()
#---------------------------------------------------------------------------------------------        
    def login(self):
        print("\n--- Login ---")
        email = input("Email: ").strip()
        pwd = input("enter password")

        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and user['password_hash'] == pwd:
                self.current_user = {
                    "id": user['id'],
                    "name": user['name'],
                    "role": user['role']                #if the password is match it saves in current_user
                }
                print(f"\n[+] Welcome back, {user['name']}! (Role: {user['role']})")
            else:
                print("[!] Invalid email or password.")
        finally:
            cursor.close()
            conn.close()
#----------------------------------------------------------------------------------------
    def add_to_cart(self):
        self.view_products()
        try:
            prod_id = int(input("\nEnter Product ID to add: "))   #take pro_id and quantity from user
            qty = int(input("Enter Quantity: "))
            if qty <= 0:
                print("[!] Quantity must be at least 1.")
                return
        except ValueError:
            print("[!] Invalid input. Numbers only.")
            return

        #conn = get_db()
        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT stock FROM products WHERE id = %s", (prod_id,))
            product = cursor.fetchone()
            if not product:
                print("[!] Product not found.")
                return
            if product['stock'] < qty:
                print(f"[!] Insufficient stock. Only {product['stock']} available.")
                return

            cursor.execute("""
                INSERT INTO cart_items (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """, (self.current_user['id'], prod_id, qty, qty))
            conn.commit()
            print("[+] Item added to cart successfully.")
        finally:
            cursor.close()
            conn.close()
#--------------------------------------------------------------------------------------------
    def view_cart(self): #it needs cart_items(it containis only ids,quantity noname)so +product  to get name
        #conn = get_db()
        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ci.product_id, p.name, p.price, ci.quantity, (p.price * ci.quantity) as subtotal
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = %s
        """, (self.current_user['id'],))
        items = cursor.fetchall()
        cursor.close()
        conn.close()

        print("\n" + "-"*65)
        print(f"{'PID':<6}{'Product Name':<30}{'Price':<10}{'Qty':<6}{'Subtotal':<10}")
        print("-"*65)
        if not items:
            print("Your cart is empty.")
            print("-"*65)
            return False

        total = 0
        for item in items:
            total += float(item['subtotal'])
            print(f"{item['product_id']:<6}{item['name']:<30}₹{float(item['price']):<9.2f}{item['quantity']:<6}₹{float(item['subtotal']):<9.2f}")
        print("-"*65)
        print(f"Total Cart Value: ₹{total:.2f}")
        print("-"*65)
        return True

#============================== ORDERS & CHECKOUT===============================================
    def checkout(self):
        if not self.view_cart(): #checks the cart
            return

        confirm = input("\nProceed to checkout? (y/n): ").strip().lower() #if product is available
        if confirm != 'y':
            print("Checkout canceled.")
            return

        address = input("Enter Delivery Address: ").strip()
        if not address:
            print("[!] Delivery address cannot be empty.")
            return

        #conn = get_db()
        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor(dictionary=True)

        try:
            # Atomic Transaction: lock rows, verify stock, create order, deduct stock
            conn.start_transaction()

            cursor.execute("""
                SELECT ci.product_id, ci.quantity, p.price, p.stock
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.user_id = %s FOR UPDATE
            """, (self.current_user['id'],))
            items = cursor.fetchall()

            if not items:
                conn.rollback()
                print("[!] Cart is empty.")
                return

            total_amount = 0
            for item in items:
                if item['stock'] < item['quantity']:
                    conn.rollback()
                    print(f"[!] Checkout failed: Item ID {item['product_id']} has insufficient stock.")
                    return
                total_amount += float(item['price']) * item['quantity']

            # Insert master order
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount, delivery_address) VALUES (%s, %s, %s)",
                (self.current_user['id'], total_amount, address)
            )
            order_id = cursor.lastrowid

            # Insert line items and update inventory
            for item in items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, item['product_id'], item['quantity'], item['price'])
                )
                cursor.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
                )

            # Clear cart
            cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (self.current_user['id'],))

            conn.commit()
            print(f"\n[+] Order #{order_id} placed successfully! Total Paid: ₹{total_amount:.2f}")

        except Exception as e:
            conn.rollback()
            print(f"[!] Order processing error: {e}")
        finally:
            cursor.close()
            conn.close()
#-------------------------------------------------------------------------------
    def view_order_history(self):
        #conn = get_db()
        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, o.total_amount, o.status, o.created_at,
                   GROUP_CONCAT(CONCAT(p.name, ' (x', oi.quantity, ')') SEPARATOR ', ') as items
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """, (self.current_user['id'],))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()

        print("\n--- Your Order History ---")
        if not orders:
            print("No previous orders found.")
            return

        for o in orders:
            print(f"\nOrder ID: #{o['id']} | Date: {o['created_at']} | Status: {o['status']}")
            print(f"Items: {o['items']}")
            print(f"Total Amount: ₹{float(o['total_amount']):.2f}")
            print("-" * 50)

# ================================= ADMIN MODULE ==================================================
    def admin_add_product(self):
        if self.current_user.get('role') != 'admin':   #check admin if admin is available then proceed
            print("[!] Unauthorized access.")
            return

        print("\n--- Add New Product ---")
        name = input("Product Name: ").strip()
        category = input("Category: ").strip()
        try:
            price = float(input("Price (INR): "))
            stock = int(input("Stock Quantity: "))
        except ValueError:
            print("[!] Invalid numerical values for price or stock.")
            return

        #conn = get_db()
        conn = mysql.connector.connect(host="127.0.0.1", user="root",password="sa123",database="ecommerce_db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, category, price, stock) VALUES (%s, %s, %s, %s)",
            (name, category, price, stock)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[+] Product '{name}' added successfully.")
    

#--------------------------------------------------------
    def logout(self):
        self.current_user = None
        print("[+] Logged out successfully.")
            
#-------------------------------------------------------
ecom=EcommerceApp()    # it is the object of class                         
ecom.run()