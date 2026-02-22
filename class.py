


## allergic = wheat, milk, tomato, soybeans, egg, beef, pork, chicken = 00000000

class Burger:
    def __init__(self):
        self.menu_name = self.menu_name
        self.price = self.price
        self.kcal = self.kcal
        self.allergic = self.allergic

class Side_menu:
    def __init__(self):
        self.menu_name = self.menu_name
        self.price = self.price
        self.kcal = self.kcal
        self.allergic = self.allergic
        self.is_upgradeable = self.is_upgradeable
        self.extra_charge = self.extra_charge

class Drink:
    def __init__(self):
        self.menu_name = self.menu_name
        self.price = self.price
        self.kcal = self.kcal
        self.is_upgradeable = self.is_upgradeable
        self.extra_charge = self.extra_charge

class Set_menu:
    def __init__(self):
        self.menu_name = self.menu_name
        self.burger_id = self.burger_id
        self.sidemenu_id = self.sidemenu_id
        self.drink_id = self.drink_id
        self.set_price = self.set_price


class Order_detail:
    def __init__(self):
        self.date = self.date
        self.burger_id = self.burger_id
        self.sidemenu_id = self.sidemenu_id
        self.drink_id = self.drink_id
        self.price = self.price
        