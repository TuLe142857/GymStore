from . import db
from sqlalchemy import (
    Column, Integer, String, Text, Float, Numeric, Boolean, text,
    DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ProductIngredient(db.Model):
    __tablename__ = 'product_ingredient'

    product_id = Column(Integer, ForeignKey('product.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
    quantity = Column(Float, nullable=False)

    # Relationship
    product = relationship('Product', back_populates='ingredient_associations')
    ingredient = relationship('Ingredient', back_populates='product_associations')


class Product(db.Model):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    desc = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    weight_grams = Column(Float, nullable=False)
    serving_size_grams = Column(Float, nullable=False)
    price = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))

    avg_rating = Column(Numeric(2, 1), nullable=False, default=0.0, server_default=text("0.0"))
    sold_quantity = Column(Integer, nullable=False, default=0, server_default=text("0"))
    feedback_count = Column(Integer, nullable=False, default=0, server_default=text("0"))

    category_id = Column(Integer, ForeignKey('category.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    brand_id = Column(Integer, ForeignKey('brand.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now(), server_onupdate=func.now())

    # Relationship
    category = relationship('Category', back_populates='products')
    brand = relationship('Brand', back_populates='products')
    ingredient_associations = relationship('ProductIngredient', back_populates='product', cascade="all, delete-orphan")
    feedbacks = relationship('Feedback', back_populates='product', cascade="all, delete-orphan")
    interactions = relationship('Interaction', back_populates='product', cascade="all, delete-orphan")
    cart_items = relationship('CartItem', back_populates='product', cascade="all, delete-orphan")
    order_items = relationship('OrderItem', back_populates='product', cascade="all, delete-orphan")


class Category(db.Model):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    products = relationship('Product', back_populates='category')


class Brand(db.Model):
    __tablename__ = 'brand'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    products = relationship('Product', back_populates='brand')


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    desc = Column(Text, nullable=True)
    measurement_unit = Column(String(20), nullable=False, default="g", server_default=text("'g'"))

    product_associations = relationship('ProductIngredient', back_populates='ingredient', cascade="save-update")