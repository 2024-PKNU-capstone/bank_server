from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from typing import List
from datetime import date, time, timedelta

app = FastAPI()

# MySQL 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="jiwon1923",
        database="bank"
    )

# 거래 내역 모델 정의
class TransactionDetail(BaseModel):
    lable: str
    amount: float
    transaction_type: str
    balance: float
    date: date
    time: str
    description: str

# 최종 응답 모델 정의
class TransactionResponse(BaseModel):
    fintechUseNum: str
    startDate: date
    endDate: date
    startTime: str  # 새로운 필드 추가
    endTime: str  # 새로운 필드 추가
    transactions: List[TransactionDetail]

# 거래내역 조회 API (GET 방식)
@app.get("/transactions", response_model=TransactionResponse)
def get_transactions(account_id: str, start_date: date, end_date: date, start_time: str, end_time: str):
    try:
        # 데이터베이스 연결
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # dict 형태로 결과 받음
        
        # SQL 쿼리 작성 (날짜 및 시간 조건 추가)
        query = """
        SELECT lable, amount, transaction_type, balance, date, time, description
        FROM transactions
        WHERE account_id = %s
        AND (
        (date = %s AND time >= %s) 
        OR 
        (date = %s AND time <= %s)
        OR 
        (date > %s AND date < %s)
        )
        """
        
        cursor.execute(query, (account_id, start_date, start_time, end_date, end_time, start_date, end_date))
        transactions = cursor.fetchall()
        
        # 결과가 없을 경우 예외 처리
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found for the given account and date range.")
        
        # 거래 내역의 time 필드를 timedelta에서 문자열로 변환
        for transaction in transactions:
            if isinstance(transaction['time'], timedelta):
                # timedelta 값을 HH:MM:SS 형식으로 변환
                total_seconds = int(transaction['time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                transaction['time'] = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                transaction['time'] = str(transaction['time'])  # 이미 문자열 형식이면 그대로 반환
        
        # 응답 구조 설정 (startTime과 endTime 추가)
        return {
            "fintechUseNum": account_id,
            "startDate": start_date,
            "endDate": end_date,
            "startTime": start_time,
            "endTime": end_time,
            "transactions": transactions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()
