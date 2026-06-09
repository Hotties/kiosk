"""
주문 분석 모듈
DB의 order_detail 데이터를 분석하여 다양한 통계 정보를 제공
- 매출 분석 (일별, 월별, 연별)
- 인기 메뉴 분석
- 시간대별 분석
- 고객 분석
"""

from datetime import datetime, timedelta
from typing import Optional
import pymysql
from pymysql.cursors import DictCursor


class OrderAnalyzer:
    """주문 데이터 분석 클래스"""

    def __init__(self, cur: pymysql.cursors.Cursor):
        """
        분석기 초기화
        
        Args:
            cur: 데이터베이스 커서
        """
        self.cur = cur

    def get_daily_sales(self, days: int = 30) -> dict:
        """
        일별 매출 통계 조회
        
        Args:
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            {날짜: 매출액, ...} 형태의 딕셔너리
        """
        try:
            query = """
                SELECT DATE(order_date) as order_date, SUM(total_price) as daily_sales
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(order_date)
                ORDER BY order_date ASC
            """
            self.cur.execute(query, (days,))
            rows = self.cur.fetchall()
            
            result = {}
            for row in rows:
                date_str = row['order_date'].strftime('%Y-%m-%d')
                result[date_str] = row['daily_sales']
            
            return result
        except Exception as e:
            raise Exception(f"[get_daily_sales] 일별 매출 조회 실패: {e}")

    def get_monthly_sales(self, months: int = 12) -> dict:
        """
        월별 매출 통계 조회
        
        Args:
            months: 조회할 개월 수 (기본값: 최근 12개월)
        
        Returns:
            {년월: 매출액, ...} 형태의 딕셔너리
        """
        try:
            query = """
                SELECT DATE_FORMAT(order_date, '%Y-%m') as month, SUM(total_price) as monthly_sales
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s MONTH)
                GROUP BY DATE_FORMAT(order_date, '%Y-%m')
                ORDER BY month ASC
            """
            self.cur.execute(query, (months,))
            rows = self.cur.fetchall()
            
            result = {}
            for row in rows:
                result[row['month']] = row['monthly_sales']
            
            return result
        except Exception as e:
            raise Exception(f"[get_monthly_sales] 월별 매출 조회 실패: {e}")

    def get_hourly_sales(self, days: int = 1) -> dict:
        """
        시간대별 매출 통계 조회
        
        Args:
            days: 조회할 일수 (기본값: 최근 1일)
        
        Returns:
            {시간: 매출액, ...} 형태의 딕셔너리 (시간: 00~23)
        """
        try:
            query = """
                SELECT HOUR(order_date) as hour, SUM(total_price) as hourly_sales
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY HOUR(order_date)
                ORDER BY hour ASC
            """
            self.cur.execute(query, (days,))
            rows = self.cur.fetchall()
            
            result = {f"{i:02d}:00": 0 for i in range(24)}  # 모든 시간 초기화
            for row in rows:
                hour_key = f"{row['hour']:02d}:00"
                result[hour_key] = row['hourly_sales']
            
            return result
        except Exception as e:
            raise Exception(f"[get_hourly_sales] 시간대별 매출 조회 실패: {e}")

    def get_popular_burgers(self, limit: int = 10, days: int = 30) -> list[dict]:
        """
        인기 버거 메뉴 순위 조회
        
        Args:
            limit: 조회할 상위 개수 (기본값: 10)
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            [{"burger_id": 1, "burger_name": "...", "order_count": 100, "sales": 500000}, ...]
        """
        try:
            query = """
                SELECT 
                    b.burger_id,
                    b.burger_name,
                    COUNT(od.order_id) as order_count,
                    SUM(od.total_price) as sales
                FROM order_detail od
                INNER JOIN burger b ON od.burger_id = b.burger_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY b.burger_id, b.burger_name
                ORDER BY order_count DESC
                LIMIT %s
            """
            self.cur.execute(query, (days, limit))
            rows = self.cur.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"[get_popular_burgers] 인기 버거 조회 실패: {e}")

    def get_popular_items(self, limit: int = 10, days: int = 30) -> dict:
        """
        모든 메뉴 항목의 인기도 조회
        
        Returns:
            {"burgers": [...], "sides": [...], "drinks": [...], "sets": [...]} 형태
        """
        try:
            result = {}
            
            # 버거
            burger_query = """
                SELECT 
                    b.burger_id,
                    b.burger_name,
                    COUNT(*) as count,
                    SUM(od.total_price) as sales
                FROM order_detail od
                INNER JOIN burger b ON od.burger_id = b.burger_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY b.burger_id
                ORDER BY count DESC
                LIMIT %s
            """
            self.cur.execute(burger_query, (days, limit))
            result['burgers'] = [dict(row) for row in self.cur.fetchall()]
            
            # 사이드
            side_query = """
                SELECT 
                    s.sidemenu_id,
                    s.sidemenu_name,
                    COUNT(*) as count,
                    SUM(od.total_price) as sales
                FROM order_detail od
                INNER JOIN sidemenu s ON od.sidemenu_id = s.sidemenu_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY s.sidemenu_id
                ORDER BY count DESC
                LIMIT %s
            """
            self.cur.execute(side_query, (days, limit))
            result['sides'] = [dict(row) for row in self.cur.fetchall()]
            
            # 음료
            drink_query = """
                SELECT 
                    d.drink_id,
                    d.drink_name,
                    COUNT(*) as count,
                    SUM(od.total_price) as sales
                FROM order_detail od
                INNER JOIN drink d ON od.drink_id = d.drink_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY d.drink_id
                ORDER BY count DESC
                LIMIT %s
            """
            self.cur.execute(drink_query, (days, limit))
            result['drinks'] = [dict(row) for row in self.cur.fetchall()]
            
            # 세트
            set_query = """
                SELECT 
                    s.set_menu_id,
                    s.set_menu_name,
                    COUNT(*) as count,
                    SUM(od.total_price) as sales
                FROM order_detail od
                INNER JOIN set_menu s ON od.set_menu_id = s.set_menu_id
                WHERE od.order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY s.set_menu_id
                ORDER BY count DESC
                LIMIT %s
            """
            self.cur.execute(set_query, (days, limit))
            result['sets'] = [dict(row) for row in self.cur.fetchall()]
            
            return result
        except Exception as e:
            raise Exception(f"[get_popular_items] 인기 메뉴 조회 실패: {e}")

    def get_order_count_by_date(self, days: int = 30) -> dict:
        """
        일별 주문 수 조회
        
        Args:
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            {날짜: 주문수, ...} 형태의 딕셔너리
        """
        try:
            query = """
                SELECT DATE(order_date) as order_date, COUNT(*) as order_count
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(order_date)
                ORDER BY order_date ASC
            """
            self.cur.execute(query, (days,))
            rows = self.cur.fetchall()
            
            result = {}
            for row in rows:
                date_str = row['order_date'].strftime('%Y-%m-%d')
                result[date_str] = row['order_count']
            
            return result
        except Exception as e:
            raise Exception(f"[get_order_count_by_date] 일별 주문 수 조회 실패: {e}")

    def get_dine_in_vs_takeout(self, days: int = 30) -> dict:
        """
        매장 식사 vs 포장 통계 조회
        
        Args:
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            {"dine_in": {"count": ..., "sales": ...}, "takeout": {"count": ..., "sales": ...}}
        """
        try:
            query = """
                SELECT 
                    dine_in,
                    COUNT(*) as count,
                    SUM(total_price) as sales
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY dine_in
            """
            self.cur.execute(query, (days,))
            rows = self.cur.fetchall()
            
            result = {
                "dine_in": {"count": 0, "sales": 0},
                "takeout": {"count": 0, "sales": 0}
            }
            
            for row in rows:
                key = "dine_in" if row['dine_in'] else "takeout"
                result[key]['count'] = row['count']
                result[key]['sales'] = row['sales']
            
            return result
        except Exception as e:
            raise Exception(f"[get_dine_in_vs_takeout] 식사 타입 통계 조회 실패: {e}")

    def get_total_sales(self, days: int = 30) -> int:
        """
        총 매출액 조회
        
        Args:
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            총 매출액 (정수)
        """
        try:
            query = """
                SELECT SUM(total_price) as total_sales
                FROM order_detail
                WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            self.cur.execute(query, (days,))
            row = self.cur.fetchone()
            
            return row['total_sales'] if row and row['total_sales'] else 0
        except Exception as e:
            raise Exception(f"[get_total_sales] 총 매출액 조회 실패: {e}")

    def get_summary_stats(self, days: int = 30) -> dict:
        """
        모든 주요 통계를 한 번에 조회 (대시보드용)
        
        Args:
            days: 조회할 일수 (기본값: 최근 30일)
        
        Returns:
            주요 통계 정보 딕셔너리
        """
        try:
            result = {
                "total_sales": self.get_total_sales(days),
                "order_count": self._get_total_order_count(days),
                "average_order_value": 0,
                "dine_in_vs_takeout": self.get_dine_in_vs_takeout(days),
                "popular_items": self.get_popular_items(limit=5, days=days),
                "hourly_distribution": self.get_hourly_sales(days=1),
            }
            
            # 평균 주문 가격 계산
            if result['order_count'] > 0:
                result['average_order_value'] = result['total_sales'] // result['order_count']
            
            return result
        except Exception as e:
            raise Exception(f"[get_summary_stats] 통계 조회 실패: {e}")

    def _get_total_order_count(self, days: int) -> int:
        """
        총 주문 수 조회 (내부 함수)
        """
        query = """
            SELECT COUNT(*) as count
            FROM order_detail
            WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        self.cur.execute(query, (days,))
        row = self.cur.fetchone()
        return row['count'] if row else 0
