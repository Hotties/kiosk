
# 키오스크 구성
#  # 해당 코드는 테스트 코드로, 키오스크의 행동은 전부 랜덤으로 한다.
# # 각 키오스크에 랜덤한 딜레이를 준다(희망사항)
# # 각 테이블에서 정보를 가져온다.
# # 버거 또는 음료 또는 사이드를 랜덤으로 선택
# # 버거를 선택할 경우 세트 메뉴로 변경할지 랜덤으로 선택
# # 세트 메뉴로 변경할 경우, 세트 메뉴에 포함된 음료 또는 사이드를 랜덤으로 선택
# # 포장 또는 매장 식사 랜덤으로 선택


## 같은 메뉴를 여러 개 주문할 수 있도록, 주문 내역을 딕셔너리로 저장하는 방식으로 변경 필요

import pymysql


class Kiosk:
    def __init__(self, name):
        self.switch = False  # 키오스크 ON/OFF 상태
        self.id = id(self)  # 고유 ID 생성
        self.name = name
        self.order = None  # 주문 내역 저장
        self.burger_menu = []  # 버거 메뉴 정보
        self.side_menu = []  # 사이드 메뉴 정보 
        self.drink_menu = []  # 음료 메뉴 정보
        self.set_menu = []  # 세트 메뉴 정보

    # ON, OFF 함수 구현
    # ON : 메뉴 정보를 DB에서 불러와서 저장하는 로직 구현 필요
    # OFF : 키오스크 종료 시 필요한 로직 구현 필요 (예: 리소스 정리 등)
    def on(self):
        # DB에서 메뉴 정보를 불러와서 저장하는 로직 구현 필요
        self.switch = True

        self.load_menus(None, None, None, None, None, None)  # DB에서 메뉴 정보를 불러와서 저장하는 로직 구현 필요
        pass  # DB에서 메뉴 정보를 불러오는 로직 구현 필요
    def off(self):
        # 키오스크 종료 시 필요한 로직 구현 필요 (예: 리소스 정리 등)
        self.order = None  # 주문 내역 초기화
        self.burger_menu = []  # 버거 메뉴 초기화
        self.side_menu = []  # 사이드 메뉴 초기화
        self.drink_menu = []  # 음료 메뉴 초기화
        self.set_menu = []  # 세트 메뉴 초기화
        
        self.switch = False
        pass  # 키오스크 종료 시 필요한 로직 구현 필요
    def load_menus(self, burger_menu, side_menu, drink_menu, set_menu, cur: pymysql.cursors.Cursor):
        # DB에서 메뉴 정보를 불러와서 저장하는 로직 구현 필요
        
        import db.sheet_handlers as create_sheet_handler
        
        burger_menu = create_sheet_handler("BURGER", cur)  
        side_menu = create_sheet_handler("SIDEMENU", cur)  
        drink_menu = create_sheet_handler("DRINK", cur)  
        set_menu = create_sheet_handler("SET_MENU", cur)

        burger_menu = list(burger_menu.load_db_data().values())  # 딕셔너리의 값들만 리스트로 추출
        side_menu = list(side_menu.load_db_data().values())  # 딕셔너리의 값들만 리스트로 추출
        drink_menu = list(drink_menu.load_db_data().values())  # 딕셔너리의 값들만 리스트로 추출
        set_menu = list(set_menu.load_db_data().values())  # 딕셔너리의 값들만 리스트로 추출

        self.burger_menu = burger_menu
        self.side_menu = side_menu
        self.drink_menu = drink_menu
        self.set_menu = set_menu


    #     pass
    
    # 랜덤 주문 생성
    def create_random_order(self):
        import random
        order = {}
        # 버거를 구매 안할 수도 있음.
        #order['burger'] = random.choice(self.burger_menu) if random.choice([True, False]) else None
        set_menu_included = False
        set_menu_included = random.choice([True, False])  # 세트 메뉴 포함 여부 랜덤 선택
        if set_menu_included is True:  # 세트 메뉴로 변경할지 랜덤 선택
            order['set_menu'] = random.choice(self.set_menu)
            # 세트 메뉴에 포함된 음료 또는 사이드 랜덤 선택
            if 'drink' in order['set_menu']:
                order['drink'] = random.choice(self.drink_menu)
            if 'side' in order['set_menu']:
                order['side'] = random.choice(self.side_menu)
        else:
            order['burger'] = random.choice(self.burger_menu) if random.choice([True, False]) else None
            order['side'] = random.choice(self.side_menu) if random.choice([True, False]) else None
            order['drink'] = random.choice(self.drink_menu) if random.choice([True, False]) else None 
        
        if order.get('burger') is  not None or order.get('side') is not None or order.get('drink') is not None or order.get('set_menu') is not None:
            # 주문이 하나라도 포함되어 있다면, 포장 또는 매장 식사 랜덤 선택
            order['dine_in'] = random.choice([True, False])  # 포장 또는 매장 식사 랜덤 선택
            self.save_order(order)
            self.order = order
    
    # 주문 내역을 db에 저장하는 메소드 (구현 필요)
    # 바로 DB에 저장을 하는 경우, 저장 후 엑셀파일을 업데이트해야함

    def save_order(self, order):

        # 매 주문마다 save를 진행
        # order_detail 테이블에 저장하는 로직 구현 필요
        
        from db.sheet_handlers import create_sheet_handler

        handler = create_sheet_handler("ORDER_DETAIL", None)  # DB 커서 전달 필요
        #self.orders.append(order)
        handler.insert_row(order)  
        

        pass  # DB 저장 로직 구현 필요
    # run(): 딜레이 추가 후 generate_order()와 save_order() 호출. (루프나 타이머로 반복 가능)
    def run(self):
        import time
        import random
        while True:
            self.create_random_order()
            time.sleep(random.uniform(1, 5))  # 1~5초 랜덤 딜레이