from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey,String,JSON,DateTime
from datetime import datetime,timezone
from src.config.database import Base
class TraceCorrectionBatch(Base):
 __tablename__='trace_correction_batches'
 id:Mapped[int]=mapped_column(primary_key=True)
 study_id:Mapped[int]=mapped_column(ForeignKey('sequence_studies.id'))
 status:Mapped[str]=mapped_column(String(24),default='pending')
 items:Mapped[list]=mapped_column(JSON)
 conflicts:Mapped[list|None]=mapped_column(JSON,nullable=True)
 created_by:Mapped[str]=mapped_column(String(120))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
 confirmed_by:Mapped[str|None]=mapped_column(String(120),nullable=True)
 confirmed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
