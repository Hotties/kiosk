

"""
멀티스레딩 키오스크 테스트
3개의 키오스크가 동시에 주문을 생성하고 저장하는 동시성 테스트
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from INITIAL_SET.create_table import initialize_database
from INITIAL_SET.init_data import initialize_all
from INITIAL_SET.init_data import PROJECT_ROOT
from db.connect_db import db_Connect
from kiosk2 import Kiosk

def run_kiosk_orders(kiosk_name: str, max_orders: int = 10) -> dict:
    """
    개별 키오스크를 실행하여 주문을 생성합니다.
    
    Args:
        kiosk_name: 키오스크 이름
        max_orders: 생성할 최대 주문 수
    
    Returns:
        실행 결과 {키오스크_이름, 생성된_주문_수, 실행_시간}
    """
    try:
        start_time = time.time()
        
        # 각 스레드에서 독립적인 데이터베이스 연결 생성
        conn = db_Connect()
        kiosk = Kiosk(kiosk_name, conn)
        
        # 키오스크 켜기
        kiosk.on(connect_if_missing=False)
        
        # 주문 생성
        kiosk.run(max_orders=max_orders, delay_range=(0.1, 0.5))
        
        # 키오스크 끄기
        kiosk.off()
        
        elapsed_time = time.time() - start_time
        
        return {
            "kiosk_name": kiosk_name,
            "orders_created": max_orders,
            "elapsed_time": f"{elapsed_time:.2f}s",
            "status": "SUCCESS"
        }
    
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "kiosk_name": kiosk_name,
            "orders_created": 0,
            "elapsed_time": f"{elapsed_time:.2f}s",
            "status": "FAILED",
            "error": str(e)
        }


def run_concurrent_kiosks(num_kiosks: int = 3, orders_per_kiosk: int = 10) -> list[dict]:
    """
    여러 키오스크를 멀티스레딩으로 동시에 실행합니다.
    
    Args:
        num_kiosks: 동시 실행할 키오스크 수
        orders_per_kiosk: 각 키오스크당 생성할 주문 수
    
    Returns:
        각 키오스크의 실행 결과 리스트
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=num_kiosks) as executor:
        # 각 키오스크를 별도의 스레드에서 실행
        futures = [
            executor.submit(run_kiosk_orders, f"Kiosk-{i+1}", orders_per_kiosk)
            for i in range(num_kiosks)
        ]
        
        # 모든 작업이 완료될 때까지 대기
        for future in as_completed(futures):
            results.append(future.result())
    
    return results


def print_test_results(results: list[dict]) -> None:
    """
    테스트 결과를 출력합니다.
    
    Args:
        results: 각 키오스크의 실행 결과 리스트
    """
    print("\n" + "="*60)
    print("키오스크 동시성 테스트 결과")
    print("="*60)
    
    total_orders = 0
    total_time = 0
    success_count = 0
    
    for result in sorted(results, key=lambda x: x["kiosk_name"]):
        status = result["status"]
        status_symbol = "✓" if status == "SUCCESS" else "✗"
        
        print(f"\n{status_symbol} {result['kiosk_name']}")
        print(f"  상태: {status}")
        print(f"  생성된 주문: {result['orders_created']}")
        print(f"  실행 시간: {result['elapsed_time']}")
        
        if status == "FAILED":
            print(f"  오류: {result.get('error', 'Unknown error')}")
        else:
            total_orders += result['orders_created']
            success_count += 1
    
    print("\n" + "-"*60)
    print(f"총 생성된 주문: {total_orders}개")
    print(f"성공한 키오스크: {success_count}/{len(results)}")
    print("="*60 + "\n")


def verify_orders_in_db() -> None:
    """
    데이터베이스의 order_detail 테이블에서 저장된 주문 수를 확인합니다.
    """
    try:
        conn = db_Connect()
        cur = conn.cursor()
        
        # ORDER_DETAIL 테이블의 행 개수 확인
        cur.execute("SELECT COUNT(*) as total_orders FROM order_detail")
        result = cur.fetchone()
        total_orders = result[0] if result else 0
        
        print("\n" + "="*60)
        print("데이터베이스 검증")
        print("="*60)
        print(f"order_detail 테이블 총 행 개수: {total_orders}개")
        print("="*60 + "\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"데이터베이스 검증 실패: {e}\n")


def main():
    
    initialize_database()
    import sys
    excel_path = sys.argv[1] if len(sys.argv) > 1 else str(PROJECT_ROOT / 'data.xlsx')
    initialize_all(excel_path)


    # """메인 테스트 함수"""
    # print("\n키오스크 멀티스레딩 동시성 테스트 시작...")
    # print(f"테스트 설정: 3개 키오스크, 각 10개 주문\n")
    
    # # 동시에 3개의 키오스크 실행 (각 10개 주문)
    # results = run_concurrent_kiosks(num_kiosks=3, orders_per_kiosk=10)
    
    # # 결과 출력
    # print_test_results(results)
    
    # # 데이터베이스 검증
    # verify_orders_in_db()
    
    # print("테스트 완료!")


if __name__ == "__main__":
    main()