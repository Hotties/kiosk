"""
개선된 Kiosk 클래스 (kiosk.py 기반)
멀티스레딩 환경에서 안전하게 작동하도록 개선됨
"""

import random
import time
import pymysql
from pymysql.cursors import DictCursor

from db.connect_db import db_Connect
from db.sheet_handlers import create_sheet_handler


class Kiosk:
    """
    개선된 키오스크 클래스
    - 타입 힌트 추가
    - DB 연결 관리 개선
    - 메뉴 로딩 로직 최적화
    """

    def __init__(self, name: str, conn: pymysql.connections.Connection | None = None):
        """
        키오스크 초기화
        
        Args:
            name: 키오스크 이름
            conn: 데이터베이스 연결 (선택사항)
        """
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
        """문자열 표현"""
        return f"<Kiosk name={self.name!r} switch={self.switch} orders_loaded={len(self.burger_menu)} burgers>"

    def on(self, connect_if_missing: bool = True) -> None:
        """
        키오스크 전원 ON
        DB 연결을 설정하고 메뉴를 로드합니다.
        
        Args:
            connect_if_missing: True면 연결이 없을 시 새로 생성
        
        Raises:
            RuntimeError: 연결이 설정되지 않은 경우
        """
        if self.conn is None and connect_if_missing:
            self.conn = db_Connect()

        if self.conn is None:
            raise RuntimeError("DB 연결이 설정되지 않았습니다.")

        self.cur = self.conn.cursor(DictCursor)
        self.switch = True
        self.load_menus()

    def off(self) -> None:
        """
        키오스크 전원 OFF
        모든 메뉴와 주문 정보를 초기화합니다.
        """
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
        """
        DB에서 모든 메뉴 정보를 로드합니다.
        
        Raises:
            RuntimeError: 커서가 열려 있지 않은 경우
        """
        if self.cur is None:
            raise RuntimeError("DB 커서가 열려 있지 않습니다. 먼저 on()을 호출하세요.")

        try:
            self.burger_menu = list(create_sheet_handler("BURGER", self.cur).load_db_data().values())
            self.side_menu = list(create_sheet_handler("SIDEMENU", self.cur).load_db_data().values())
            self.drink_menu = list(create_sheet_handler("DRINK", self.cur).load_db_data().values())
            self.set_menu = list(create_sheet_handler("SET_MENU", self.cur).load_db_data().values())
        except Exception as e:
            raise RuntimeError(f"메뉴 로드 실패: {e}")

    def _random_item(self, menu: list[dict]) -> dict | None:
        """
        메뉴에서 랜덤으로 항목 선택
        
        Args:
            menu: 메뉴 리스트
        
        Returns:
            선택된 메뉴 또는 None
        """
        return random.choice(menu) if menu else None

    def create_random_order(self) -> dict | None:
        """
        랜덤 주문을 생성합니다.
        
        Returns:
            생성된 주문 딕셔너리 또는 None (주문이 없는 경우)
        
        Raises:
            RuntimeError: 키오스크가 꺼진 경우 또는 메뉴가 로드되지 않은 경우
        """
        if not self.switch:
            raise RuntimeError("키오스크가 켜져 있지 않습니다. 먼저 on()을 호출하세요.")

        if not any([self.burger_menu, self.side_menu, self.drink_menu, self.set_menu]):
            raise RuntimeError("메뉴가 로드되지 않았습니다. load_menus()를 호출하거나 on()을 다시 실행하세요.")

        order: dict = {
            "burger": None,
            "side": None,
            "drink": None,
            "set_menu": None,
            "dine_in": None,
            "price": 0
        }

        # 세트 메뉴 또는 개별 메뉴 선택
        if random.choice([True, False]) and self.set_menu:
            order["set_menu"] = self._random_item(self.set_menu)
            order["price"] += order["set_menu"].get("set_menu_price", 0) if order["set_menu"] else 0
            
            # 세트에 추가 옵션 선택
            if self.drink_menu and self.side_menu:
                if random.choice([True, False]):
                    order["drink"] = self._random_item(self.drink_menu)
                    order["price"] += order["drink"].get("drink_price", 0) if order["drink"] else 0
                else:
                    order["side"] = self._random_item(self.side_menu)
                    order["price"] += order["side"].get("sidemenu_price", 0) if order["side"] else 0
            elif self.drink_menu:
                order["drink"] = self._random_item(self.drink_menu)
                order["price"] += order["drink"].get("drink_price", 0) if order["drink"] else 0
            elif self.side_menu:
                order["side"] = self._random_item(self.side_menu)
                order["price"] += order["side"].get("sidemenu_price", 0) if order["side"] else 0
        else:
            # 개별 메뉴 선택
            order["burger"] = self._random_item(self.burger_menu) if random.choice([True, False]) else None
            order["price"] += order["burger"].get("burger_price", 0) if order["burger"] else 0
            
            order["side"] = self._random_item(self.side_menu) if random.choice([True, False]) else None
            order["price"] += order["side"].get("sidemenu_price", 0) if order["side"] else 0
            
            order["drink"] = self._random_item(self.drink_menu) if random.choice([True, False]) else None
            order["price"] += order["drink"].get("drink_price", 0) if order["drink"] else 0

        # 주문이 하나 이상 포함되어 있는 경우
        if any([order["burger"], order["side"], order["drink"], order["set_menu"]]):
            order["dine_in"] = random.choice([True, False])
            self.order = order
            self.save_order(order)
            return order

        return None

    def _extract_id(self, item: dict | None, id_key: str) -> int | None:
        """
        항목에서 ID 추출
        
        Args:
            item: 메뉴 항목
            id_key: ID 키 이름
        
        Returns:
            추출된 ID 또는 None
        """
        if item is None:
            return None
        if isinstance(item, dict):
            return item.get(id_key)
        return item

    def save_order(self, order: dict) -> None:
        """
        주문을 DB에 저장합니다.
        
        Args:
            order: 저장할 주문 딕셔너리
        
        Raises:
            RuntimeError: 커서가 열려 있지 않은 경우
        """
        if self.cur is None:
            raise RuntimeError("DB 커서가 열려 있지 않습니다. 먼저 on()을 호출하세요.")

        row = {
            "order_id": None,
            "burger_id": self._extract_id(order.get("burger"), "burger_id"),
            "sidemenu_id": self._extract_id(order.get("side"), "sidemenu_id"),
            "drink_id": self._extract_id(order.get("drink"), "drink_id"),
            "set_menu_id": self._extract_id(order.get("set_menu"), "set_menu_id"),
        }

        try:
            handler = create_sheet_handler("ORDER_DETAIL", self.cur)
            handler.insert_row(row)
            if self.conn is not None:
                self.conn.commit()
        except Exception as e:
            if self.conn is not None:
                self.conn.rollback()
            raise RuntimeError(f"주문 저장 실패: {e}")

    def run(self, max_orders: int | None = None, delay_range: tuple[float, float] = (1.0, 5.0)) -> None:
        """
        키오스크를 실행하여 주문을 계속 생성합니다.
        
        Args:
            max_orders: 최대 주문 수 (None이면 무한)
            delay_range: 주문 간 딜레이 범위 (최소, 최대)
        """
        created = 0
        while self.switch and (max_orders is None or created < max_orders):
            if self.create_random_order() is not None:
                created += 1
            time.sleep(random.uniform(*delay_range))


# if __name__ == "__main__":
#     # 테스트 코드
#     kiosk = Kiosk("TestKiosk")
#     kiosk.on()
#     try:
#         kiosk.run(max_orders=5, delay_range=(0.5, 1.0))
#     finally:
#         kiosk.off()
