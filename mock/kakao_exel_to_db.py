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

# 엑셀 파일 경로
file_path = "mock/exel/commit_exel.xlsx"
file_name = "120240065088961100509102"  # account_id로 사용

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

# '거래일시'를 date와 time으로 분리
df['거래일시'] = pd.to_datetime(df['거래일시'])
df['date'] = df['거래일시'].dt.date
df['time'] = df['거래일시'].dt.time

# 거래금액 열 생성: '입금'은 양수, '출금'은 음수로 설정
df['거래금액'] = df.apply(lambda row: row['입금'] if pd.notnull(row['입금']) else -row['출금'], axis=1)

# label 값 설정: 거래금액이 양수면 '입금', 음수면 '출금'
df['label'] = df['거래금액'].apply(lambda x: '입금' if x > 0 else '출금')

# 필요한 컬럼만 남기기
df = df[['label', '거래금액', '거래 후 잔액', '거래구분', '내용', '입출금은행', 'date', 'time']]
df.columns = ['label', 'amount', 'balance', 'transaction_type', 'description', 'bank', 'date', 'time']

# 금액 열과 잔액 열을 float로 변환 후 정수로 변환 (소수점 이하 제거)
df['amount'] = df['amount'].replace({',': ''}, regex=True).astype(float).astype(int)
df['balance'] = df['balance'].replace({',': ''}, regex=True).astype(float).astype(int)

# 데이터베이스에 저장 함수 정의
def insert_transaction_data(df: pd.DataFrame, file_name: str, cursor):
    for _, row in df.iterrows():
        try:
            # 입금인 경우 description을 내용(입출금은행)으로 포맷 변경
            if row['label'] == '입금':
                formatted_description = f"{row['description']} ({row['bank']})"
            else:
                formatted_description = row['description']
            
            # SQL 쿼리 작성
            query = """
            INSERT INTO transactions (account_id, label, amount, transaction_type, balance, date, time, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                str(file_name),
                row['label'],
                row['amount'],
                row['transaction_type'],
                row['balance'],
                row['date'],
                row['time'],
                formatted_description
            )
            
            cursor.execute(query, values)  # 쿼리 실행
            connection.commit()
        except Exception as e:
            print(f"Error inserting row: {row}, error: {e}")

# 데이터 삽입 함수 호출
insert_transaction_data(df, file_name, cursor)

# 연결 종료
cursor.close()
connection.close()
