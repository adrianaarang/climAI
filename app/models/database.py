from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# CATÁLOGOS

class Province(Base):
    __tablename__ = "provinces"
    province_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    stations = relationship("Station", back_populates="province", cascade="all, delete-orphan", passive_deletes=True)

class Unit(Base):
    __tablename__ = "units"
    unit_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

class Level(Base):
    __tablename__ = "levels"
    level_id = Column(Integer, primary_key=True, index=True)
    color = Column(String, nullable=False)

# ENTIDADES PRINCIPALES

class Station(Base):
    __tablename__ = "stations"
    station_id = Column(Integer, primary_key=True, index=True)
    idema = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    
    province_id = Column(Integer, ForeignKey("provinces.province_id", ondelete="CASCADE"))
    
    province = relationship("Province", back_populates="stations")
    records = relationship("Record", back_populates="station", cascade="all, delete-orphan", passive_deletes=True)

class Record(Base):
    __tablename__ = "records"
    record_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    rain = Column(Float)
    
    station_id = Column(Integer, ForeignKey("stations.station_id", ondelete="CASCADE"))
    
    station = relationship("Station", back_populates="records")
    triggered_alerts = relationship("RecordAlert", back_populates="record", cascade="all, delete-orphan", passive_deletes=True)

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    telegram_id = Column(String)
    
    notifications = relationship("SentAlert", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

# SISTEMA DE ALERTAS

class Metric(Base):
    __tablename__ = "metrics"
    metric_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.unit_id", ondelete="SET NULL"))
    
    unit = relationship("Unit")

class Threshold(Base):
    __tablename__ = "thresholds"
    threshold_id = Column(Integer, primary_key=True, index=True)
    lower_limit = Column(Float)
    upper_limit = Column(Float)
    message = Column(Text)
    level_id = Column(Integer, ForeignKey("levels.level_id", ondelete="CASCADE"))
    
    level = relationship("Level")

class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.metric_id", ondelete="CASCADE"))
    threshold_id = Column(Integer, ForeignKey("thresholds.threshold_id", ondelete="CASCADE"))
    
    metric = relationship("Metric")
    threshold = relationship("Threshold")
    linked_records = relationship("RecordAlert", back_populates="alert", cascade="all, delete-orphan", passive_deletes=True)
    notified_users = relationship("SentAlert", back_populates="alert", cascade="all, delete-orphan", passive_deletes=True)

# TABLAS RELACIONALES

class RecordAlert(Base):
    __tablename__ = "records_alerts"
    record_alert_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("records.record_id", ondelete="CASCADE"))
    alert_id = Column(Integer, ForeignKey("alerts.alert_id", ondelete="CASCADE"))
    
    record = relationship("Record", back_populates="triggered_alerts")
    alert = relationship("Alert", back_populates="linked_records")

class SentAlert(Base):
    __tablename__ = "sent_alerts"
    sent_alert_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    alert_id = Column(Integer, ForeignKey("alerts.alert_id", ondelete="CASCADE"))
    sent_at = Column(DateTime, index=True)
    
    user = relationship("User", back_populates="notifications")
    alert = relationship("Alert", back_populates="notified_users")