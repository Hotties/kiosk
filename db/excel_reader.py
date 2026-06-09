"""
Excel 파일 읽기 모듈
데이터를 Excel에서 읽어오는 로직
"""

import pandas as pd

try:
    from db.sheet_handlers import SheetName
except ImportError:
    from sheet_handlers import SheetName


def get_excel_version_code(excel_file_path: str = 'data.xlsx') -> int:
    """
    Excel 파일에서 VERSION 시트의 version_code 값을 읽어옴
    
    Args:
        excel_file_path: Excel 파일 경로 (기본값: 'data.xlsx')
    
    Returns:
        version_code 값 (정수)
    
    Raises:
        Exception: Excel 파일 읽기 실패 시
    """
    try:
        df = pd.read_excel(excel_file_path, sheet_name=SheetName.VERSION.name)
        version_code = df['version_code'].iloc[0]  # 첫 번째 행의 version_code
        return int(version_code)
    except Exception as e:
        raise Exception(f"[get_excel_version_code] Excel에서 version_code 읽기 실패: {e}")


def get_data_from_excel(excel_file_path: str = 'data.xlsx') -> dict:
    """
    Excel 파일에서 모든 시트의 데이터를 읽어옴
    
    Args:
        excel_file_path: Excel 파일 경로 (기본값: 'data.xlsx')
    
    Returns:
        {시트명: [행1, 행2, ...], ...} 형태의 딕셔너리
        각 행은 {컬럼명: 값, ...} 형태의 딕셔너리
    
    Raises:
        Exception: Excel 파일 읽기 실패 시
    """
    try:
        # 모든 시트를 딕셔너리 형태로 읽음
        excel_file = pd.ExcelFile(excel_file_path)
        datasheets = {}

        for sheet_name in excel_file.sheet_names:
            # 해당 시트를 읽음
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            # 데이터프레임을 딕셔너리 리스트로 변환
            # orient='records'는 각 행을 {컬럼명: 값, ...} 형태로 변환
            records = df.to_dict(orient='records')
            
            datasheets[sheet_name] = records

        return datasheets
    except Exception as e:
        raise Exception(f"[get_data_from_excel] Excel 파일에서 데이터 읽기 실패: {e}")
