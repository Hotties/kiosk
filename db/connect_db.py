
import pymysql
from pymysql.err import OperationalError
from dotenv import load_dotenv
import os

def db_Connect( _host=os.getenv("DB_HOST"),
                _user=os.getenv("DB_USER"),
                _passwd=os.getenv("DB_PASSWORD"),
                _db=os.getenv("DB_NAME"),
                _charset=os.getenv("DB_CHARSET")):
    try:
        conn = pymysql.connect(
        host=_host,
        user=_user,
        passwd=_passwd,
        db=_db,
        charset=_charset
        )
        print('Connected to DB:', _db)
        
        return conn
    except OperationalError as e:
        if e.args[0] == 1049:  # Unknown database
            print(f"Database '{_db}' does not exist. Creating it...")

            # DB 없이 연결 (접속만)
            conn = pymysql.connect(
            host=_host,
            user=_user,
            passwd=_passwd,
            charset=_charset
            )

            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{_db}` DEFAULT CHARACTER SET {_charset};")
                print(f"Database '{_db}' created.")

            conn.select_db(_db)  # 새 DB 선택
            return conn

        else:
            # 다른 오류는 그대로 raise
            print("Connection failed:", e)
            raise
        