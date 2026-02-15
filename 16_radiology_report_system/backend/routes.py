from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import RadiologyReport
from word_export import create_table_format, create_list_format, create_detailed_format

# Create router
router = APIRouter()

# Pydantic model for request data
class ReportCreate(BaseModel):
    uhid: Optional[str] = None
    sl_no: Optional[str] = None
    reg_no: Optional[str] = None
    patient_no: Optional[str] = None
    patient_name: str
    report_date: Optional[str] = None
    age_sex: Optional[str] = None
    origin_ethe: Optional[str] = None
    ref_by: Optional[str] = None
    film_no: Optional[str] = None
    scan_time: Optional[str] = None
    report_time: Optional[str] = None
    tat: Optional[str] = None
    scan_type: Optional[str] = None
    doctor_description: Optional[str] = None
    impression: Optional[str] = None


# Route 1: Create new report
@router.post("/reports")
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    try:
        new_report = RadiologyReport(**report.dict())
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        return {
            "success": True,
            "id": new_report.id,
            "message": "Report created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Route 2: Get all reports
@router.get("/reports")
def get_all_reports(db: Session = Depends(get_db)):
    try:
        reports = db.query(RadiologyReport).order_by(
            RadiologyReport.created_at.desc()
        ).all()
        
        # Convert to dictionary
        reports_list = []
        for report in reports:
            reports_list.append({
                "id": report.id,
                "uhid": report.uhid,
                "patient_name": report.patient_name,
                "patient_no": report.patient_no,
                "report_date": str(report.report_date) if report.report_date else None,
                "age_sex": report.age_sex,
                "scan_type": report.scan_type,
                "created_at": str(report.created_at)
            })
        
        return reports_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route 3: Get single report by ID
@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    try:
        report = db.query(RadiologyReport).filter(
            RadiologyReport.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route 4: Export report to Word
@router.get("/reports/{report_id}/export")
def export_report(report_id: int, format: str, db: Session = Depends(get_db)):
    try:
        # Get report from database
        report = db.query(RadiologyReport).filter(
            RadiologyReport.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Generate Word document based on format
        if format == "table":
            file_stream = create_table_format(report)
        elif format == "list":
            file_stream = create_list_format(report)
        elif format == "detailed":
            file_stream = create_detailed_format(report)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        filename = f"radiology_report_{report_id}_{format}.docx"
        
        # Return file as download
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))