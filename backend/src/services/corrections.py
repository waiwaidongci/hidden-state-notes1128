from datetime import datetime,timezone
from sqlalchemy import select
from fastapi import HTTPException
from src.models import SequenceStudy,ObservationTrace,TraceCorrectionBatch
from src.utils.serialize import row
from .validation import validate_traces
from .audit import record

def preview_corrections(db,data,actor):
 study=db.get(SequenceStudy,data.study_id)
 if not study:raise HTTPException(404,'研究不存在')
 ids=[item.trace_id for item in data.items]
 if len(ids)!=len(set(ids)):raise HTTPException(422,'同一轨迹在一批纠错中只能出现一次')
 traces={t.id:t for t in db.scalars(select(ObservationTrace).where(ObservationTrace.id.in_(ids)))}
 if len(traces)!=len(ids) or any(t.study_id!=study.id for t in traces.values()):raise HTTPException(422,'轨迹不属于该研究或不存在')
 try:validate_traces(study.symbols,[{'reference':str(i.trace_id),'tokens':i.tokens} for i in data.items])
 except ValueError as error:raise HTTPException(422,str(error))
 items=[{'trace_id':t.trace_id,'reference':traces[t.trace_id].reference,'base_revision':traces[t.trace_id].revision,'before':traces[t.trace_id].tokens,'after':t.tokens} for t in data.items]
 batch=TraceCorrectionBatch(study_id=study.id,items=items,created_by=actor);db.add(batch);db.commit()
 record(db,actor,'trace.batch_previewed',{'batch_id':batch.id,'study_id':study.id,'items':len(items)});return row(batch)

def confirm_corrections(db,id,actor):
 batch=db.scalar(select(TraceCorrectionBatch).where(TraceCorrectionBatch.id==id).with_for_update())
 if not batch:raise HTTPException(404,'纠错预览不存在')
 if batch.status=='applied':return {**row(batch),'duplicated':True}
 if batch.status=='conflicted':raise HTTPException(409,conflict_message(batch.conflicts))
 traces={t.id:t for t in db.scalars(select(ObservationTrace).where(ObservationTrace.id.in_([i['trace_id'] for i in batch.items])).order_by(ObservationTrace.id).with_for_update())}
 conflicts=[{'trace_id':i['trace_id'],'reference':i['reference'],'base_revision':i['base_revision'],'current_revision':traces[i['trace_id']].revision if i['trace_id'] in traces else None,'current_tokens':traces[i['trace_id']].tokens if i['trace_id'] in traces else None} for i in batch.items if i['trace_id'] not in traces or traces[i['trace_id']].revision!=i['base_revision']]
 if conflicts:
  batch.status='conflicted';batch.conflicts=conflicts;db.commit()
  record(db,actor,'trace.batch_conflicted',{'batch_id':id,'study_id':batch.study_id,'traces':[c['trace_id'] for c in conflicts]})
  raise HTTPException(409,conflict_message(conflicts))
 for item in batch.items:
  trace=traces[item['trace_id']];trace.tokens=item['after'];trace.revision+=1
 batch.status='applied';batch.confirmed_by=actor;batch.confirmed_at=datetime.now(timezone.utc);db.commit()
 record(db,actor,'trace.batch_applied',{'batch_id':id,'study_id':batch.study_id,'items':len(batch.items),'changed':sum(1 for i in batch.items if i['before']!=i['after'])})
 return {**row(batch),'duplicated':False}

def conflict_message(conflicts):
 refs='、'.join(c['reference'] for c in conflicts[:5])+(' 等' if len(conflicts)>5 else '')
 return f'整批纠错被拒绝：{refs}共{len(conflicts)}条已被他人改动，未冲突条目也保持原样，请重新生成预览'
