from sqlalchemy import Column, Integer, String, JSON
from .database import Base


class SMSConfig(Base):
    __tablename__ = "sms_config"

    id = Column(Integer, primary_key=True, index=True)
    main_gateway_url = Column(String, index=True)
    backup_gateway_url = Column(String, index=True)
    main_gateway_password = Column(String, index=True)
    backup_gateway_api_id = Column(String, index=True)
    regions = Column(JSON)


class TextSMS(Base):
    __tablename__ = "textsms"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)


class SMSBuffer(Base):
    __tablename__ = "sms_buffer"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String, index=True)
    text = Column(String, index=True)
    password = Column(String, index=True)
