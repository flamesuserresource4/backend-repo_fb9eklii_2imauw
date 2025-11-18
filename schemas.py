"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (kept for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Stripe-like models for our fintech demo
class Customer(BaseModel):
    """
    Customers collection schema
    Collection name: "customer"
    """
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email")
    business: Optional[str] = Field(None, description="Business name if applicable")

class Payment(BaseModel):
    """
    Payments collection schema
    Collection name: "payment"
    """
    amount: int = Field(..., ge=1, description="Amount in smallest currency unit (e.g., cents)")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code, e.g., USD")
    description: Optional[str] = Field(None, description="Payment description")
    customer_id: Optional[str] = Field(None, description="Related customer id")
    status: Literal['authorized','captured','failed'] = Field('authorized', description="Payment status")
