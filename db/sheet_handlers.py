"""
시트별 핸들러 클래스 모듈
각 시트의 테이블 구조와 데이터베이스 작업을 캡슐화
"""

import pymysql
from abc import ABC, abstractmethod
from enum import Enum, auto


class SheetName(Enum):
    """지원하는 시트 이름"""
    VERSION = auto()
    BURGER = auto()
    SIDEMENU = auto()
    DRINK = auto()
    SET_MENU = auto()
    ORDER_DETAIL = auto()


class SheetHandler(ABC):
    """
    모든 시트 핸들러의 추상 기반 클래스
    공통 로직: DB 데이터 로드, 쿼리 구성
    """

    def __init__(self, cur: pymysql.cursors.Cursor):
        self.cur = cur

    @abstractmethod
    def get_table_name(self) -> str:
        """테이블 이름 반환"""
        pass

    @abstractmethod
    def get_id_column(self) -> str:
        """ID 컬럼명 반환"""
        pass

    @abstractmethod
    def get_columns(self) -> list[str]:
        """모든 컬럼명 반환 (ID 포함)"""
        pass

    def load_db_data(self) -> dict:
        """
        DB에서 현재 데이터를 로드 (ID를 키로 하는 딕셔너리)
        공통 로직이므로 구현됨
        """
        try:
            query = f"SELECT * FROM {self.get_table_name()}"
            self.cur.execute(query)
            rows = self.cur.fetchall()
            
            # 컬럼명 추출
            columns = [desc[0] for desc in self.cur.description]
            
            # {ID: {컬럼명: 값, ...}} 형태의 딕셔너리 반환
            # ex) {1: {"burger_id": 1, "burger_name": "치즈버거", "burger_price": 5000}, ...}
            db_data = {}
            for row in rows:
                row_dict = dict(zip(columns, row))
                row_id = row_dict[self.get_id_column()]
                db_data[row_id] = row_dict
            return db_data
        except pymysql.MySQLError as e:
            raise Exception(f"[{self.get_table_name()}] DB 데이터 로드 실패: {e}")

    def insert_row(self, row: dict):
        """행 삽입 (공통 로직)""" 
        try:
            cols = self.get_columns()
            placeholders = ', '.join(['%s'] * len(cols))
            query = f"INSERT INTO {self.get_table_name()} ({', '.join(cols)}) VALUES ({placeholders})"
            values = [row.get(col) for col in cols]
            self.cur.execute(query, tuple(values))
        except pymysql.MySQLError as e:
            raise Exception(f"[{self.get_table_name()}] 행 삽입 실패: {e}")

    def update_row(self, row: dict):
        """행 업데이트 (ID 제외한 필드 업데이트)"""
        try:
            id_col = self.get_id_column()
            cols = [c for c in self.get_columns() if c != id_col]
            set_clause = ', '.join([f"{col} = %s" for col in cols])
            query = f"UPDATE {self.get_table_name()} SET {set_clause} WHERE {id_col} = %s"
            values = [row.get(col) for col in cols] + [row.get(id_col)]
            self.cur.execute(query, tuple(values))
        except pymysql.MySQLError as e:
            raise Exception(f"[{self.get_table_name()}] 행 업데이트 실패: {e}")

    def delete_row(self, row_id):
        """행 삭제 (공통 로직)"""
        try:
            query = f"DELETE FROM {self.get_table_name()} WHERE {self.get_id_column()} = %s"
            self.cur.execute(query, (row_id,))
        except pymysql.MySQLError as e:
            raise Exception(f"[{self.get_table_name()}] 행 삭제 실패: {e}")


class VersionHandler(SheetHandler):
    """VERSION 시트 핸들러"""

    def get_table_name(self) -> str:
        return "version"

    def get_id_column(self) -> str:
        return "version_code"

    def get_columns(self) -> list[str]:
        return ["version_code"]


class BurgerHandler(SheetHandler):
    """BURGER 시트 핸들러"""

    def get_table_name(self) -> str:
        return "burger"

    def get_id_column(self) -> str:
        return "burger_id"

    def get_columns(self) -> list[str]:
        return ["burger_id", "burger_name", "burger_price"]


class SidemenuHandler(SheetHandler):
    """SIDEMENU 시트 핸들러"""

    def get_table_name(self) -> str:
        return "sidemenu"

    def get_id_column(self) -> str:
        return "sidemenu_id"

    def get_columns(self) -> list[str]:
        return ["sidemenu_id", "sidemenu_name", "sidemenu_price"]


class DrinkHandler(SheetHandler):
    """DRINK 시트 핸들러"""

    def get_table_name(self) -> str:
        return "drink"

    def get_id_column(self) -> str:
        return "drink_id"

    def get_columns(self) -> list[str]:
        return ["drink_id", "drink_name", "drink_price"]


class SetMenuHandler(SheetHandler):
    """SET_MENU 시트 핸들러"""

    def get_table_name(self) -> str:
        return "set_menu"

    def get_id_column(self) -> str:
        return "set_menu_id"

    def get_columns(self) -> list[str]:
        return ["set_menu_id", "set_menu_name", "set_menu_price"]


class OrderDetailHandler(SheetHandler):
    """ORDER_DETAIL 시트 핸들러"""

    def get_table_name(self) -> str:
        return "order_detail"

    def get_id_column(self) -> str:
        return "order_id"

    def get_columns(self) -> list[str]:
        return ["order_id", "burger_id", "sidemenu_id", "drink_id", "set_menu_id"]


def create_sheet_handler(sheet_name: str, cur: pymysql.cursors.Cursor) -> SheetHandler:
    """
    팩토리 함수: sheet_name에 따라 적절한 핸들러 생성
    
    Args:
        sheet_name: SheetName enum의 name 속성
        cur: 데이터베이스 커서
    
    Returns:
        해당 시트의 핸들러 인스턴스
    
    Raises:
        ValueError: 지원하지 않는 시트명인 경우
    """
    handlers = {
        SheetName.VERSION.name: VersionHandler,
        SheetName.BURGER.name: BurgerHandler,
        SheetName.SIDEMENU.name: SidemenuHandler,
        SheetName.DRINK.name: DrinkHandler,
        SheetName.SET_MENU.name: SetMenuHandler,
        SheetName.ORDER_DETAIL.name: OrderDetailHandler,
    }

    handler_class = handlers.get(sheet_name)
    if not handler_class:
        raise ValueError(f"지원하지 않는 시트명: {sheet_name}")

    return handler_class(cur)
