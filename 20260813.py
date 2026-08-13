#문항 1
import pymysql


class CafeDBManager:

  def __init__(
      self,
      host='localhost',
      user='root',
      password='',
      db='cafe_db',
      port=3306,
      charset='utf8mb4',
  ):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
    self.port = port
    self.charset = charset
    self.connection = None

  def connect(self):
    if not self.connection or not self.connection.open:
      self.connection = pymysql.connect(
          host=self.host,
          user=self.user,
          password=self.password,
          db=self.db,
          port=self.port,
          charset=self.charset,
          cursorclass=pymysql.cursors.DictCursor,
      )

  def execute_query(self, sql, params=None):

    self.connect()
    cursor = self.connection.cursor()
    try:
      cursor.execute(sql, params)
      result = cursor.fetchall()
      return result
    except Exception as e:
      print(f'조회 중 에러 발생: {e}')
      raise
    finally:
      cursor.close()

  def execute_update(self, sql, params=None):
    """INSERT, UPDATE, DELETE 쿼리를 수행하고 commit 처리"""
    self.connect()
    cursor = self.connection.cursor()
    try:
      affected_rows = cursor.execute(sql, params)
      self.connection.commit()
      return affected_rows
    except Exception as e:
      self.connection.rollback()
      print(f'데이터 변경 중 에러 발생 (Rollback 수행): {e}')
      raise
    finally:
      cursor.close()

  def close(self):
    """커넥션 자원 반납"""
    if self.connection and self.connection.open:
      self.connection.close()


if __name__ == '__main__':
  db_manager = CafeDBManager(
      host='localhost', user='root', password='your_password', db='cafe_db'
  )

  try:
    pass

  except Exception as e:
    print(f'작업 중 오류 발생: {e}')
  finally:
    db_manager.close()

    #문항 2

    import pandas as pd
import pymysql


class CafeDBManager:
  """MariaDB cafe_db 관리를 위한 DB Manager 클래스"""

  def __init__(
      self,
      host='localhost',
      user='root',
      password='',
      db='cafe_db',
      port=3306,
      charset='utf8mb4',
  ):
    self.host = host
    self.user = user
    self.password = password
    self.db = db
    self.port = port
    self.charset = charset
    self.connection = None

  def connect(self):
    """데이터베이스 커넥션 생성 (이미 연결되어 있지 않은 경우)"""
    if not self.connection or not self.connection.open:
      self.connection = pymysql.connect(
          host=self.host,
          user=self.user,
          password=self.password,
          db=self.db,
          port=self.port,
          charset=self.charset,
          cursorclass=pymysql.cursors.DictCursor,
      )

  def execute_query(self, sql, params=None):
    """SELECT 쿼리를 수행하고 딕셔너리 리스트 결과를 반환"""
    self.connect()
    cursor = self.connection.cursor()
    try:
      cursor.execute(sql, params)
      result = cursor.fetchall()
      return result
    except Exception as e:
      print(f'조회 중 에러 발생: {e}')
      raise
    finally:
      cursor.close()

  def execute_update(self, sql, params=None):
    """INSERT, UPDATE, DELETE 쿼리를 수행하고 commit 처리"""
    self.connect()
    cursor = self.connection.cursor()
    try:
      affected_rows = cursor.execute(sql, params)
      self.connection.commit()
      return affected_rows
    except Exception as e:
      self.connection.rollback()
      print(f'데이터 변경 중 에러 발생 (Rollback 수행): {e}')
      raise
    finally:
      cursor.close()

  def close(self):
    """커넥션 자원 반납"""
    if self.connection and self.connection.open:
      self.connection.close()


if __name__ == '__main__':
  db_manager = CafeDBManager(
      host='localhost', user='root', password='your_password', db='cafe_db'
  )

  try:
    print('==================================================')
    print('[분석 1] 매장별 매출 및 객단가(AOV) 진단')
    print('==================================================')
    sql_store_aov = """
            SELECT 
                s.store_nm AS 매장명,
                COUNT(DISTINCT o.order_id) AS 독립주문건수,
                SUM(oi.unit_price * oi.qty) AS 총매출액
            FROM tb_store s
            JOIN tb_order o ON s.store_id = o.store_id
            JOIN tb_order_item oi ON o.order_id = oi.order_id
            GROUP BY s.store_id, s.store_nm
        """
    df_store = pd.DataFrame(db_manager.execute_query(sql_store_aov))

      df_store['평균객단가_AOV'] = df_store['총매출액'] / df_store['독립주문건수']
      df_store = df_store.sort_values(by='총매출액', ascending=False).reset_index(
          drop=True
      )
      print(df_store.head(8))

      top_store = df_store.iloc[0]
      print(
          f"\n[분석 의견] 매출 1위 매장은 '{top_store['매장명']}'이며,"
          f" 총 매출액은 {top_store['총매출액']:,.0f원, 독립 주문건수는"
          f" {top_store['독립주문건수']:,}건, 평균 객단가는"
          f" {top_store['평균객단가_AOV']:,.2f}원으로 집계되었습니다."
          ' 해당 매장은 탄탄한 고객 방문 수와 함께 우수한 객단가를'
          ' 기록하고 있으므로, 타 지점 확산을 위한 프로모션 벤치마킹 대상로'
          ' 적합합니다.\n'
      )

    print('==================================================')
    print('[분석 2] 시간대별 주문 피크 타임 분석')
    print('==================================================')
    sql_time_peak = """
            SELECT 
                HOUR(o.order_dt) AS 주문시간대,
                COUNT(o.order_id) AS 총주문건수
            FROM tb_order o
            GROUP BY HOUR(o.order_dt)
            ORDER BY 주문시간대 ASC
        """
    df_time = pd.DataFrame(db_manager.execute_query(sql_time_peak))

    if not df_time.empty:
      top_3_peaks = df_time.sort_values(by='총주문건수', ascending=False).head(3)
      print(top_3_peaks)

      print(
          '\n[인력 배치 제언] 가장 주문이 집중되는 상위 피크 시간대에는'
          ' 고객 응대 및 제조 지연을 방지하기 위해 숙련된 파트타임 인력을'
          ' 집중 배치(Overlap Shift)하고, 주문량이 급감하는 브레이크'
          ' 타임에는 인력을 탄력적으로 축소하여 인건비 효율성을 극대화해야'
          ' 합니다.\n'
      )

    print('==================================================')
    print('[분석 3] 메뉴 카테고리별 매출 점유율 분석')
    print('==================================================')
    
    sql_category = """
            SELECT 
                c.category_nm AS 카테고리명,
                SUM(oi.unit_price * oi.qty) AS 총매출액,
                SUM(oi.qty) AS 총판매수량
            FROM tb_menu_category c
            JOIN tb_menu m ON c.category_id = m.category_id
            JOIN tb_order_item oi ON m.menu_id = oi.menu_id
            GROUP BY c.category_id, c.category_nm
        """
    df_category = pd.DataFrame(db_manager.execute_query(sql_category))

    if not df_category.empty:
      
      total_sales = df_category['총매출액'].sum()
      df_category['매출점유율_%'] = (
          df_category['총매출액'] / total_sales
      ) * 100
      df_category = df_category.sort_values(
          by='총매출액', ascending=False
      ).reset_index(drop=True)
      print(df_category)

      top_category = df_category.iloc[0]
      print(
          f"\n[영업 인사이트] 가장 높은 매출 점유율을 기록한 주력 카테고리는"
          f" '{top_category['카테고리명']}'(점유율:"
          f" {top_category['매출점유율_%']:.2f}%)입니다. 해당 카테고리는"
          ' 브랜드의 핵심 캐시카우 역할을 수행하고 있으므로, 시그니처'
          ' 메뉴 개발 및 연계 구매(Cross-selling)를 유도할 수 있는 사이드'
          ' 메뉴 세트 구성을 강화하는 전략이 필요합니다.'
      )

  except Exception as e:
    print(f'분석 실행 중 오류 발생: {e}')
  finally:
    db_manager.close()