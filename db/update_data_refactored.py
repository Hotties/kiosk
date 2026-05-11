"""
메인 데이터 업데이트 모듈 (리팩토링 버전)

Excel 파일의 데이터와 DB를 동기화하는 메인 로직
version_code를 기준으로 Excel이 업데이트되었는지 확인하고,
필요시 DB의 모든 데이터를 동기화

의존성:
- sheet_handlers: 시트별 핸들러 클래스
- excel_reader: Excel 읽기 로직
- version_manager: 버전 관리 로직
- data_sync: 데이터 동기화 로직
"""

import pymysql
from excel_reader import get_excel_version_code, get_data_from_excel
from version_manager import get_version_code, update_version_code
from data_sync import sync_sheet


def update_data(cur: pymysql.cursors.Cursor, conn: pymysql.Connection, excel_file_path: str = 'data.xlsx') -> None:
    """
    Excel 데이터와 DB를 동기화하는 메인 함수
    
    처리 로직:
    1. DB의 version_code 조회
    2. Excel의 version_code 조회
    3. version_code 비교:
       - 같으면 동기화 불필요 (종료)
       - 다르면 Excel 데이터 모두 DB와 동기화
    4. 모든 시트의 데이터 동기화 (sync_sheet)
    5. DB의 version_code 업데이트
    
    Args:
        cur: 데이터베이스 커서
        conn: 데이터베이스 연결
        excel_file_path: Excel 파일 경로 (기본값: 'data.xlsx')
    
    Raises:
        Exception: 버전 조회 또는 동기화 실패 시
    """
    try:
        # 1. DB에서 현재 version_code 조회
        db_version_code = get_version_code(cur, conn)
        
        # 2. Excel에서 version_code 조회
        excel_version_code = get_excel_version_code(excel_file_path)
        
        # 3. version_code 비교
        if db_version_code == excel_version_code and db_version_code != -1:
            print(f"[update_data] 데이터가 최신 버전입니다. (v{db_version_code})")
            return  # 동기화 불필요
        
        print(f"[update_data] 데이터 동기화 필요: DB v{db_version_code} -> Excel v{excel_version_code}")
        
        # 4. Excel에서 모든 시트 데이터 읽기
        datasheets = get_data_from_excel(excel_file_path)
        
        # 5. 각 시트별로 DB와 동기화
        for sheet_name, sheet_data in datasheets.items():
            print(f"[update_data] 동기화 중: {sheet_name}")
            sync_sheet(cur, sheet_name, sheet_data)
        
        # 6. DB의 version_code 업데이트
        update_version_code(cur, conn, excel_version_code)
        
        print(f"[update_data] 동기화 완료! (v{excel_version_code})")
        
    except Exception as e:
        conn.rollback()  # 오류 발생 시 롤백
        raise Exception(f"[update_data] 데이터 동기화 실패: {e}")


if __name__ == "__main__":
    # 테스트 코드 예시
    # 실제 사용 시: from update_data_refactored import update_data
    print("이 모듈은 라이브러리입니다. 다른 파일에서 import하여 사용하세요.")
