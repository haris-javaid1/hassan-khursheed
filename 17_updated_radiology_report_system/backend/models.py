from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from datetime import datetime
from database import Base

class RadiologyReport(Base):
    __tablename__ = "radiology_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(50), unique=True, nullable=False)
    
    uhid = Column(String(50))
    sl_no = Column(String(50))
    reg_no = Column(String(50))
    patient_no = Column(String(50))
    patient_name = Column(String(255), nullable=False)
    
    report_date = Column(Date)
    age_sex = Column(String(50))
    origin_ethe = Column(String(100))
    ref_by = Column(String(255))
    
    film_no = Column(String(50))
    scan_time = Column(String(50))
    report_time = Column(String(50))
    tat = Column(String(50))
    scan_type = Column(String(100))
    
    doctor_description = Column(Text)
    impression = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)