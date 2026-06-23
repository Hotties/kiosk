"""
데이터 모델 클래스 정의
메뉴 항목, 주문 관련 클래스들을 타입 안전하게 정의
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Burger:
    """버거 메뉴 데이터 모델"""
    burger_id: int
    burger_name: str
    burger_price: int
    kcal: Optional[int] = None
    allergic: Optional[str] = None  # 비트마스크: wheat, milk, tomato, soybeans, egg, beef, pork, chicken

    def __str__(self) -> str:
        return f"{self.burger_name} (₩{self.burger_price:,})"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "burger_id": self.burger_id,
            "burger_name": self.burger_name,
            "burger_price": self.burger_price,
            "kcal": self.kcal,
            "allergic": self.allergic,
        }


@dataclass
class side_menu:
    """사이드 메뉴 데이터 모델"""
    side_menu_id: int
    side_menu_name: str
    side_menu_price: int
    kcal: Optional[int] = None
    allergic: Optional[str] = None
    is_upgradeable: bool = False  # 업그레이드 가능 여부
    extra_charge: int = 0  # 업그레이드 시 추가 요금

    def __str__(self) -> str:
        charge_str = f" (+₩{self.extra_charge:,})" if self.extra_charge > 0 else ""
        return f"{self.side_menu_name} (₩{self.side_menu_price:,}){charge_str}"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "side_menu_id": self.side_menu_id,
            "side_menu_name": self.side_menu_name,
            "side_menu_price": self.side_menu_price,
            "kcal": self.kcal,
            "allergic": self.allergic,
            "is_upgradeable": self.is_upgradeable,
            "extra_charge": self.extra_charge,
        }


@dataclass
class Drink:
    """음료 메뉴 데이터 모델"""
    drink_id: int
    drink_name: str
    drink_price: int
    kcal: Optional[int] = None
    is_upgradeable: bool = False  # 업그레이드 가능 여부 (예: 사이즈 업그레이드)
    extra_charge: int = 0  # 업그레이드 시 추가 요금

    def __str__(self) -> str:
        charge_str = f" (+₩{self.extra_charge:,})" if self.extra_charge > 0 else ""
        return f"{self.drink_name} (₩{self.drink_price:,}){charge_str}"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "drink_id": self.drink_id,
            "drink_name": self.drink_name,
            "drink_price": self.drink_price,
            "kcal": self.kcal,
            "is_upgradeable": self.is_upgradeable,
            "extra_charge": self.extra_charge,
        }


@dataclass
class SetMenu:
    """세트 메뉴 데이터 모델"""
    set_menu_id: int
    set_menu_name: str
    burger_id: Optional[int] = None
    side_menu_id: Optional[int] = None
    drink_id: Optional[int] = None
    set_menu_price: int = 0

    def __str__(self) -> str:
        return f"{self.set_menu_name} (₩{self.set_menu_price:,})"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "set_menu_id": self.set_menu_id,
            "set_menu_name": self.set_menu_name,
            "burger_id": self.burger_id,
            "side_menu_id": self.side_menu_id,
            "drink_id": self.drink_id,
            "set_menu_price": self.set_menu_price,
        }


@dataclass
class OrderDetail:
    """주문 상세 데이터 모델"""
    order_id: Optional[int] = None
    burger_id: Optional[int] = None
    side_menu_id: Optional[int] = None
    drink_id: Optional[int] = None
    set_menu_id: Optional[int] = None
    order_date: Optional[str] = None  # YYYY-MM-DD HH:MM:SS
    dine_in: Optional[bool] = None  # True: 매장, False: 포장
    total_price: int = 0

    def __str__(self) -> str:
        items = []
        if self.burger_id:
            items.append(f"Burger(ID:{self.burger_id})")
        if self.side_menu_id:
            items.append(f"Side(ID:{self.side_menu_id})")
        if self.drink_id:
            items.append(f"Drink(ID:{self.drink_id})")
        if self.set_menu_id:
            items.append(f"SetMenu(ID:{self.set_menu_id})")

        dine_type = "매장식사" if self.dine_in else "포장"
        return f"Order(ID:{self.order_id}) [{', '.join(items)}] {dine_type} ₩{self.total_price:,}"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "order_id": self.order_id,
            "burger_id": self.burger_id,
            "side_menu_id": self.side_menu_id,
            "drink_id": self.drink_id,
            "set_menu_id": self.set_menu_id,
            "order_date": self.order_date,
            "dine_in": self.dine_in,
            "total_price": self.total_price,
        }
