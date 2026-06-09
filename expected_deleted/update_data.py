import pandas as pd
import pymysql
from enum import Enum, auto

class SheetName(Enum):
    VERSION = auto()
    BURGER = auto()
    SIDEMENU = auto()
    DRINK = auto()
    SET_MENU = auto()
    ORDER_DETAIL = auto()

def update_data(cur: pymysql.cursors.Cursor, conn: pymysql.Connection):

    # 0. 여기서 

    # 1. version 테이블에서 verion_code 가져오기
    version_code = get_version_code(cur, conn)
    
    
    # 2. excel 파일에서 version_code 가져오기
    if version_code == -1:
        excel_version_code = get_excel_version_code()  # 이 함수는 excel 파일에서 version_code를 읽어오는 함수로 구현해야 함
    
    # 3. version_code 비교하기
    if version_code != excel_version_code or version_code == -1:
        # 4. version_code가 다르면, excel 파일에서 데이터 가져와서 DB에 업데이트하기
        datasheets = get_data_from_excel()  # 이 함수는 excel 파일에서 데이터를 읽어오는 함수로 구현해야 함
        
        # 4-2. DB에 업데이트하기
        for sheet_name, sheet in datasheets.items(): ## version, burger, sidemenu, drink, set_menu, order_detail 시트를 순환
            update_or_insert_data(cur, sheet_name, sheet, version_code)  # 이 함수는 sheet이 DB에 존재하는지 확인하고, 존재하면 update, 존재하지 않으면 insert 하는 함수로 구현해야 함
        
        # version 테이블의 version_code 업데이트
        update_version_code(cur, conn, excel_version_code)  # 이 함수는 version 테이블의 version_code를 업데이트하는 함수로 구현해야 함

## 1. version 테이블에서 verion_code 가져오기
def get_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection):
    
    # 만약 version 테이블이 없으면 version_code는 -1로 설정

    try:    
        query = "SELECT version_code FROM version"
        cur.execute(query)
        conn.commit()
        result = cur.fetchone()
        if result:
            return result[0]  # version_code 반환
        else:
            return -1
    except pymysql.MySQLError as e:
        raise Exception(f"[get_version_code] DB 조회 실패: {e}")


## 2. excel 파일에서 version_code 가져오기
def get_excel_version_code():
    # 이 함수는 excel 파일에서 version_code를 읽어오는 함수로 구현해야 함
    # 예시로 pandas를 사용하여 excel 파일에서 version_code를 읽어오는 방법을 보여줍니다.
    try:
        df = pd.read_excel('data.xlsx', sheet_name=SheetName.VERSION.name)  # 엑셀 파일 경로와 시트 이름
        version_code = df['version_code'][0]  # version_code가 있는 열과 행을 지정
        return version_code
    except Exception as e:
        raise Exception(f"[get_excel_version_code] Excel 파일에서 version_code 읽기 실패: {e}")
    
## 4. version_code가 다르면, excel 파일에서 데이터 가져와서 DB에 업데이트하기
## 4-1. excel 파일에서 데이터 가져오기
def get_data_from_excel():
    # 이 함수는 excel 파일에서 데이터를 읽어오는 함수로 구현해야 함
    # 예시로 pandas를 사용하여 excel 파일에서 데이터를 읽어오는 방법을 보여줍니다.
    try:
        df = pd.read_excel('data.xlsx', sheet_name=None)  # 엑셀 파일 경로와 시트 이름
        data = df.to_dict(orient='records')  # 데이터프레임을 딕셔너리 리스트로 변환
        return data
    except Exception as e:
        raise Exception(f"[get_data_from_excel] Excel 파일에서 데이터 읽기 실패: {e}")
    
## 4-1. excel 파일에서 데이터 가져오기
## 4-2. DB에 업데이트하기
def update_or_insert_data(cur: pymysql.cursors.Cursor, sheet_name: str, sheet: dict, version_code: int):
    ## version_code가 -1이면 sheet insert, version_code가 -1이 아니면 sheet update
    if version_code == -1:
        # sheet insert
        insert_sheet(cur, sheet_name,sheet)  # 이 함수는 sheet을 DB에 삽입하는 함수로 구현해야 함
    else:
        # sheet update
        update_sheet(cur, sheet_name, sheet)  # 이 함수는 sheet을 DB에 업데이트하는 함수로 구현해야 함

def insert_sheet(cur: pymysql.cursors.Cursor, sheet_name: str, sheet: dict):## version, burger, sidemenu, drink, set_menu, order_detail 시트를 순환
    # 이미 딕셔너리
    # 이 함수는 sheet을 DB에 삽입하는 함수로 구현해야 함
    # 이 함수는 시트 전체를 삽입하는 함수
    # 시트 제목을 기준으로 조건문을 생성
    # if sheet['sheet_name'] == 'burger':
    #    #   for 반복문을 사용하여 sheet의 각 행을 DB에 삽입하는 쿼리 작성
  
    for row in sheet:
        insert_row(cur, sheet_name, row)  

    # if sheet_name == SheetName.VERSION.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row)  
    # elif sheet_name == SheetName.BURGER.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row)  
    # elif sheet_name == SheetName.SIDEMENU.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row) 
    # elif sheet_name == SheetName.DRINK.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row) 
    # elif sheet_name == SheetName.SET_MENU.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row)  
    # elif sheet_name == SheetName.ORDER_DETAIL.name:
    #     for row in sheet:
    #         insert_row(cur, sheet_name, row)  

def insert_row(cur: pymysql.cursors.Cursor, sheet_name: str, sheet: dict):
   
    # 시트 제목을 기준으로 조건문을 생성
    # if sheet_name == 'burger':
    #   #   insert 쿼리를 작성하여 sheet의 각 행을 DB에 삽입

    try:
        query = f"INSERT INTO {sheet_name} ({', '.join(sheet.keys())}) VALUES ({', '.join(['%s'] * len(sheet))})"
        cur.execute(query, tuple(sheet.values()))
    except pymysql.MySQLError as e:
        raise Exception(f"[insert_row] DB 삽입 실패: {e}")

    # if sheet_name == SheetName.VERSION.name:
    #     try:
    #         query = "INSERT INTO version (version_code) VALUES (%s)"
    #         cur.execute(query, (sheet['version_code']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}")
    # elif sheet_name == SheetName.BURGER.name:
    #     try:
    #         query = "INSERT INTO burger (burger_id, burger_name, burger_price) VALUES (%s, %s, %s)"
    #         cur.execute(query, (sheet['burger_id'], sheet['burger_name'], sheet['burger_price']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}")
    # elif sheet_name == SheetName.SIDEMENU.name:
    #     try:
    #         query = "INSERT INTO sidemenu (sidemenu_id, sidemenu_name, sidemenu_price) VALUES (%s, %s, %s)"
    #         cur.execute(query, (sheet['sidemenu_id'], sheet['sidemenu_name'], sheet['sidemenu_price']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}") 
    # elif sheet_name == SheetName.DRINK.name:
    #     try:
    #         query = "INSERT INTO drink (drink_id, drink_name, drink_price) VALUES (%s, %s, %s)"
    #         cur.execute(query, (sheet['drink_id'], sheet['drink_name'], sheet['drink_price']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}")
    # elif sheet_name == SheetName.SET_MENU.name:
    #     try:
    #         query = "INSERT INTO set_menu (set_menu_id, set_menu_name, set_menu_price) VALUES (%s, %s, %s)"
    #         cur.execute(query, (sheet['set_menu_id'], sheet['set_menu_name'], sheet['set_menu_price']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}")
    # elif sheet_name == SheetName.ORDER_DETAIL.name:
    #     try:
    #         query = "INSERT INTO order_detail (order_id, burger_id, sidemenu_id, drink_id, set_menu_id) VALUES (%s, %s, %s, %s, %s)"
    #         cur.execute(query, (sheet['order_id'], sheet['burger_id'], sheet['sidemenu_id'], sheet['drink_id'], sheet['set_menu_id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[insert_row] DB 삽입 실패: {e}")


def update_sheet(cur: pymysql.cursors.Cursor, sheet_name: str, sheet: dict):
    # 이 함수는 sheet을 DB에 업데이트하는 함수로 구현해야 함
    # 이 함수를 쓰는 경우 : 시트에 새로운 행 추가, 기존 행의 정보 변경, 기존 행 삭제
    # 경우를 어떻게 구분해야할까 
    # 시트에 새로운 행 추가 : insert_row 함수 작성
    # 기존 행의 정보 변경 : update_row 함수 작성
    # 기존 행 삭제 : delete_row 함수 작성

    # 우선 db에서 해당 시트의 데이터를 가져온다.
    db_data = get_data_from_db(cur, sheet_name)
    # 그리고 각 시트의 데이터와 엑셀파일과 비교한다.
    for row in sheet:
        row_id = row['id']  # 각 행의 id를 기준으로 비교
        if row_id in db_data:
            # 해당 행의 데이터를 비교하여 바꿀 정보가 있다면 update_row 함수를 사용하여 db에 업데이트한다.
            if has_changes(row, db_data[row_id]):  # has_changes 함수는 row와 db_data[row_id]를 비교하여 변경된 정보가 있는지 확인하는 함수로 구현해야 함
                update_row(cur, sheet_name, row)
        # 해당 아이디가 존재하지 않으면 insert_row 함수를 사용하여 db에 삽입한다.
        else:
            insert_row(cur, sheet_name, row) 
    
    excel_ids = {row['id'] for row in sheet}  # 엑셀 파일에 존재하는 아이디 집합
    for db_row in db_data:
        db_row_id = db_row['id']  # DB에서 가져온 행의 id
        if db_row_id not in excel_ids:
            # DB에 존재하지만 엑셀 파일에 존재하지 않는 아이디가 있다면 delete_row 함수를 사용하여 db에서 삭제한다.
            delete_row(cur, sheet_name, db_row_id)
    pass

def has_changes(row: dict, db_row: dict):
    # 이 함수는 row와 db_row를 비교하여 변경된 정보가 있는지 확인하는 함수로 구현해야 함
    # row와 db_row는 딕셔너리 형태로 되어있다고 가정
    for key in row:
        if row[key] != db_row[key]:
            return True  # 변경된 정보가 있음
    return False  # 변경된 정보가 없음

def update_row(cur: pymysql.cursors.Cursor, sheet_name: str, row: dict):
    # 이 함수는 row을 DB에 업데이트하는 함수로 구현해야 함
    # 시트 제목을 기준으로 조건문을 생성
    # if sheet_name == 'burger':
    #   #   update 쿼리를 작성하여 row의 각 정보를 DB에 업데이트


    try:
        query = f"UPDATE {sheet_name} SET {', '.join([f'{key} = %s' for key in row.keys() if key != 'id'])} WHERE id = %s"
        values = [value for key, value in row.items() if key != 'id'] + [row['id']]
        cur.execute(query, tuple(values))
    except pymysql.MySQLError as e:
        raise Exception(f"[update_row] DB 업데이트 실패: {e}")

    # if sheet_name == SheetName.VERSION.name:
    #     try:
    #         query = "UPDATE version SET version_code = %s WHERE id = %s"
    #         cur.execute(query, (row['version_code'], row['id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[update_row] DB 업데이트 실패: {e}")
    # elif sheet_name == SheetName.BURGER.name:
    #     try:
    #         query = "UPDATE burger SET burger_name = %s, burger_price = %s WHERE burger_id = %s"
    #         cur.execute(query, (row['burger_name'], row['burger_price'], row['burger_id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[update_row] DB 업데이트 실패: {e}")
    # elif sheet_name == SheetName.SIDEMENU.name:
    #     try:
    #         query = "UPDATE sidemenu SET sidemenu_name = %s, sidemenu_price = %s WHERE sidemenu_id = %s"
    #         cur.execute(query, (row['sidemenu_name'], row['sidemenu_price'], row['sidemenu_id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[update_row] DB 업데이트 실패: {e}") 
    # elif sheet_name == SheetName.DRINK.name:
    #     try:
    #         query = "UPDATE drink SET drink_name = %s, drink_price = %s WHERE drink_id = %s"
    #         cur.execute(query, (row['drink_name'], row['drink_price'], row['drink_id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[update_row] DB 업데이트 실패: {e}")
    # elif sheet_name == SheetName.SET_MENU.name:
    #     try:
    #         query = "UPDATE set_menu SET set_menu_name = %s, set_menu_price = %s WHERE set_menu_id = %s"
    #         cur.execute(query, (row['set_menu_name'], row['set_menu_price'], row['set_menu_id']))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[update_row] DB 업데이트 실패: {e}")

def delete_row(cur: pymysql.cursors.Cursor, sheet_name: str, row_id: int):
    # 이 함수는 row_id를 DB에서 삭제하는 함수로 구현해야 함
    # 시트 제목을 기준으로 조건문을 생성
    # if sheet_name == 'burger':
    #   #   delete 쿼리를 작성하여 row_id에 해당하는 행을 DB에서 삭제

    try:
        query = f"DELETE FROM {sheet_name} WHERE id = %s"
        cur.execute(query, (row_id))
    except pymysql.MySQLError as e:
        raise Exception(f"[delete_row] DB 삭제 실패: {e}")

    # if sheet_name == SheetName.VERSION.name:
    #     try:
    #         query = "DELETE FROM version WHERE id = %s"
    #         cur.execute(query, (row_id))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[delete_row] DB 삭제 실패: {e}")
    # elif sheet_name == SheetName.BURGER.name:
    #     try:
    #         query = "DELETE FROM burger WHERE burger_id = %s"
    #         cur.execute(query, (row_id))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[delete_row] DB 삭제 실패: {e}")
    # elif sheet_name == SheetName.SIDEMENU.name:
    #     try:
    #         query = "DELETE FROM sidemenu WHERE sidemenu_id = %s"
    #         cur.execute(query, (row_id))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[delete_row] DB 삭제 실패: {e}") 
    # elif sheet_name == SheetName.DRINK.name:
    #     try:
    #         query = "DELETE FROM drink WHERE drink_id = %s"
    #         cur.execute(query, (row_id))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[delete_row] DB 삭제 실패: {e}")
    # elif sheet_name == SheetName.SET_MENU.name:
    #     try:
    #         query = "DELETE FROM set_menu WHERE set_menu_id = %s"
    #         cur.execute(query, (row_id))
    #     except pymysql.MySQLError as e:
    #         raise Exception(f"[delete_row] DB 삭제 실패: {e}")

def get_data_from_db(cur: pymysql.cursors.Cursor, sheet_name: str):
    try:
        
        query = f"SELECT * FROM {sheet_name}"
        cur.execute(query)
        return cur.fetchall()
    except pymysql.MySQLError as e:
        raise Exception(f"[get_data_from_db] DB 조회 실패: {e}")

## version 테이블의 version_code 업데이트
def update_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection, version_code):
    try:
        query = "UPDATE version SET version_code = %s"
        cur.execute(query, (version_code))
        conn.commit()
    except pymysql.MySQLError as e:
        raise Exception(f"[update_version_code] DB 업데이트 실패: {e}")