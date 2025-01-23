from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Create declarative base using the new syntax
Base = declarative_base()

class Fund(Base):
    __tablename__ = 'funds'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    aum = Column(Float)
    currency = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = relationship("Holding", back_populates="fund")
    sectors = relationship("SectorAllocation", back_populates="fund")

class Holding(Base):
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'))
    stock_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    percentage = Column(Float)
    value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    fund = relationship("Fund", back_populates="holdings")

class SectorAllocation(Base):
    __tablename__ = 'sector_allocations'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'))
    name = Column(String(100), nullable=False)
    allocation = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    fund = relationship("Fund", back_populates="sectors")
