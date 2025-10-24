from . import db
from sqlalchemy import (
    Column, Integer, String, Text, Enum, DateTime, text,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum



class OrderStatus(enum.Enum):
    PROCESSING = 'PROCESSING'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'


class InteractionType(enum.Enum):
    VIEW = 'VIEW'
    ADD_TO_CART = 'ADD_TO_CART'
    PURCHASE = 'PURCHASE'


class Cart(db.Model):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now(), server_onupdate=func.now())

    # Relationship
    user = relationship('User', back_populates='cart')
    items = relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")


class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('cart.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1, server_default=text("1"))

    # Relationship
    cart = relationship('Cart', back_populates='items')
    product = relationship('Product', back_populates='cart_items')

    # Unique Constraint
    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', name='_cart_product_uc'),
    )


class Order(db.Model):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    address = Column(Text, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PROCESSING)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Integer, nullable=False)

    # Relationship
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship('User', back_populates='feedbacks')
    product = relationship('Product', back_populates='feedbacks')

    # Unique Constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='_user_product_feedback_uc'),
    )


class Interaction(db.Model):
    __tablename__ = 'interaction'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    type = Column(Enum(InteractionType), nullable=False)
    timestamp = Column(DateTime, default=func.now())

    # Relationship
    user = relationship('User', back_populates='interactions')
    product = relationship('Product', back_populates='interactions')

    # Index
    __table_args__ = (
        Index('idx_user_product_type', 'user_id', 'product_id', 'type'),
    )