from typing import Literal
from pydantic import BaseModel, field_validator, Field, model_validator
from datetime import date


class AuthReg(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name:  str = Field(min_length=1, max_length=50)
    patronymic: str | None = Field(min_length=1, max_length=50, default=None)
    email:      str = Field(min_length=1, max_length=320)
    password:   str = Field(min_length=8, max_length=70)
    password2:  str = Field(min_length=8, max_length=70, exclude=True)  #exclude=True автоматически удалит это поле при .model_dump()

    #Проверяем совпадают ли пароли
    @model_validator(mode='after')
    def check_passwords(self):
        if self.password != self.password2:
            raise ValueError('Пароли не совпадают')
        return self


class AuthCreateAccount(BaseModel):
    role_id:    int  
    first_name: str
    last_name:  str 
    patronymic: str | None = None
    email:      str
    hashed_password: str 