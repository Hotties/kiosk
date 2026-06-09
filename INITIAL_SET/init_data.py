"""
Excel 데이터를 데이터베이스 테이블에 로드하는 스크립트
create_table.py로 생성된 테이블에 초기 데이터를 저장합니다.
"""

import os
import sys
from pathlib import Path

import pymysql

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from db.connect_db import db_Connect
from db.sheet_handlers import create_sheet_handler, SheetName
from db.excel_reader import get_data_from_excel


def _resolve_excel_path(excel_file_path: str) -> str:
    path = Path(excel_file_path)
    if path.is_absolute():
        return str(path)
    return str(PROJECT_ROOT / path)


def load_data_from_excel(excel_file_path: str = str(PROJECT_ROOT / 'data.xlsx')) -> bool:
    """
    Excel 파일에서 데이터를 읽어 데이터베이스 테이블에 저장합니다.
    
    Args:
        excel_file_path: Excel 파일 경로 (기본값: 'data.xlsx')
    
    Returns:
        성공 여부 (bool)
    """
    try:
        resolved_path = _resolve_excel_path(excel_file_path)
        print(f"Excel 파일 '{resolved_path}'에서 데이터를 읽고 있습니다...\n")
        
        # Excel 파일에서 모든 데이터 읽기
        excel_data = get_data_from_excel(resolved_path)
        
        # 데이터베이스 연결
        conn = db_Connect()
        
        try:
            with conn.cursor() as cursor:
                # 각 시트에 해당하는 테이블에 데이터 삽입
                
                # 1. VERSION 테이블
                if SheetName.VERSION.name in excel_data:
                    print(f"📝 '{SheetName.VERSION.name}' 시트 데이터 로드 중...")
                    handler = create_sheet_handler(SheetName.VERSION.name, cursor)
                    version_rows = excel_data[SheetName.VERSION.name]
                    
                    for row in version_rows:
                        if row.get('version_code'):
                            handler.insert_row(row)
                    
                    print(f"   ✓ {len(version_rows)}개 레코드 저장 완료\n")
                
                # 2. BURGER 테이블
                if SheetName.BURGER.name in excel_data:
                    print(f"📝 '{SheetName.BURGER.name}' 시트 데이터 로드 중...")
                    handler = create_sheet_handler(SheetName.BURGER.name, cursor)
                    burger_rows = excel_data[SheetName.BURGER.name]
                    
                    for row in burger_rows:
                        if row.get('burger_name') and row.get('burger_price') is not None:
                            # burger_id가 없으면 DB에서 자동 생성 (AUTO_INCREMENT)
                            handler.insert_row(row)
                    
                    print(f"   ✓ {len(burger_rows)}개 레코드 저장 완료\n")
                
                # 3. SIDEMENU 테이블
                if SheetName.SIDEMENU.name in excel_data:
                    print(f"📝 '{SheetName.SIDEMENU.name}' 시트 데이터 로드 중...")
                    handler = create_sheet_handler(SheetName.SIDEMENU.name, cursor)
                    sidemenu_rows = excel_data[SheetName.SIDEMENU.name]
                    
                    for row in sidemenu_rows:
                        if row.get('sidemenu_name') and row.get('sidemenu_price') is not None:
                            handler.insert_row(row)
                    
                    print(f"   ✓ {len(sidemenu_rows)}개 레코드 저장 완료\n")
                
                # 4. DRINK 테이블
                if SheetName.DRINK.name in excel_data:
                    print(f"📝 '{SheetName.DRINK.name}' 시트 데이터 로드 중...")
                    handler = create_sheet_handler(SheetName.DRINK.name, cursor)
                    drink_rows = excel_data[SheetName.DRINK.name]
                    
                    for row in drink_rows:
                        if row.get('drink_name') and row.get('drink_price') is not None:
                            handler.insert_row(row)
                    
                    print(f"   ✓ {len(drink_rows)}개 레코드 저장 완료\n")
                
                # 5. SET_MENU 테이블
                if SheetName.SET_MENU.name in excel_data:
                    print(f"📝 '{SheetName.SET_MENU.name}' 시트 데이터 로드 중...")
                    handler = create_sheet_handler(SheetName.SET_MENU.name, cursor)
                    set_menu_rows = excel_data[SheetName.SET_MENU.name]
                    
                    for row in set_menu_rows:
                        if row.get('set_menu_name') and row.get('set_menu_price') is not None:
                            handler.insert_row(row)
                    
                    print(f"   ✓ {len(set_menu_rows)}개 레코드 저장 완료\n")
                
                conn.commit()
                print("✓ 모든 데이터가 데이터베이스에 성공적으로 저장되었습니다!")
                return True
        
        except Exception as e:
            conn.rollback()
            print(f"✗ 데이터 삽입 중 오류 발생: {e}")
            return False
        finally:
            conn.close()
    
    except Exception as e:
        print(f"✗ Excel 파일 읽기 실패: {e}")
        return False


def initialize_all(excel_file_path: str = str(PROJECT_ROOT / 'data.xlsx')) -> bool:
    """
    전체 초기화: 테이블 생성 -> 데이터 로드
    
    Args:
        excel_file_path: Excel 파일 경로
    
    Returns:
        성공 여부 (bool)
    """
    from INITIAL_SET.create_table import initialize_database
    
    print("=" * 60)
    print("키오스크 데이터베이스 초기화 시작")
    print("=" * 60)
    print()
    
    # Step 1: 테이블 생성
    print("[Step 1] 데이터베이스 및 테이블 생성")
    print("-" * 60)
    if not initialize_database():
        print("\n✗ 테이블 생성에 실패했습니다.")
        return False
    
    print()
    
    # Step 2: Excel 데이터 로드
    print("[Step 2] Excel 파일 데이터 로드")
    print("-" * 60)
    if not load_data_from_excel(excel_file_path):
        print("\n✗ 데이터 로드에 실패했습니다.")
        return False
    
    print()
    print("=" * 60)
    print("✓ 초기화 완료!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import sys
    
    # 필요시 Excel 파일 경로를 명령줄 인자로 받을 수 있음
    excel_path = sys.argv[1] if len(sys.argv) > 1 else str(PROJECT_ROOT / 'data.xlsx')
    
    success = initialize_all(excel_path)
    sys.exit(0 if success else 1)
