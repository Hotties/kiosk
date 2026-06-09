## order detail 테이블에 있는 데이터를 excel 파일로 저장하는 로직
## sheet handlers.py를 import

import pymysql

try:
    from db.sheet_handlers import OrderDetailHandler
except ImportError:
    from sheet_handlers import OrderDetailHandler

## def get_data_from_order_detail_table(cur) -> list[dict]:

def get_data_from_order_detail_table(cur: pymysql.cursors.Cursor) -> list[dict]:
    """
    order_detail 테이블에서 데이터를 조회하여 딕셔너리 리스트로 반환
    
    Args:
        cur: 데이터베이스 커서
    
    Returns:
        order_detail 테이블의 모든 행을 {컬럼명: 값, ...} 형태의 딕셔너리 리스트로 반환
    
    Raises:
        Exception: 데이터 조회 실패 시
    """
    try:
        handler = OrderDetailHandler()
        table_name = handler.get_table_name()
        columns = handler.get_columns()
        
        # SQL 쿼리 작성
        sql = f"SELECT {', '.join(columns)} FROM {table_name}"
        
        # 쿼리 실행
        cur.execute(sql)
        rows = cur.fetchall()
        
        # 컬럼명과 값을 매핑하여 딕셔너리 리스트로 변환
        data = []
        for row in rows:
            row_dict = {col: row[col] for col in columns}
            data.append(row_dict)
        
        return data
    except Exception as e:
        raise Exception(f"[get_data_from_order_detail_table] 데이터 조회 실패: {e}")

## write_data_to_excel(data: list[dict], excel_file_path: str = 'data.xlsx') -> None:
## 엑셀 파일이 없다면 새로 만든다.
## 엑셀 파일이 있다면 기존 데이터를 덮어쓰거나, 비교해서 추가

def write_data_to_excel(data: list[dict], excel_file_path: str = 'data.xlsx') -> None:
    """
    데이터를 Excel 파일에 저장
    
    Args:
        data: 저장할 데이터 리스트 (각 요소는 {컬럼명: 값, ...} 형태의 딕셔너리)
        excel_file_path: Excel 파일 경로 (기본값: 'data.xlsx')
    
    Raises:
        Exception: Excel 파일 쓰기 실패 시
    """
    try:
        import pandas as pd
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        
        # Excel 파일로 저장 (덮어쓰기)
        df.to_excel(excel_file_path, sheet_name='order_detail', index=False)
        
        print(f"[write_data_to_excel] 데이터가 '{excel_file_path}'에 저장되었습니다.")
    except Exception as e:
        raise Exception(f"[write_data_to_excel] Excel 파일 쓰기 실패: {e}")
