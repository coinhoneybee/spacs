import FinanceDataReader as fdr

class StockManager:
    """
    주식 정보를 관리하고 제공하는 클래스
    """

    def __init__(self):
        self.stocks = {}

    def fetch_stock_info(self, code: str, date: str):
        """
        주식 코드를 통해 주식 정보를 가져와 StockData 객체로 저장
        """
        try:
            # 현재 날짜 기준으로 하루 전 데이터를 가져옵니다.
            df = fdr.DataReader(code, start=date)
            latest_data = df.iloc[-1]
            current_price = latest_data['Close']
            high_price = latest_data['High']
            low_price = latest_data['Low']
            #name = fdr.StockListing('KRX')[fdr.StockListing('KRX')['Symbol'] == code]['Name'].values[0]

            stock_data = StockData('', code, current_price, high_price, low_price)
            self.stocks[code] = stock_data
            return stock_data
        except Exception as e:
            print(f"주식 정보를 가져오는 중 오류가 발생했습니다: {e}")
            return None

    def get_stock_data(self, code: str):
        """
        저장된 주식 데이터를 반환. 없으면 fetch_stock_info를 호출하여 가져옵니다.
        """
        if code in self.stocks:
            return self.stocks[code]
        else:
            return self.fetch_stock_info(code)

    def update_stock_info(self, code: str):
        """
        특정 주식의 정보를 업데이트합니다.
        """
        return self.fetch_stock_info(code)

    def get_all_stocks(self):
        """
        현재 관리 중인 모든 주식 데이터를 반환합니다.
        """
        return list(self.stocks.values())









class StockData:
    """
    주식의 기본 정보를 담는 클래스
    """
    def __init__(self, name: str, code: str, current_price: float, high_price: float, low_price: float):
        self.name = name
        self.code = code
        self.current_price = current_price
        self.high_price = high_price
        self.low_price = low_price

    def __repr__(self):
        return (f"StockData(name={self.name}, code={self.code}, "
                f"current_price={self.current_price}, high_price={self.high_price}, "
                f"low_price={self.low_price})")