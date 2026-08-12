import os
import sys
from pathlib import Path

# 테스트 실행을 위해 상위 폴더를 경로에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import pymysql
from pymysql.cursors import DictCursor

from ANALYZE.order_analyze_1 import OrderAnalyzer
from db.connect_db import db_Connect


def main():
    print("ANALYZE/order_analyze_1.py 테스트 시작")

    conn = db_Connect()
    cur = conn.cursor(DictCursor)

    try:
        analyzer = OrderAnalyzer(cur)

        # print("- get_daily_sales() 호출")
        # daily = analyzer.get_daily_sales(days=7)
        # print(f"  일별 매출: {daily}")

        print("- get_monthly_sales() 호출")
        monthly = analyzer.get_monthly_sales(months=3)
        print(f"  월별 매출: {monthly}")

        print("- get_hourly_sales() 호출")
        hourly = analyzer.get_hourly_sales(days=7)
        print(f"  시간대별 매출: {hourly}")

        # print("- get_popular_burgers() 호출")
        # burgers = analyzer.get_popular_burgers(limit=5, days=30)
        # print(f"  인기 버거: {burgers}")

        # print("- get_summary_stats() 호출")
        # summary = analyzer.get_summary_stats(days=7)
        # print(f"  요약 통계: {summary}")

        print("테스트 완료: 오류 없이 실행되었습니다.")
    except Exception as exc:
        print(f"테스트 실패: {exc}")
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
