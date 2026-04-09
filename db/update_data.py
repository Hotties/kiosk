import pandas as pd
import pymysql

def update_data(cur: pymysql.cursors.Cursor, conn: pymysql.Connection):
    # 1. version 테이블에서 verion_code 가져오기
    version_code = get_version_code(cur, conn)
    
    # 2. excel 파일에서 version_code 가져오기
    excel_version_code = get_excel_version_code()  # 이 함수는 excel 파일에서 version_code를 읽어오는 함수로 구현해야 함
    
    # 3. version_code 비교하기
    if version_code != excel_version_code or version_code == -1:
        # 4. version_code가 다르면, excel 파일에서 데이터 가져와서 DB에 업데이트하기
        data = get_data_from_excel()  # 이 함수는 excel 파일에서 데이터를 읽어오는 함수로 구현해야 함
        
        # 4-2. DB에 업데이트하기
        for item in data: ## version, burger, sidemenu, drink, set_menu, order_detail 시트를 순환
            update_or_insert_data(cur, item, version_code)  # 이 함수는 item이 DB에 존재하는지 확인하고, 존재하면 update, 존재하지 않으면 insert 하는 함수로 구현해야 함
        
        # version 테이블의 version_code 업데이트
        update_version_code(cur, conn, excel_version_code)  # 이 함수는 version 테이블의 version_code를 업데이트하는 함수로 구현해야 함

## 1. version 테이블에서 verion_code 가져오기
def get_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection):
    
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
        df = pd.read_excel('data.xlsx', sheet_name='version')  # 엑셀 파일 경로와 시트 이름
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
def update_or_insert_data(cur: pymysql.cursors.Cursor, item, version_code):
    ## version_code가 -1이면 item insert, version_code가 -1이 아니면 item update
    if version_code == -1:
        # item insert
        insert_item(cur, item)  # 이 함수는 item을 DB에 삽입하는 함수로 구현해야 함
    else:
        # item update
        update_item(cur, item)  # 이 함수는 item을 DB에 업데이트하는 함수로 구현해야 함

## version 테이블의 version_code 업데이트
def update_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection, version_code):
    try:
        query = "UPDATE version SET version_code = %s"
        cur.execute(query, (version_code))
        conn.commit()
    except pymysql.MySQLError as e:
        raise Exception(f"[update_version_code] DB 업데이트 실패: {e}")