import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class EmailCreate(BaseModel):
    recipient: EmailStr  # Ensures valid email address
    subject: str
    body: str

    model_config = ConfigDict(from_attributes=True)

        
class EmailModel(EmailCreate):
    id: int
    status: str  # E.g., 'sent', 'failed'
    created_at: datetime.datetime