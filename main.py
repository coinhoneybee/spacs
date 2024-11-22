import OpenDartReader
import dart_fss as dart
import sqlite3
import datetime
import re
from stock_manager import StockManager

# DART API 키 설정
dart_api_key = '8c9ce5ea6e1ee72ad514ab73d923a7414affd5c6'
Odart = OpenDartReader(dart_api_key)
dart.set_api_key(api_key=dart_api_key)  # dart_fss API 키 설정

# 현재 날짜
today = datetime.datetime.today()

# 1주일 전 날짜 계산
one_week_ago = today - datetime.timedelta(weeks=1)

# 날짜를 'YYYYMMDD' 형식으로 변환
bgn_date = one_week_ago.strftime('%Y%m%d')
end_date = today.strftime('%Y%m%d')

# 2. 데이터베이스 연결 및 테이블 생성
conn = sqlite3.connect('dart_spac.db')
cursor = conn.cursor()

# 정규 표현식 패턴
pattern = r"(\d+호스팩|스팩\d+호)"

# "스팩" 종목 리스트 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS spac_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spac_name TEXT,
    stock_code TEXT UNIQUE,
    corp_code TEXT UNIQUE,
    delisted TEXT
)
''')

# 1-2. DART에서 "스팩"이 포함된 종목 정보 가져오기 및 저장
def get_all_stock_info():
    all_list = dart.get_corp_list()
    spac_list = all_list.find_by_corp_name("스팩")
    spac_stocks = []

    for cl in spac_list:
        if re.search(pattern, cl.corp_name):
            #print(cl.corp_name + " " + cl.stock_code, " " + cl.corp_code)
            spac_stocks.append({
                'corp_name': cl.corp_name,
                'stock_code': cl.stock_code,
                'corp_code': cl.corp_code
            })


    print("total count : " + str(len(spac_stocks)))
    return spac_stocks

def update_spac_list():
    spac_stocks = get_all_stock_info()  # dart_fss를 사용하여 종목 정보 가져오기

    for stock in spac_stocks:
        spac_name = stock['corp_name']
        stock_code = stock['stock_code']
        corp_code = stock['corp_code']
        delisted = 'N'  # 신규 종목은 상폐 여부를 N으로 설정

        # DB에 종목 저장, 이미 있는 종목은 업데이트하지 않음
        cursor.execute('''
        INSERT OR IGNORE INTO spac_list (spac_name, stock_code, corp_code, delisted)
        VALUES (?, ?, ?, ?)
        ''', (spac_name, stock_code, corp_code, delisted))

    conn.commit()


# 1-3. 상폐 여부가 'N'인 종목들의 금일 공시 리스트 읽어오기 (corp_code 기반)
def get_today_disclosures():
    cursor.execute("SELECT corp_code FROM spac_list WHERE delisted = 'N'")
    active_corp_codes = cursor.fetchall()  # corp_code 목록 가져오기

    for corp_code_tuple in active_corp_codes:
        corp_code = corp_code_tuple[0]  # 튜플에서 corp_code 추출

        try:
            # OpenDartReader로 공시 정보 가져오기 (기간 설정)
            disclosures = dart.filings.search(corp_code, bgn_de=bgn_date, end_de=end_date)

            # disclosures가 None인 경우 처리
            if disclosures is None or len(disclosures) == 0:
                print(f"{corp_code}에 대한 금일 공시 정보가 없습니다.")
            else:
                print(f"공시 목록 for corp_code {corp_code}:")
                for disclosure in disclosures:  # 각 공시 정보 출력
                    url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure.rcp_no}"
                    print(disclosure.corp_name + " " + disclosure.report_nm + " " + url)

        except dart.errors.errors.NoDataReceived:
            # 조회된 데이터가 없을 경우 예외 처리
            print(f"{corp_code}에 대한 공시 데이터가 없습니다.")
        except Exception as e:
            # 그 외 다른 오류가 발생했을 경우 예외 처리
            print(f"{corp_code} 처리 중 오류 발생: {e}")

def get_today_prices():
    manager = StockManager()
    cursor.execute("SELECT stock_code FROM spac_list WHERE delisted = 'N'")
    active_corp_codes = cursor.fetchall()  # corp_code 목록 가져오기
    for corp_code_tuple in active_corp_codes:
        stock_code = corp_code_tuple[0]  # 튜플에서 corp_code 추출
        stock = manager.fetch_stock_info(stock_code, '2024-10-08')
        print(stock)

# 프로그램 실행
if __name__ == "__main__":
    #update_spac_list()
    get_today_disclosures()
    #get_today_prices()



# 연결 종료
conn.close()