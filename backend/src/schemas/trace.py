from pydantic import BaseModel,Field,ConfigDict
class TraceInput(BaseModel):
 model_config=ConfigDict(str_strip_whitespace=True)
 reference:str=Field(min_length=1,max_length=100)
 tokens:list[str]=Field(min_length=1,max_length=200)
class TracePatch(BaseModel):
 tokens:list[str]=Field(min_length=1,max_length=200)
 base_revision:int|None=Field(default=None,ge=0)
class CorrectionItem(BaseModel):
 trace_id:int=Field(gt=0,strict=True)
 tokens:list[str]=Field(min_length=1,max_length=200)
class CorrectionPreviewInput(BaseModel):
 study_id:int=Field(gt=0,strict=True)
 items:list[CorrectionItem]=Field(min_length=1,max_length=240)
