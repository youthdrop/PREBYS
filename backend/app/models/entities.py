from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attorney(Base):
    __tablename__ = 'attorneys'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='attorney')


class Judge(Base):
    __tablename__ = 'judges'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    clerk_telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    courtroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='judge')


class Prosecutor(Base):
    __tablename__ = 'prosecutors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='prosecutor')


class Volunteer(Base):
    __tablename__ = 'volunteers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    availability: Mapped[str | None] = mapped_column(Text, nullable=True)
    travel_courts: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Intake(Base):
    __tablename__ = 'intakes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    case_numbers: Mapped[str | None] = mapped_column(String(255), nullable=True)
    charges: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_person_telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_person_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    volunteer_assigned: Mapped[str | None] = mapped_column(String(255), nullable=True)
    maximum_exposure: Mapped[str | None] = mapped_column(String(255), nullable=True)
    court_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_court_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_court_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    court_site: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hearing_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_saved_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    attorney_id: Mapped[int | None] = mapped_column(ForeignKey('attorneys.id'), nullable=True)
    judge_id: Mapped[int | None] = mapped_column(ForeignKey('judges.id'), nullable=True)
    prosecutor_id: Mapped[int | None] = mapped_column(ForeignKey('prosecutors.id'), nullable=True)

    attorney = relationship('Attorney', back_populates='cases')
    judge = relationship('Judge', back_populates='cases')
    prosecutor = relationship('Prosecutor', back_populates='cases')
    notes = relationship('CaseNote', back_populates='intake', cascade='all, delete-orphan', order_by='desc(CaseNote.created_at)')


class CaseNote(Base):
    __tablename__ = 'case_notes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    intake_id: Mapped[int] = mapped_column(ForeignKey('intakes.id', ondelete='CASCADE'), nullable=False, index=True)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    service_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_saved_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    intake = relationship('Intake', back_populates='notes')
