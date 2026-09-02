from datetime import date, time, datetime
from pydantic import BaseModel, EmailStr


class AttorneyBase(BaseModel):
    name: str
    business_name: str | None = None
    email: EmailStr | None = None
    telephone: str | None = None
    notes: str | None = None
    note_date: date | None = None


class AttorneyCreate(AttorneyBase):
    pass


class AttorneyRead(AttorneyBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class JudgeBase(BaseModel):
    name: str
    clerk_telephone: str | None = None
    courtroom: str | None = None
    notes: str | None = None
    note_date: date | None = None


class JudgeCreate(JudgeBase):
    pass


class JudgeRead(JudgeBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class ProsecutorBase(BaseModel):
    name: str
    email: EmailStr | None = None
    telephone: str | None = None
    notes: str | None = None
    note_date: date | None = None


class ProsecutorCreate(ProsecutorBase):
    pass


class ProsecutorRead(ProsecutorBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class VolunteerBase(BaseModel):
    name: str
    email: EmailStr | None = None
    telephone: str | None = None
    availability: str | None = None
    travel_courts: str | None = None
    training_completed_date: date | None = None
    training_type: str | None = None
    notes: str | None = None


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerRead(VolunteerBase):
    id: int
    class Config:
        from_attributes = True


class IntakeBase(BaseModel):
    name: str
    case_numbers: str | None = None
    charges: str | None = None
    contact_person: str | None = None
    contact_person_telephone: str | None = None
    contact_person_email: EmailStr | None = None
    volunteer_assigned: str | None = None
    maximum_exposure: str | None = None
    court_location: str | None = None
    next_court_date: date | None = None
    next_court_time: time | None = None
    court_site: str | None = None
    hearing_type: str | None = None
    attorney_id: int | None = None
    judge_id: int | None = None
    prosecutor_id: int | None = None
    service_type: str | None = None
    case_note: str | None = None
    case_note_date: date | None = None
    time_saved_hours: float | None = None


class IntakeCreate(IntakeBase):
    attorney: AttorneyCreate | None = None
    judge: JudgeCreate | None = None
    prosecutor: ProsecutorCreate | None = None


class IntakeRead(IntakeBase):
    id: int
    created_at: datetime
    attorney_name: str | None = None
    judge_name: str | None = None
    prosecutor_name: str | None = None
    class Config:
        from_attributes = True


class CaseNoteCreate(BaseModel):
    note: str
    service_type: str | None = None
    note_date: date | None = None
    time_saved_hours: float | None = None


class CaseNoteRead(CaseNoteCreate):
    id: int
    intake_id: int
    created_by_email: EmailStr | None = None
    created_by_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
