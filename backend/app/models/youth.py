from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Youth(Base):
    __tablename__='youth'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(255),nullable=False,index=True)
    telephone: Mapped[str|None]=mapped_column(String(50))
    email: Mapped[str|None]=mapped_column(String(255))
    gender: Mapped[str|None]=mapped_column(String(100))
    race: Mapped[str|None]=mapped_column(String(100))
    birthdate: Mapped[date|None]=mapped_column(Date)
    enrollment_date: Mapped[date|None]=mapped_column(Date)
    status: Mapped[str]=mapped_column(String(50),default='active')
    assigned_staff_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'),index=True)
    next_contact_date: Mapped[date|None]=mapped_column(Date,index=True)
    emergency_contact_name: Mapped[str|None]=mapped_column(String(255))
    emergency_contact_phone: Mapped[str|None]=mapped_column(String(50))
    aces_pre_score: Mapped[int|None]=mapped_column(Integer)
    aces_post_score: Mapped[int|None]=mapped_column(Integer)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    notes=relationship('YouthCaseNote',back_populates='youth',cascade='all, delete-orphan',order_by='desc(YouthCaseNote.created_at)')
    documents=relationship('YouthDocument',back_populates='youth',cascade='all, delete-orphan')

class YouthCaseNote(Base):
    __tablename__='youth_case_notes'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    youth_id: Mapped[int]=mapped_column(ForeignKey('youth.id',ondelete='CASCADE'),index=True)
    note_type: Mapped[str|None]=mapped_column(String(100))
    contact_method: Mapped[str|None]=mapped_column(String(100))
    note: Mapped[str]=mapped_column(Text,nullable=False)
    next_action: Mapped[str|None]=mapped_column(Text)
    next_contact_date: Mapped[date|None]=mapped_column(Date)
    confidential: Mapped[bool]=mapped_column(Boolean,default=False)
    created_by_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'))
    created_by_name: Mapped[str|None]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    youth=relationship('Youth',back_populates='notes')

class Service(Base):
    __tablename__='services'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(255),nullable=False,unique=True)
    category: Mapped[str|None]=mapped_column(String(100))
    description: Mapped[str|None]=mapped_column(Text)
    active: Mapped[bool]=mapped_column(Boolean,default=True)

class YouthService(Base):
    __tablename__='youth_services'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    youth_id: Mapped[int]=mapped_column(ForeignKey('youth.id',ondelete='CASCADE'),index=True)
    service_id: Mapped[int]=mapped_column(ForeignKey('services.id'))
    service_date: Mapped[date]=mapped_column(Date,default=date.today)
    status: Mapped[str]=mapped_column(String(50),default='provided')
    notes: Mapped[str|None]=mapped_column(Text)

class Activity(Base):
    __tablename__='activities'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    title: Mapped[str]=mapped_column(String(255),nullable=False)
    activity_date: Mapped[date]=mapped_column(Date,index=True)
    start_time: Mapped[str|None]=mapped_column(String(20))
    end_time: Mapped[str|None]=mapped_column(String(20))
    location: Mapped[str|None]=mapped_column(String(255))
    description: Mapped[str|None]=mapped_column(Text)
    staff_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'))

class ActivityParticipant(Base):
    __tablename__='activity_participants'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    activity_id: Mapped[int]=mapped_column(ForeignKey('activities.id',ondelete='CASCADE'))
    youth_id: Mapped[int]=mapped_column(ForeignKey('youth.id',ondelete='CASCADE'))
    attendance_status: Mapped[str]=mapped_column(String(50),default='scheduled')

class Referral(Base):
    __tablename__='referrals'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    youth_id: Mapped[int]=mapped_column(ForeignKey('youth.id',ondelete='CASCADE'),index=True)
    referral_type: Mapped[str]=mapped_column(String(100))
    organization_name: Mapped[str]=mapped_column(String(255))
    contact_name: Mapped[str|None]=mapped_column(String(255))
    telephone: Mapped[str|None]=mapped_column(String(50))
    email: Mapped[str|None]=mapped_column(String(255))
    referral_date: Mapped[date]=mapped_column(Date,default=date.today)
    status: Mapped[str]=mapped_column(String(50),default='referred')
    outcome: Mapped[str|None]=mapped_column(Text)

class YouthDocument(Base):
    __tablename__='youth_documents'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    youth_id: Mapped[int]=mapped_column(ForeignKey('youth.id',ondelete='CASCADE'),index=True)
    document_type: Mapped[str]=mapped_column(String(50))
    original_filename: Mapped[str]=mapped_column(String(255))
    stored_filename: Mapped[str]=mapped_column(String(255),unique=True)
    content_type: Mapped[str|None]=mapped_column(String(100))
    size_bytes: Mapped[int]=mapped_column(Integer)
    uploaded_by_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'))
    uploaded_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    youth=relationship('Youth',back_populates='documents')
