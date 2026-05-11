"""
버전 관리 모듈
데이터베이스의 version_code를 조회/업데이트
"""

import pymysql


def get_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection) -> int:
    """
    데이터베이스의 VERSION 테이블에서 version_code를 조회
    
    Args:
        cur: 데이터베이스 커서
        conn: 데이터베이스 연결
    
    Returns:
        version_code 값
        테이블이 없거나 데이터가 없으면 -1 반환
    
    Raises:
        Exception: 데이터베이스 조회 실패 시
    """
    try:
        query = "SELECT version_code FROM version"
        cur.execute(query)
        conn.commit()
        result = cur.fetchone()
        
        if result:
            return result[0]
        else:
            return -1
    except pymysql.MySQLError as e:
        # 테이블이 없을 때도 -1 반환 (초기 상태)
        if "doesn't exist" in str(e):
            return -1
        raise Exception(f"[get_version_code] DB 조회 실패: {e}")


def update_version_code(cur: pymysql.cursors.Cursor, conn: pymysql.Connection, version_code: int) -> None:
    """
    데이터베이스의 VERSION 테이블의 version_code를 업데이트
    
    Args:
        cur: 데이터베이스 커서
        conn: 데이터베이스 연결
        version_code: 새로운 version_code 값
    
    Raises:
        Exception: 데이터베이스 업데이트 실패 시
    """
    try:
        query = "UPDATE version SET version_code = %s"
        cur.execute(query, (version_code,))
        conn.commit()
    except pymysql.MySQLError as e:
        raise Exception(f"[update_version_code] DB 업데이트 실패: {e}")
