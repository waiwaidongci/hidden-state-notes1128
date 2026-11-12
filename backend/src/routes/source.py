from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.controllers.dependencies import current_user,writers
from src.models import SequenceStudy,ObservationTrace,TraceCorrectionBatch
from src.schemas.study import StudyInput
from src.schemas.trace import TracePatch,CorrectionPreviewInput
from src.services.source import create_study,edit_trace
from src.services.corrections import preview_corrections,confirm_corrections
from src.utils.serialize import row
router=APIRouter()
@router.get('/studies')
def studies(db:Session=Depends(get_db),user=Depends(current_user)):return [row(s) for s in db.scalars(select(SequenceStudy).order_by(SequenceStudy.id))]
@router.post('/studies')
def create(data:StudyInput,db:Session=Depends(get_db),user=Depends(writers)):return create_study(db,data,user.email)
@router.get('/traces')
def traces(db:Session=Depends(get_db),user=Depends(current_user)):return [row(t) for t in db.scalars(select(ObservationTrace).order_by(ObservationTrace.id))]
@router.patch('/traces/{id}')
def trace(id:int,data:TracePatch,db:Session=Depends(get_db),user=Depends(writers)):return edit_trace(db,id,data,user.email)
@router.get('/corrections')
def corrections(study_id:int|None=None,db:Session=Depends(get_db),user=Depends(current_user)):
 query=select(TraceCorrectionBatch).order_by(TraceCorrectionBatch.id.desc())
 if study_id:query=query.where(TraceCorrectionBatch.study_id==study_id)
 return [row(b) for b in db.scalars(query)]
@router.post('/corrections/preview')
def preview(data:CorrectionPreviewInput,db:Session=Depends(get_db),user=Depends(writers)):return preview_corrections(db,data,user.email)
@router.post('/corrections/{id}/confirm')
def confirm(id:int,db:Session=Depends(get_db),user=Depends(writers)):return confirm_corrections(db,id,user.email)
