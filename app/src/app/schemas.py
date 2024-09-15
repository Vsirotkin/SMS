from pydantic import BaseModel
from typing import Dict, Any


class SMSRequest(BaseModel):
    recipient: str
    text: str
    password: str


class SMSConfigBase(BaseModel):
    main_gateway_url: str
    backup_gateway_url: str
    main_gateway_password: str
    backup_gateway_api_id: str
    regions: Dict[str, Any]


class SMSConfigCreate(SMSConfigBase):
    pass


class SMSConfig(SMSConfigBase):
    id: int

    class Config:
        from_attributes = True  # Заменяем orm_mode на from_attributes


class TextSMSBase(BaseModel):
    text: str


class TextSMSCreate(TextSMSBase):
    pass


class TextSMS(TextSMSBase):
    id: int

    class Config:
        from_attributes = True  # Заменяем orm_mode на from_attributes


class SMSBufferBase(BaseModel):
    recipient: str
    text: str
    password: str


class SMSBufferCreate(SMSBufferBase):
    pass


class SMSBuffer(SMSBufferBase):
    id: int

    class Config:
        from_attributes = True  # Заменяем orm_mode на from_attributes
