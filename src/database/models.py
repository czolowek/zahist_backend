from typing import List
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

from src.database.base import Base
from src.database.associative_tables import prod_rev_assoc, user_prod_assoc, user_shop_list_assoc, shop_list_prod_assoc


@dataclass
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    text: Mapped[str] = mapped_column(String())
    grade: Mapped[str] = mapped_column(String())


@dataclass
class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    img_url: Mapped[str] = mapped_column(String())
    price: Mapped[float] = mapped_column()
    reviews: Mapped[List[Review]] = relationship(secondary=prod_rev_assoc)


@dataclass
class ShopList(Base):
    __tablename__ = "shop_list"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    products: Mapped[List[Product]] = relationship(secondary=shop_list_prod_assoc)


@dataclass
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    email: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    _password: Mapped[str] = mapped_column(String(), nullable=False)
    products_cart: Mapped[List[Product]] = relationship(secondary=user_prod_assoc)
    shop_list: Mapped[List[ShopList]] = relationship(secondary=user_shop_list_assoc)

    @property
    def password(self):
        return "Don`t use this"

    @password.setter
    def password(self, pwd):
        self._password = generate_password_hash(pwd)

    def create_tokens(self, pwd):
        if check_password_hash(self._password, pwd):
            return dict(
                access_token=create_access_token(identity=self.id),
                refresh_token=create_refresh_token(identity=self.id)
            )