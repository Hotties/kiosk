"""
데이터베이스 및 테이블 생성 스크립트
키오스크 시스템에 필요한 모든 테이블을 생성합니다.
"""

import pymysql
from pymysql.err import OperationalError, ProgrammingError
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()


def create_tables(conn: pymysql.connections.Connection) -> bool:
    """
    데이터베이스에 필요한 모든 테이블을 생성합니다.
    
    Args:
        conn: 데이터베이스 연결 객체
    
    Returns:
        성공 여부 (bool)
    """
    try:
        with conn.cursor() as cursor:
            # 1. VERSION 테이블
            create_version_table = """
            CREATE TABLE IF NOT EXISTS `version` (
                `version_code` VARCHAR(50) PRIMARY KEY
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_version_table)
            print("✓ 'version' 테이블 생성 완료")

            # 2. BURGER 테이블
            create_burger_table = """
            CREATE TABLE IF NOT EXISTS `burger` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `menu_name` VARCHAR(100) NOT NULL,
                `price` INT NOT NULL,
                `kcal` INT NOT NULL,
                `is_upgradeable` BOOLEAN DEFAULT FALSE,
                `allergic` VARCHAR(8) NOT NULL DEFAULT '00000000'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_burger_table)
            print("✓ 'burger' 테이블 생성 완료")

            # 3. SIDE_MENU 테이블
            create_side_menu_table = """
            CREATE TABLE IF NOT EXISTS `side_menu` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `menu_name` VARCHAR(100) NOT NULL,
                `price` INT NOT NULL,
                `kcal` INT NOT NULL,
                `allergic` VARCHAR(8) NOT NULL DEFAULT '00000000',
                `is_upgradeable` BOOLEAN DEFAULT FALSE,
                extra_charge INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_side_menu_table)
            print("✓ 'side_menu' 테이블 생성 완료")

            # 4. DRINK 테이블
            create_drink_table = """
            CREATE TABLE IF NOT EXISTS `drink` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `menu_name` VARCHAR(100) NOT NULL,
                `price` INT NOT NULL,
                `kcal` INT NOT NULL,
                `is_upgradeable` BOOLEAN DEFAULT FALSE,
                extra_charge INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_drink_table)
            print("✓ 'drink' 테이블 생성 완료")

            # 5. SET_MENU 테이블
            create_set_menu_table = """
            CREATE TABLE IF NOT EXISTS `set_menu` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `menu_name` VARCHAR(100) NOT NULL,
                burger_id INT,
                side_menu_id INT,
                drink_id INT,
                `price` INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_set_menu_table)
            print("✓ 'set_menu' 테이블 생성 완료")

            # 6. ORDER_DETAIL 테이블
            create_order_detail_table = """
            CREATE TABLE IF NOT EXISTS `order_detail` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `date` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `order_number` VARCHAR(20) NOT NULL,
                `is_takeout` BOOLEAN DEFAULT TRUE,

                `burger_id` INT,
                `side_menu_id` INT,
                `drink_id` INT,
                `set_menu_id` INT,
                `price` INT NOT NULL,

                FOREIGN KEY (`burger_id`) REFERENCES `burger`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`side_menu_id`) REFERENCES `side_menu`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`drink_id`) REFERENCES `drink`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`set_menu_id`) REFERENCES `set_menu`(`id`) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_order_detail_table)
            print("✓ 'order_detail' 테이블 생성 완료")

            conn.commit()
            print("\n✓ 모든 테이블이 성공적으로 생성되었습니다!")
            return True

    except ProgrammingError as e:
        print(f"✗ SQL 문법 오류: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"✗ 테이블 생성 중 오류 발생: {e}")
        conn.rollback()
        return False


def initialize_database():
    """
    데이터베이스 연결을 설정하고 테이블을 생성합니다.
    
    Returns:
        성공 여부 (bool)
    """
    try:
        # 환경 변수에서 DB 정보 가져오기
        db_host = os.getenv("DB_HOST", "localhost")
        db_user = os.getenv("DB_USER", "root")
        db_passwd = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "kiosk_db")
        db_charset = os.getenv("DB_CHARSET", "utf8mb4")

        print(f"데이터베이스 '{db_name}' 초기화를 시작합니다...")
        print(f"연결 정보: {db_host} / {db_user}\n")

        # DB 연결 시도 (DB가 없을 수도 있으므로)
        try:
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                passwd=db_passwd,
                db=db_name,
                charset=db_charset
            )
            print(f"✓ 기존 데이터베이스 '{db_name}'에 연결되었습니다.")
        except OperationalError as e:
            if e.args[0] == 1049:  # Unknown database
                print(f"✗ 데이터베이스 '{db_name}'이 없습니다. 새로 생성합니다...\n")

                # DB 없이 연결
                conn = pymysql.connect(
                    host=db_host,
                    user=db_user,
                    passwd=db_passwd,
                    charset=db_charset
                )

                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE `{db_name}` DEFAULT CHARACTER SET {db_charset} COLLATE utf8mb4_unicode_ci;")
                    print(f"✓ 데이터베이스 '{db_name}' 생성 완료\n")

                conn.select_db(db_name)
            else:
                print(f"✗ DB 연결 실패: {e}")
                raise

        # 테이블 생성
        success = create_tables(conn)

        # 연결 종료
        conn.close()

        return success

    except Exception as e:
        print(f"✗ 초기화 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    import sys

    success = initialize_database()
    sys.exit(0 if success else 1)
