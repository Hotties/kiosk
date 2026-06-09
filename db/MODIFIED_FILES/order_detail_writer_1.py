"""
주문 상세 데이터 작성 모듈
order_detail 테이블의 데이터를 Excel 파일로 저장하는 로직
"""

import pymysql
from typing import Optional
import pandas as pd


def get_order_details_from_db(cur: pymysql.cursors.Cursor, 
                               days: Optional[int] = None) -> list[dict]:
    """
    order_detail 테이블에서 데이터를 조회하여 딕셔너리 리스트로 반환
    
    Args:
        cur: 데이터베이스 커서
        days: 조회할 일수 (None이면 전체 조회)
    
    Returns:
        order_detail 테이블의 행을 {컬럼명: 값, ...} 형태의 딕셔너리 리스트로 반환
    
    Raises:
        Exception: 데이터 조회 실패 시
    """
    try:
        if days is not None:
            query = """
                SELECT order_id, burger_id, sidemenu_id, drink_id, set_menu_id, 
                       order_date, dine_in, total_price
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY order_date DESC
            """
            cur.execute(query, (days,))
        else:
            query = """
                SELECT order_id, burger_id, sidemenu_id, drink_id, set_menu_id, 
                       order_date, dine_in, total_price
                FROM order_detail
                ORDER BY order_date DESC
            """
            cur.execute(query)
        
        rows = cur.fetchall()
        
        # DictCursor 사용 시 직접 리스트 반환
        if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
            return rows
        
        # 일반 커서 사용 시 컬럼명과 매핑
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)
            return data
        
        return rows
    
    except Exception as e:
        raise Exception(f"[get_order_details_from_db] 데이터 조회 실패: {e}")


def get_order_details_with_menu_names(cur: pymysql.cursors.Cursor,
                                       days: Optional[int] = None) -> list[dict]:
    """
    order_detail 테이블에서 데이터를 조회하되, 메뉴 이름도 함께 조회
    (좀 더 읽기 쉬운 형태)
    
    Args:
        cur: 데이터베이스 커서
        days: 조회할 일수 (None이면 전체 조회)
    
    Returns:
        주문 데이터 + 메뉴 이름이 포함된 딕셔너리 리스트
    
    Raises:
        Exception: 데이터 조회 실패 시
    """
    try:
        if days is not None:
            query = """
                SELECT 
                    od.order_id,
                    COALESCE(b.burger_name, '-') as burger_name,
                    COALESCE(s.sidemenu_name, '-') as sidemenu_name,
                    COALESCE(d.drink_name, '-') as drink_name,
                    COALESCE(sm.set_menu_name, '-') as set_menu_name,
                    od.order_date,
                    CASE WHEN od.dine_in THEN '매장' ELSE '포장' END as order_type,
                    od.total_price
                FROM order_detail od
                LEFT JOIN burger b ON od.burger_id = b.burger_id
                LEFT JOIN sidemenu s ON od.sidemenu_id = s.sidemenu_id
                LEFT JOIN drink d ON od.drink_id = d.drink_id
                LEFT JOIN set_menu sm ON od.set_menu_id = sm.set_menu_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY od.order_date DESC
            """
            cur.execute(query, (days,))
        else:
            query = """
                SELECT 
                    od.order_id,
                    COALESCE(b.burger_name, '-') as burger_name,
                    COALESCE(s.sidemenu_name, '-') as sidemenu_name,
                    COALESCE(d.drink_name, '-') as drink_name,
                    COALESCE(sm.set_menu_name, '-') as set_menu_name,
                    od.order_date,
                    CASE WHEN od.dine_in THEN '매장' ELSE '포장' END as order_type,
                    od.total_price
                FROM order_detail od
                LEFT JOIN burger b ON od.burger_id = b.burger_id
                LEFT JOIN sidemenu s ON od.sidemenu_id = s.sidemenu_id
                LEFT JOIN drink d ON od.drink_id = d.drink_id
                LEFT JOIN set_menu sm ON od.set_menu_id = sm.set_menu_id
                ORDER BY od.order_date DESC
            """
            cur.execute(query)
        
        rows = cur.fetchall()
        
        if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
            return rows
        
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)
            return data
        
        return rows
    
    except Exception as e:
        raise Exception(f"[get_order_details_with_menu_names] 데이터 조회 실패: {e}")


def write_order_details_to_excel(data: list[dict], 
                                  excel_file_path: str = 'order_details.xlsx',
                                  sheet_name: str = 'order_detail') -> None:
    """
    주문 데이터를 Excel 파일에 저장
    (메뉴 이름이 포함된 상세 데이터 권장)
    
    Args:
        data: 저장할 데이터 리스트 (각 요소는 {컬럼명: 값, ...} 형태)
        excel_file_path: Excel 파일 경로 (기본값: 'order_details.xlsx')
        sheet_name: 시트명 (기본값: 'order_detail')
    
    Raises:
        Exception: Excel 파일 쓰기 실패 시
    """
    try:
        if not data:
            print(f"[write_order_details_to_excel] 저장할 데이터가 없습니다.")
            return
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        
        # Excel 파일로 저장 (덮어쓰기)
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"[write_order_details_to_excel] {len(data)}개 행이 '{excel_file_path}'에 저장되었습니다.")
    
    except Exception as e:
        raise Exception(f"[write_order_details_to_excel] Excel 파일 쓰기 실패: {e}")


def export_order_details(cur: pymysql.cursors.Cursor,
                         excel_file_path: str = 'order_details.xlsx',
                         days: Optional[int] = None) -> None:
    """
    DB에서 주문 데이터를 조회하여 Excel 파일로 한 번에 내보내기
    (편의 함수)
    
    Args:
        cur: 데이터베이스 커서
        excel_file_path: Excel 파일 경로
        days: 조회할 일수 (None이면 전체)
    
    Raises:
        Exception: 조회 또는 저장 실패 시
    """
    try:
        # 메뉴 이름이 포함된 상세 데이터 조회
        data = get_order_details_with_menu_names(cur, days)
        
        # Excel 파일로 저장
        write_order_details_to_excel(data, excel_file_path)
    
    except Exception as e:
        raise Exception(f"[export_order_details] 내보내기 실패: {e}")


def append_order_details_to_excel(data: list[dict],
                                   excel_file_path: str = 'order_details.xlsx',
                                   sheet_name: str = 'order_detail') -> None:
    """
    기존 Excel 파일에 주문 데이터를 추가 (기존 데이터는 유지)
    
    Args:
        data: 추가할 데이터 리스트
        excel_file_path: Excel 파일 경로
        sheet_name: 시트명
    
    Raises:
        Exception: 파일 처리 실패 시
    """
    try:
        import os
        
        if not data:
            print(f"[append_order_details_to_excel] 추가할 데이터가 없습니다.")
            return
        
        # 기존 데이터 로드 (파일이 있는 경우)
        if os.path.exists(excel_file_path):
            try:
                existing_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            except Exception:
                # 시트가 없거나 파일이 손상된 경우 빈 데이터프레임 사용
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()
        
        # 새 데이터프레임 생성
        new_df = pd.DataFrame(data)
        
        # 기존 데이터와 새 데이터 병합
        if len(existing_df) > 0:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        # Excel 파일로 저장
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"[append_order_details_to_excel] {len(data)}개 행이 '{excel_file_path}'에 추가되었습니다.")
    
    except Exception as e:
        raise Exception(f"[append_order_details_to_excel] 파일 추가 실패: {e}")
