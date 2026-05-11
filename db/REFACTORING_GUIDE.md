# 리팩토링된 데이터 업데이트 시스템

## 개요

`update_data.py` 원본 파일을 팩토리 패턴과 클래스 기반 아키텍처로 리팩토링했습니다.  
기능별로 모듈을 분리하여 **확장성**, **유지보수성**, **테스트 용이성**을 높였습니다.

---

## 파일 구조 및 책임

### 1. **sheet_handlers.py** 
시트별 데이터베이스 작업을 캡슐화한 핸들러 클래스들

**주요 클래스:**
- `SheetHandler` (추상 기본 클래스)
  - `get_table_name()` - 테이블 이름
  - `get_id_column()` - ID 컬럼명
  - `get_columns()` - 모든 컬럼 목록
  - `load_db_data()` - DB에서 데이터 로드 (공통)
  - `insert_row()` - 행 삽입 (공통)
  - `update_row()` - 행 업데이트 (공통)
  - `delete_row()` - 행 삭제 (공통)

- `VersionHandler`, `BurgerHandler`, `SidemenuHandler`, `DrinkHandler`, `SetMenuHandler`, `OrderDetailHandler`
  - 각 시트별 구체적 구현 (테이블/컬럼 정보만 정의)

- `create_sheet_handler()` (팩토리 함수)
  - sheet_name에 따라 적절한 핸들러 자동 생성

**특징:**
- 각 시트별 쿼리가 중복되지 않음
- 새 시트 추가 시 핸들러 클래스만 추가하면 됨
- 기존 insert/update/delete 함수의 if-elif 분기 제거

---

### 2. **excel_reader.py**
Excel 파일에서 데이터를 읽는 로직

**주요 함수:**
- `get_excel_version_code(excel_file_path)` 
  - VERSION 시트에서 version_code 읽기

- `get_data_from_excel(excel_file_path)`
  - 모든 시트의 데이터를 {시트명: [행1, 행2, ...]} 형태로 반환

**특징:**
- Excel 파일 경로를 파라미터로 받음 (테스트 시 다른 파일 사용 가능)
- pandas를 사용하여 깔끔한 데이터 변환

---

### 3. **version_manager.py**
데이터베이스의 version_code 관리

**주요 함수:**
- `get_version_code(cur, conn)`
  - DB의 version_code 조회
  - 테이블 없으면 -1 반환

- `update_version_code(cur, conn, version_code)`
  - DB의 version_code 업데이트

**특징:**
- 버전 관리 로직을 독립적인 모듈로 분리
- 버전 비교 로직과 분리

---

### 4. **data_sync.py**
Excel과 DB 데이터를 동기화하는 핵심 로직

**주요 함수:**
- `sync_sheet(cur, sheet_name, excel_data)`
  - Excel 데이터와 DB를 동기화 (중요!)
  - 로직:
    1. 핸들러 생성 (팩토리 사용)
    2. DB 데이터 로드
    3. Excel 데이터 순회:
       - 새 행: insert
       - 기존 행 + 변경 있음: update
    4. DB만 있는 행: delete

- `has_changes(excel_row, db_row)`
  - Excel 행과 DB 행의 변경사항 확인

- `insert_sheet_legacy()` (선택사항)
  - 기존 코드 호환성용 (새 코드에서는 sync_sheet 사용)

**특징:**
- 파일의 모든 데이터를 매번 덮어쓰지 않음
- 실제 변경사항만 반영

---

### 5. **update_data_refactored.py**
메인 조율 로직

**주요 함수:**
- `update_data(cur, conn, excel_file_path)`
  - 전체 동기화 프로세스 조율
  - 로직:
    1. DB version_code 조회
    2. Excel version_code 조회
    3. 버전 비교 → 필요시 sync_sheet 호출
    4. DB version_code 업데이트

**특징:**
- 이전 파일의 update_data와 동일한 인터페이스
- 내부적으로는 새로운 모듈들을 활용

---

## 사용 방법

### 기본 사용 (원본과 동일)

```python
import pymysql
from update_data_refactored import update_data

# DB 연결
conn = pymysql.connect(
    host='localhost',
    user='your_user',
    password='your_password',
    database='your_database'
)
cur = conn.cursor()

# 데이터 동기화
try:
    update_data(cur, conn, 'data.xlsx')  # 또는 기본값 'data.xlsx'
    conn.commit()
except Exception as e:
    print(f"오류: {e}")
finally:
    cur.close()
    conn.close()
```

### 특정 시트만 동기화

```python
from data_sync import sync_sheet
from excel_reader import get_data_from_excel
from sheet_handlers import SheetName

# Excel 데이터 읽기
datasheets = get_data_from_excel('data.xlsx')

# BURGER 시트만 동기화
if SheetName.BURGER.name in datasheets:
    sync_sheet(cur, SheetName.BURGER.name, datasheets[SheetName.BURGER.name])
    conn.commit()
```

### 특정 시트 핸들러 직접 사용

```python
from sheet_handlers import create_sheet_handler

handler = create_sheet_handler('BURGER', cur)
db_data = handler.load_db_data()

# 새 행 추가
handler.insert_row({'burger_id': 10, 'burger_name': '치즈버거', 'burger_price': 5500})
conn.commit()
```

---

## 개선 사항

| 항목 | 원본 | 리팩토링 |
|------|------|---------|
| **코드 중복** | 많음 (if-elif 반복) | 없음 (공통 로직 캡슐화) |
| **새 시트 추가** | 여러 함수 수정 필요 | 핸들러 클래스만 추가 |
| **유지보수** | 어려움 | 쉬움 (모듈별 책임 명확) |
| **테스트** | 어려움 | 쉬움 (모듈 단위 테스트 가능) |
| **확장성** | 낮음 | 높음 (팩토리 패턴 활용) |

---

## 주의사항

1. **Excel 파일 경로**: 기본값은 `'data.xlsx'` (실행 디렉토리 기준)  
   필요시 절대 경로 사용: `update_data(cur, conn, '/path/to/data.xlsx')`

2. **version_code**: 
   - VERSION 시트의 첫 행, 'version_code' 컬럼에서 읽음
   - DB에 VERSION 테이블 필요
   - 초기 상태 (테이블 없음): version_code = -1

3. **ID 컬럼**: 각 시트는 고유 ID 필요
   - VERSION: version_code
   - BURGER: burger_id
   - SIDEMENU: sidemenu_id
   - DRINK: drink_id
   - SET_MENU: set_menu_id
   - ORDER_DETAIL: order_id

4. **트랜잭션**: 
   - 오류 시 자동 롤백됨
   - 성공 시 호출자가 commit() 호출

5. **기존 코드 호환성**: 
   - 원본 `update_data()` 함수와 동일한 시그니처
   - 기존 코드를 교체할 수 있음

---

## 테스트 방법

```python
# 1. 단위 테스트: 핸들러 테스트
from sheet_handlers import create_sheet_handler

handler = create_sheet_handler('VERSION', cur)
print(handler.get_table_name())  # "version"
print(handler.get_id_column())   # "version_code"

# 2. 통합 테스트: 전체 동기화
from update_data_refactored import update_data

update_data(cur, conn, 'test_data.xlsx')
```

---

## 향후 개선 아이디어

1. **배치 작업**: 대량 데이터 처리 시 배치 insert 사용
2. **로깅**: 각 동기화 작업 상세 로깅
3. **트랜잭션 관리**: 시트별 트랜잭션 분리
4. **변경 이력**: 수정된 내용 별도 로그 테이블에 저장
5. **스키마 검증**: Excel 시트 구조 사전 검증
6. **성능 모니터링**: 동기화 속도 측정

---

## 원본 파일 참고

원본 `update_data.py`는 그대로 유지되므로 필요시 비교 참고 가능합니다.
