from datetime import datetime

from pydantic import BaseModel

class LinksCreate(BaseModel):
    user_id: int
    long_link: str
    custom_alias: str
    expires_at: datetime

class LinksRedirect(BaseModel):
    short_link: str

class LinksDelete(BaseModel):
    short_link: str

class LinksChange(BaseModel):
    short_link: str

class LinkPopularity(BaseModel):
    short_link: str

class LinkOriginal(BaseModel):
    long_link: str