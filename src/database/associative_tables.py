from sqlalchemy import ForeignKey, Table, Column

from src.database.base import Base


prod_rev_assoc = Table(
    "prod_rev_assoc",
    Base.metadata,
    Column("prod_id", ForeignKey("products.id"), primary_key=True),
    Column("rev_id", ForeignKey("reviews.id"), primary_key=True)
)


user_prod_assoc = Table(
    "user_prod_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("prod_id", ForeignKey("products.id"), primary_key=True)
)


user_shop_list_assoc = Table(
    "user_shop_list_assoc",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("shop_list_id", ForeignKey("shop_list.id"), primary_key=True)
)


shop_list_prod_assoc = Table(
    "shop_list_prod_assoc",
    Base.metadata,
    Column("shop_list_id", ForeignKey("shop_list.id"), primary_key=True),
    Column("prod_id", ForeignKey("products.id"), primary_key=True)
)