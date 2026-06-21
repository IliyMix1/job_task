from sqlalchemy import Text, BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from datetime import date, datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    #Описываем столбцы таблицы
    user_id:         Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id:         Mapped[int] = mapped_column(BigInteger, ForeignKey('roles.role_id'), nullable=False)
    first_name:      Mapped[str] = mapped_column(Text, nullable=False)
    last_name:       Mapped[str] = mapped_column(Text, nullable=False)
    patronymic:      Mapped[str | None] = mapped_column(Text, nullable=True)   #Это отчество
    phone_number:    Mapped[str | None] = mapped_column(Text, nullable=True)
    email:           Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True, server_default='true', nullable=False)

    #Описываем связи между таблицами
    role: Mapped['Role'] = relationship('Role', back_populates='users') 


class Role(Base):
    __tablename__ = 'roles'

    #Описываем столбцы таблицы
    role_id:   Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    #Описываем связи между таблицами
    users:        Mapped[list['User']]        = relationship('User',        back_populates='role') 
    access_rules: Mapped[list['Access_rule']] = relationship('Access_rule', back_populates='role')  


class Resource(Base):
    __tablename__ = 'resources'

    #Описываем столбцы таблицы
    resource_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resource_name:   Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    #Описываем связи между таблицами
    access_rules: Mapped[list['Access_rule']] = relationship('Access_rule', back_populates='resource')


class Access_rule(Base):
    __tablename__ = 'access_rules'

    #Описываем столбцы таблицы
    role_id:        Mapped[int]  = mapped_column(BigInteger, ForeignKey('roles.role_id',         ondelete='CASCADE'), primary_key=True)
    resource_id:    Mapped[int]  = mapped_column(BigInteger, ForeignKey('resources.resource_id', ondelete='CASCADE'), primary_key=True)
    #Доступ к созданию
    can_create:     Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    #Доступ к чтению
    can_read_own:   Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_read_all:   Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    #Доступ к изменению
    can_update_own: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_update_all: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    #Доступ к удалению
    can_delete_own: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete_all: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #Описываем связи между таблицами
    role:     Mapped['Role']     = relationship('Role',     back_populates='access_rules') 
    resource: Mapped['Resource'] = relationship('Resource', back_populates='access_rules')


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    jti:        Mapped[str]      = mapped_column(Text, primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)