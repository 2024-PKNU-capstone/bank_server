import pandas as pd
import os
import mysql.connector
from transaction_model import Transaction  # 앞서 정의한 Transaction 모델을 임포트
import time

# MySQL 연결 설정
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jiwon1923",
    database="bank"
)

cursor = connection.cursor()

file_path = "mock\exel\\120240065088961100942100.xlsx"
##file_name = os.path.splitext(os.path.basename(file_path))[0]
file_name = "120240065088961100509102"


df = pd.read_excel(file_path)

# '거래일시'를 datetime 형식으로 변환
df['거래일시'] = pd.to_datetime(df['거래일시'])

# '거래일시'를 date와 time으로 분리
df['거래일자'] = df['거래일시'].dt.date
df['거래시간'] = df['거래일시'].dt.time

# 사용하지 않는 '거래일시' 컬럼 삭제
df = df.drop(columns=['거래일시'])
df = df.drop(columns=['메모'])
print(df.head())

#df.columns = ['account_id','type','amount','transaction_type','balance', 'date', 'time', 'description']

# 컬럼 이름을 데이터베이스 필드에 맞게 변환
df.columns = ['lable', 'amount', 'balance', 'transaction_type', 'description', 'date', 'time']

# 'amount' 및 'balance' 열에서 쉼표 제거하고, float으로 변환
df['amount'] = df['amount'].replace({',': ''}, regex=True).astype(float)
df['balance'] = df['balance'].replace({',': ''}, regex=True).astype(float)

# 날짜와 시간 변환
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date  # 날짜를 'date'로 변환
df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.time  # 시간을 'time'으로 변환
print(df.head())


# 데이터베이스에 저장
def insert_transaction_data(df: pd.DataFrame, file_name: str, db: cursor):
    for _, row in df.iterrows():
        try:
            print(f"Inserting row: {row}")
            
            # 각 필드를 출력해서 확인
            print(f"Values: {file_name}, {row['lable']}, {row['amount']}, {row['transaction_type']}, {row['balance']}, {row['date']}, {row['time']}, {row['description']}")
            
            # SQL 쿼리 작성
            query = """
            INSERT INTO transactions (account_id, lable, amount, transaction_type, balance, date, time, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                str(file_name),
                row['lable'],
                row['amount'],
                row['transaction_type'],
                row['balance'],
                row['date'],
                row['time'],
                row['description']
            )
            
            cursor.execute(query, values)  # 쿼리 실행
            connection.commit()
            time.sleep(10)
        except Exception as e:
            print(f"Error inserting row: {row}, error: {e}")
    
      # 데이터베이스에 변경 사항 커밋

# 데이터 삽입 함수 호출
insert_transaction_data(df, file_name, cursor)

# 연결 종료
cursor.close()
connection.close()