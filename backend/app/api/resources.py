from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.deps import get_current_user, get_db, require_admin
from app.models.entities import Attorney, CaseNote, Intake, Judge, Prosecutor, Volunteer
from app.schemas.common import (
    AttorneyCreate, AttorneyRead, IntakeCreate, IntakeRead,
    JudgeCreate, JudgeRead, ProsecutorCreate, ProsecutorRead,
    VolunteerCreate, VolunteerRead, CaseNoteCreate, CaseNoteRead,
)

router = APIRouter()

COURTS = ['Central', 'Southbay', 'El Cajon', 'Vista', 'Juvenile Court']
HEARING_TYPES = [
    'Arraignment',
    'Bail Motion',
    'Other Motion',
    'Further Proceedings',
    'Preliminary Hearing',
    'Trial',
    'Jury Selection',
    'Resentencing Hearing',
    'SB 1437 Hearing',
]


@router.get('/dashboard')
def dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    week_end = today + timedelta(days=7)

    total_intakes = db.query(Intake).count()
    total_volunteers = db.query(Volunteer).count()
    total_case_notes = db.query(CaseNote).count()

    court_today = (
        db.query(Intake)
        .filter(Intake.next_court_date == today)
        .order_by(Intake.next_court_time.asc().nullslast(), Intake.name.asc())
        .all()
    )

    court_this_week = (
        db.query(Intake)
        .filter(
            Intake.next_court_date != None,
            Intake.next_court_date >= today,
            Intake.next_court_date <= week_end,
        )
        .count()
    )

    upcoming_hearings = (
        db.query(Intake)
        .filter(
            Intake.next_court_date != None,
            Intake.next_court_date >= today,
        )
        .order_by(Intake.next_court_date.asc(), Intake.next_court_time.asc().nullslast())
        .limit(10)
        .all()
    )

    recent_notes = (
        db.query(CaseNote)
        .order_by(CaseNote.created_at.desc())
        .limit(10)
        .all()
    )

    total_hours_saved = db.query(func.coalesce(func.sum(CaseNote.time_saved_hours), 0)).scalar()

    return {
        "total_intakes": total_intakes,
        "total_volunteers": total_volunteers,
        "total_case_notes": total_case_notes,
        "court_this_week": court_this_week,
        "total_hours_saved": float(total_hours_saved or 0),
        "court_today": [
            {
                "id": item.id,
                "name": item.name,
                "case_numbers": item.case_numbers,
                "next_court_date": item.next_court_date,
                "next_court_time": item.next_court_time,
                "court_site": item.court_site,
                "court_location": item.court_location,
                "hearing_type": item.hearing_type,
                "volunteer_assigned": item.volunteer_assigned,
            }
            for item in court_today
        ],
        "upcoming_hearings": [
            {
                "id": item.id,
                "name": item.name,
                "case_numbers": item.case_numbers,
                "next_court_date": item.next_court_date,
                "next_court_time": item.next_court_time,
                "court_site": item.court_site,
                "court_location": item.court_location,
                "hearing_type": item.hearing_type,
                "volunteer_assigned": item.volunteer_assigned,
            }
            for item in upcoming_hearings
        ],
        "recent_notes": [
            {
                "id": note.id,
                "intake_id": note.intake_id,
                "client_name": note.intake.name if note.intake else None,
                "note": note.note,
                "service_type": note.service_type,
                "note_date": note.note_date,
                "time_saved_hours": note.time_saved_hours,
                "created_by_name": note.created_by_name,
                "created_at": note.created_at,
            }
            for note in recent_notes
        ],
    }


def serialize_intake(item: Intake) -> IntakeRead:
    return IntakeRead(
        id=item.id,
        name=item.name,
        case_numbers=item.case_numbers,
        charges=item.charges,
        contact_person=item.contact_person,
        contact_person_telephone=item.contact_person_telephone,
        contact_person_email=item.contact_person_email,
        volunteer_assigned=item.volunteer_assigned,
        maximum_exposure=item.maximum_exposure,
        court_location=item.court_location,
        next_court_date=item.next_court_date,
        next_court_time=item.next_court_time,
        court_site=item.court_site,
        hearing_type=item.hearing_type,
        attorney_id=item.attorney_id,
        judge_id=item.judge_id,
        prosecutor_id=item.prosecutor_id,
        service_type=item.service_type,
        case_note=item.case_note,
        case_note_date=item.case_note_date,
        time_saved_hours=item.time_saved_hours,
        created_at=item.created_at,
        attorney_name=item.attorney.name if item.attorney else None,
        judge_name=item.judge.name if item.judge else None,
        prosecutor_name=item.prosecutor.name if item.prosecutor else None,
    )


def upsert_related(db: Session, payload: IntakeCreate):
    attorney_id = payload.attorney_id
    judge_id = payload.judge_id
    prosecutor_id = payload.prosecutor_id

    if payload.attorney:
        obj = Attorney(**payload.attorney.model_dump())
        db.add(obj)
        db.flush()
        attorney_id = obj.id

    if payload.judge:
        obj = Judge(**payload.judge.model_dump())
        db.add(obj)
        db.flush()
        judge_id = obj.id

    if payload.prosecutor:
        obj = Prosecutor(**payload.prosecutor.model_dump())
        db.add(obj)
        db.flush()
        prosecutor_id = obj.id

    return attorney_id, judge_id, prosecutor_id

@router.get('/calendar')
def court_calendar(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = (
        db.query(Intake)
        .filter(Intake.next_court_date != None)
        .order_by(
            Intake.next_court_date.asc(),
            Intake.next_court_time.asc().nullslast(),
            Intake.name.asc(),
        )
        .all()
    )

    return [
        {
            "id": item.id,
            "name": item.name,
            "case_numbers": item.case_numbers,
            "next_court_date": item.next_court_date,
            "next_court_time": item.next_court_time,
            "court_site": item.court_site,
            "court_location": item.court_location,
            "hearing_type": item.hearing_type,
            "volunteer_assigned": item.volunteer_assigned,
            "attorney_name": item.attorney.name if item.attorney else None,
            "judge_name": item.judge.name if item.judge else None,
            "prosecutor_name": item.prosecutor.name if item.prosecutor else None,
        }
        for item in items
    ]

@router.get('/lookups')
def lookups(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        'courts': COURTS,
        'hearing_types': HEARING_TYPES,
        'attorneys': [AttorneyRead.model_validate({**a.__dict__, 'case_count': len(a.cases)}) for a in db.query(Attorney).order_by(Attorney.name).all()],
        'judges': [JudgeRead.model_validate({**j.__dict__, 'case_count': len(j.cases)}) for j in db.query(Judge).order_by(Judge.name).all()],
        'prosecutors': [ProsecutorRead.model_validate({**p.__dict__, 'case_count': len(p.cases)}) for p in db.query(Prosecutor).order_by(Prosecutor.name).all()],
        'volunteers': [VolunteerRead.model_validate(v) for v in db.query(Volunteer).order_by(Volunteer.name).all()],
    }


@router.post('/intakes', response_model=IntakeRead)
def create_intake(payload: IntakeCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    attorney_id, judge_id, prosecutor_id = upsert_related(db, payload)

    obj = Intake(
        **payload.model_dump(
            exclude={
                'attorney',
                'judge',
                'prosecutor',
                'attorney_id',
                'judge_id',
                'prosecutor_id',
            }
        ),
        attorney_id=attorney_id,
        judge_id=judge_id,
        prosecutor_id=prosecutor_id,
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return serialize_intake(obj)


@router.get('/intakes', response_model=list[IntakeRead])
def list_intakes(search: str = Query(default=''), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Intake)
    if search:
        like = f'%{search}%'
        q = q.filter(or_(Intake.name.ilike(like), Intake.case_numbers.ilike(like), Intake.contact_person.ilike(like)))
    items = q.order_by(Intake.next_court_date.asc().nullslast(), Intake.name.asc()).all()
    return [serialize_intake(item) for item in items]


@router.get('/intakes/{intake_id}', response_model=IntakeRead)
def get_intake(intake_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    if not obj:
        raise HTTPException(404, 'Case not found')
    return serialize_intake(obj)


@router.put('/intakes/{intake_id}', response_model=IntakeRead)
def update_intake(intake_id: int, payload: IntakeCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    print("PAYLOAD hearing_type:", payload.hearing_type)
    print("PAYLOAD:", payload.model_dump())
    if not obj:
        raise HTTPException(404, 'Case not found')

    attorney_id, judge_id, prosecutor_id = upsert_related(db, payload)

    for key, value in payload.model_dump(
        exclude={
            'attorney',
            'judge',
            'prosecutor',
            'attorney_id',
            'judge_id',
            'prosecutor_id',
        }
    ).items():
        setattr(obj, key, value)

    obj.attorney_id = attorney_id
    obj.judge_id = judge_id
    obj.prosecutor_id = prosecutor_id

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return serialize_intake(obj)



def serialize_case_note(note: CaseNote) -> CaseNoteRead:
    return CaseNoteRead(
        id=note.id,
        intake_id=note.intake_id,
        note=note.note,
        service_type=note.service_type,
        note_date=note.note_date,
        time_saved_hours=note.time_saved_hours,
        created_by_email=note.created_by_email,
        created_by_name=note.created_by_name,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get('/intakes/{intake_id}/notes', response_model=list[CaseNoteRead])
def list_case_notes(intake_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    intake = db.get(Intake, intake_id)
    if not intake:
        raise HTTPException(404, 'Case not found')

    notes = (
        db.query(CaseNote)
        .filter(CaseNote.intake_id == intake_id)
        .order_by(CaseNote.created_at.desc())
        .all()
    )
    return [serialize_case_note(note) for note in notes]


@router.post('/intakes/{intake_id}/notes', response_model=CaseNoteRead)
def create_case_note(intake_id: int, payload: CaseNoteCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    intake = db.get(Intake, intake_id)
    if not intake:
        raise HTTPException(404, 'Case not found')

    note = CaseNote(
        intake_id=intake_id,
        note=payload.note,
        service_type=payload.service_type,
        note_date=payload.note_date,
        time_saved_hours=payload.time_saved_hours,
        created_by_email=current_user.email,
        created_by_name=current_user.full_name,
    )

    db.add(note)

    # Keep the older single-note fields in sync with the newest note so existing reports still work.
    intake.case_note = payload.note
    intake.case_note_date = payload.note_date
    intake.service_type = payload.service_type
    intake.time_saved_hours = payload.time_saved_hours
    db.add(intake)

    db.commit()
    db.refresh(note)
    return serialize_case_note(note)


@router.delete('/intakes/{intake_id}/notes/{note_id}')
def delete_case_note(intake_id: int, note_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    note = db.get(CaseNote, note_id)
    if not note or note.intake_id != intake_id:
        raise HTTPException(404, 'Case note not found')
    db.delete(note)
    db.commit()
    return {'message': 'Case note deleted'}


@router.delete('/intakes/{intake_id}')
def delete_intake(intake_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    if not obj:
        raise HTTPException(404, 'Case not found')
    db.delete(obj)
    db.commit()
    return {'message': 'Case deleted'}


def crud_routes(path: str, model, create_schema, read_schema):
    @router.post(path, response_model=read_schema)
    def create_item(payload: create_schema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        obj = model(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        data = obj.__dict__.copy()
        if hasattr(obj, 'cases'):
            data['case_count'] = len(obj.cases)
        return read_schema.model_validate(data)

    @router.get(path, response_model=list[read_schema])
    def list_items(search: str = Query(default=''), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        q = db.query(model)
        if search and hasattr(model, 'name'):
            q = q.filter(model.name.ilike(f'%{search}%'))
        items = q.order_by(model.name.asc()).all()
        results = []
        for item in items:
            data = item.__dict__.copy()
            if hasattr(item, 'cases'):
                data['case_count'] = len(item.cases)
            results.append(read_schema.model_validate(data))
        return results

    @router.get(f'{path}/{{item_id}}', response_model=read_schema)
    def get_item(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        data = item.__dict__.copy()
        if hasattr(item, 'cases'):
            data['case_count'] = len(item.cases)
        return read_schema.model_validate(data)

    @router.put(f'{path}/{{item_id}}', response_model=read_schema)
    def update_item(item_id: int, payload: create_schema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        db.add(item)
        db.commit()
        db.refresh(item)
        data = item.__dict__.copy()
        if hasattr(item, 'cases'):
            data['case_count'] = len(item.cases)
        return read_schema.model_validate(data)

    @router.delete(f'{path}/{{item_id}}')
    def delete_item(item_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        db.delete(item)
        db.commit()
        return {'message': 'Deleted'}

crud_routes('/attorneys', Attorney, AttorneyCreate, AttorneyRead)
crud_routes('/judges', Judge, JudgeCreate, JudgeRead)
crud_routes('/prosecutors', Prosecutor, ProsecutorCreate, ProsecutorRead)
crud_routes('/volunteers', Volunteer, VolunteerCreate, VolunteerRead)


@router.post('/public/family-intake')
def public_family_intake(payload: IntakeCreate, db: Session = Depends(get_db)):
    attorney_id, judge_id, prosecutor_id = upsert_related(db, payload)

    obj = Intake(
        **payload.model_dump(
            exclude={
                'attorney',
                'judge',
                'prosecutor',
                'attorney_id',
                'judge_id',
                'prosecutor_id',
            }
        ),
        attorney_id=attorney_id,
        judge_id=judge_id,
        prosecutor_id=prosecutor_id,
    )

    db.add(obj)
    db.commit()
    return {'message': 'Intake submitted successfully'}


@router.post('/public/volunteer-signup')
def public_volunteer_signup(payload: VolunteerCreate, db: Session = Depends(get_db)):
    obj = Volunteer(**payload.model_dump())
    db.add(obj)
    db.commit()
    return {'message': 'Volunteer signup submitted successfully'}