import random
import time
import pymysql
from pymysql.cursors import DictCursor

from db.connect_db import db_Connect
from db.sheet_handlers import create_sheet_handler

##

class Kiosk:
    def __init__(self, name: str, conn: pymysql.connections.Connection | None = None):
        self.kiosk_id = None
        self.name = name
        self.switch = False
        self.id = id(self)
        self.conn = conn
        self.cur: pymysql.cursors.Cursor | None = None
        self.order: dict | None = None
        self.burger_menu: list[dict] = []
        self.side_menu: list[dict] = []
        self.drink_menu: list[dict] = []
        self.set_menu: list[dict] = []

    def __repr__(self) -> str:
        return f"<Kiosk name={self.name!r} switch={self.switch} orders_loaded={len(self.burger_menu)} burgers>"

    def on(self, connect_if_missing: bool = True) -> None:
        if self.conn is None and connect_if_missing:
            self.conn = db_Connect()

        if self.conn is None:
            raise RuntimeError("DB 연결이 설정되지 않았습니다.")

        self.cur = self.conn.cursor(DictCursor)
        self.switch = True 
        self.kiosk_id = random.randint(1, 10)*100
        print(f"키오스크 '{self.name}'가 켜졌습니다. (ID: {self.kiosk_id})")
        self.load_menus()

    def off(self) -> None:
        self.order = None
        self.burger_menu = []
        self.side_menu = []
        self.drink_menu = []
        self.set_menu = []
        self.switch = False

        if self.cur is not None:
            self.cur.close()
            self.cur = None

        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def load_menus(self) -> None:
        if self.cur is None:
            raise RuntimeError("DB 커서가 열려 있지 않습니다. 먼저 on()을 호출하세요.")

        self.burger_menu = list(create_sheet_handler("BURGER", self.cur).load_db_data().values())
        self.side_menu = list(create_sheet_handler("SIDE_MENU", self.cur).load_db_data().values())
        self.drink_menu = list(create_sheet_handler("DRINK", self.cur).load_db_data().values())
        self.set_menu = list(create_sheet_handler("SET_MENU", self.cur).load_db_data().values())

    def _random_item(self, menu: list[dict]) -> dict | None:
        return random.choice(menu) if menu else None

    def create_random_order(self) -> dict | None:
        if not self.switch:
            raise RuntimeError("키오스크가 켜져 있지 않습니다. 먼저 on()을 호출하세요.")

        if not any([self.burger_menu, self.side_menu, self.drink_menu, self.set_menu]):
            raise RuntimeError("메뉴가 로드되지 않았습니다. load_menus()를 호출하거나 on()을 다시 실행하세요.")

        order: dict = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_number": self.kiosk_id, ## 한번 해보기
            "is_takeout": None,
            "burger": None,
            "side": None,
            "drink": None,
            "set_menu": None,
            "price": 0
        }

        #print(f"{self.burger_menu=}, {self.side_menu=}, {self.drink_menu=}, {self.set_menu=}")

        if random.choice([True, False]) and self.set_menu:
            order["set_menu"] = self._random_item(self.set_menu)
            order["price"] += order["set_menu"].get("price", 0)
            if self.drink_menu and self.side_menu:
                if random.choice([True, False]):
                    order["drink"] = self._random_item(self.drink_menu)
                    order["price"] += order["drink"].get("extra_charge", 0)
                else:
                    order["side"] = self._random_item(self.side_menu)
                    order["price"] += order["side"].get("extra_charge", 0)
            elif self.drink_menu:
                order["drink"] = self._random_item(self.drink_menu)
                order["price"] += order["drink"].get("extra_charge", 0)
            elif self.side_menu:
                order["side"] = self._random_item(self.side_menu)
                order["price"] += order["side"].get("extra_charge", 0)
        else:
            order["burger"] = self._random_item(self.burger_menu) if random.choice([True, False]) else None
            order["price"] += order["burger"].get("price", 0) if order["burger"] else 0
            order["side"] = self._random_item(self.side_menu) if random.choice([True, False]) else None
            order["price"] += order["side"].get("price", 0) if order["side"] else 0
            order["drink"] = self._random_item(self.drink_menu) if random.choice([True, False]) else None
            order["price"] += order["drink"].get("price", 0) if order["drink"] else 0

        if any([order["burger"], order["side"], order["drink"], order["set_menu"]]):
            order["is_takeout"] = random.choice([True, False])
            order["order_number"] += 1
            self.order = order
            print(f"키오스크 '{self.name}'에서 생성된 주문: {order['price']}\n")
            self.save_order(order)
            return order

        return None

    def _extract_id(self, item: dict | None, id_key: str) -> int | None:
        if item is None:
            return None
        if isinstance(item, dict):
            return item.get(id_key)
        return item

    def save_order(self, order: dict) -> None:
        if self.cur is None:
            raise RuntimeError("DB 커서가 열려 있지 않습니다. 먼저 on()을 호출하세요.")

        row = {
            "id" : None,
            "date": order.get("date"),
            "order_number": order.get("order_number"),
            "is_takeout": order.get("is_takeout"),
            "burger_id": self._extract_id(order.get("burger"), "burger_id"),
            "sidemenu_id": self._extract_id(order.get("side"), "sidemenu_id"),
            "drink_id": self._extract_id(order.get("drink"), "drink_id"),
            "set_menu_id": self._extract_id(order.get("set_menu"), "set_menu_id"),
            "price": order.get("price")
        }

        print(f"저장할 주문 데이터: {row}")

        handler = create_sheet_handler("ORDER_DETAIL", self.cur)
        handler.insert_row(row)
        if self.conn is not None:
            self.conn.commit()

    def run(self, max_orders: int | None = None, delay_range: tuple[float, float] = (1.0, 5.0)) -> None:
        created = 0
        while self.switch and (max_orders is None or created < max_orders):
            if self.create_random_order() is not None:
                created += 1
            time.sleep(random.uniform(*delay_range))


# if __name__ == "__main__":
#     kiosk = Kiosk("TestKiosk")
#     kiosk.on()
#     try:
#         kiosk.run(max_orders=5, delay_range=(0.5, 1.0))
#     finally:
#         kiosk.off()
