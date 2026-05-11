"""
데이터 동기화 모듈
Excel 데이터와 DB 데이터를 동기화 (insert/update/delete)
"""

import pymysql
from sheet_handlers import create_sheet_handler


def sync_sheet(cur: pymysql.cursors.Cursor, sheet_name: str, excel_data: list[dict]) -> None:
    """
    Excel 데이터와 DB 데이터를 동기화
    
    동기화 로직:
    1. DB에서 현재 데이터 로드
    2. Excel 데이터와 비교하면서:
       - Excel에만 있는 행: 삽입
       - Excel과 DB 모두에 있는 행: 변경사항 있으면 업데이트
    3. DB에만 있는 행 (Excel에 없는 행): 삭제
    
    Args:
        cur: 데이터베이스 커서
        sheet_name: 시트명 (SheetName enum의 name)
        excel_data: Excel에서 읽은 데이터 ([{컬럼명: 값, ...}, ...])
    
    Raises:
        Exception: 동기화 중 오류 발생 시
    """
    try:
        # 핸들러 생성 (시트별 로직이 캡슐화됨)
        handler = create_sheet_handler(sheet_name, cur)
        
        # DB에서 현재 데이터 로드
        db_data = handler.load_db_data()
        id_col = handler.get_id_column()
        
        # Excel 데이터의 ID 집합 (나중에 삭제 대상 찾기용)
        excel_ids = set()
        
        # Excel 데이터를 순회하며 동기화
        for row in excel_data:
            row_id = row.get(id_col)
            if row_id is None:
                raise ValueError(f"[{sheet_name}] ID 컬럼({id_col})이 데이터에 없음: {row}")
            
            excel_ids.add(row_id)
            
            if row_id in db_data:
                # 기존 행: 변경사항 있으면 업데이트
                if has_changes(row, db_data[row_id]):
                    handler.update_row(row)
            else:
                # 새로운 행: 삽입
                handler.insert_row(row)
        
        # DB에는 있지만 Excel에 없는 행 삭제
        for db_id in db_data:
            if db_id not in excel_ids:
                handler.delete_row(db_id)
                
    except Exception as e:
        raise Exception(f"[sync_sheet] {sheet_name} 동기화 실패: {e}")


def has_changes(excel_row: dict, db_row: dict) -> bool:
    """
    Excel 행과 DB 행을 비교하여 변경사항 확인
    
    Args:
        excel_row: Excel에서 읽은 행 데이터
        db_row: DB에서 읽은 행 데이터
    
    Returns:
        변경사항이 있으면 True, 없으면 False
    """
    for key in excel_row:
        # DB에 없는 컬럼은 무시
        if key not in db_row:
            continue
        # 값이 다르면 변경사항 있음
        if excel_row[key] != db_row[key]:
            return True
    return False


def insert_sheet_legacy(cur: pymysql.cursors.Cursor, sheet_name: str, sheet_data: list[dict]) -> None:
    """
    [레거시 호환성용] 시트의 모든 데이터를 DB에 삽입
    
    새로운 코드에서는 sync_sheet()를 사용하세요.
    
    Args:
        cur: 데이터베이스 커서
        sheet_name: 시트명
        sheet_data: 삽입할 데이터 리스트
    
    Raises:
        Exception: 삽입 실패 시
    """
    try:
        handler = create_sheet_handler(sheet_name, cur)
        for row in sheet_data:
            handler.insert_row(row)
    except Exception as e:
        raise Exception(f"[insert_sheet_legacy] {sheet_name} 삽입 실패: {e}")
