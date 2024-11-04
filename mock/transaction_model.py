from sqlalchemy import Column, Integer, String, Float, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 고유 ID
    account_id = Column(String, index=True, nullable=False)  # 계좌 ID (파일명)
    amount = Column(Float, nullable=False)  # 거래 금액
    label = Column(String(50),nullable=False) # 구분 (입금/출금 등)
    transaction_type = Column(String(50), nullable=False)  # 거래 구분 (체크카드,자동이체,일반입금..)
    date = Column(Date, nullable=False)  # 거래 날짜
    time = Column(Time, nullable=False)  # 거래 시간
    balance = Column(Float)  # 잔액
    description = Column(String(255))  # 거래 설명
