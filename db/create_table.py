import pymysql.cursors

def create_version(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS VERSION(
                version_code INT
            )    
    """)

def create_burger(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS BURGER(
            id INT AUTO_INCREMENT,
            menu_name VARCHAR(50),
            price INT,
            kcal INT,
            allergic TINYINT,
            PRIMARY KEY(INT)
            )
    """)

def create_side_menu(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS SIDEMENU(
                id INT AUTO_INCREMENT,
                menu_name VARCHAR(50),
                price INT,
                kcal INT,
                allergic TINYINT,
                is_upgradeable BOOLEAN,
                extra_charge INT,
                PRIMARY KEY(INT)
                )
    
""")

def create_drink(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS DRINK(
                id INT AUTO_INCREMENT,
                menu_name VARCHAR(50),
                price INT,
                kcal INT,
                is_upgradeable BOOLEAN,
                extra_charge INT,
                PRIMARY KEY(id)
                )
""")

def create_set_menu(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS SET_MENU(
                id INT,
                menu_name VARCHAR(50),
                burger_id INT,
                sidemenu_id INT,
                drink_id INT,
                price INT,
                FOREIGN KEY (burger_id) REFERENCES BURGER(burger_id),
                FOREIGN KEY (sidemenu_id) REFERENCES SIDEMENU(sidemenu_id),
                FOREIGN KEY (drink_id) REFERENCES DRINK(drink_id),
                PRIMARY KEY (id)
                )

""")

def create_order_detail(cur : pymysql.cursors.Cursor):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ORDER_DETAIL(
                id INT,
                date DATETIME,
                order_number INT,
                is_takeout BOOLEAN,
                burger_id INT,
                sidemenu_id INT,
                drink_id INT,
                price INT,
                FOREIGN KEY (burger_id) REFERENCES BURGER(burger_id),
                FOREIGN KEY (sidemenu_id) REFERENCES SIDEMENU(sidemenu_id),
                FOREIGN KEY (drink_id) REFERENCES DRINK(drink_id),
                PRIMARY KEY (id)
                )

""")