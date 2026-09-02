from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.deps import get_current_user, get_db, require_admin
from app.models.user import User
from app.models.youth import Youth, YouthCaseNote, Service, YouthService, Activity, ActivityParticipant, Referral, YouthDocument

router=APIRouter()
UPLOAD_DIR=Path(__file__).resolve().parents[2]/'uploads'/'youth_documents'
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
ALLOWED={'application/pdf','image/jpeg','image/png','image/webp','application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
MAX_SIZE=10*1024*1024

def age_from_birthdate(value):
    if not value: return None
    today=date.today(); return today.year-value.year-((today.month,today.day)<(value.month,value.day))

def can_access(user:User,y:Youth):
    return user.role in ('admin','supervisor','manager') or y.assigned_staff_id==user.id

def serialize(y, db: Session | None = None):
    staff_name = None
    if db and y.assigned_staff_id:
        staff = db.get(User, y.assigned_staff_id)
        staff_name = (staff.full_name or staff.email) if staff else None
    return {'id':y.id,'name':y.name,'telephone':y.telephone,'email':y.email,'gender':y.gender,'race':y.race,'birthdate':y.birthdate,'age':age_from_birthdate(y.birthdate),'enrollment_date':y.enrollment_date,'status':y.status,'assigned_staff_id':y.assigned_staff_id,'assigned_staff_name':staff_name,'next_contact_date':y.next_contact_date,'emergency_contact_name':y.emergency_contact_name,'emergency_contact_phone':y.emergency_contact_phone,'aces_pre_score':y.aces_pre_score,'aces_post_score':y.aces_post_score,'created_at':y.created_at}


@router.get('/dashboard')
def dashboard(current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    today = date.today()
    week_end = today + timedelta(days=7)

    youth_query = db.query(Youth)
    note_query = db.query(YouthCaseNote).join(Youth, Youth.id == YouthCaseNote.youth_id)
    if current_user.role not in ('admin', 'supervisor', 'manager'):
        youth_query = youth_query.filter(Youth.assigned_staff_id == current_user.id)
        note_query = note_query.filter(Youth.assigned_staff_id == current_user.id)

    active_youth = youth_query.filter(Youth.status == 'active').count()
    contacts_due_today = youth_query.filter(Youth.next_contact_date == today).count()
    overdue_contacts = youth_query.filter(Youth.next_contact_date < today, Youth.status == 'active').count()
    total_case_notes = note_query.count()

    activities_this_week = db.query(Activity).filter(
        Activity.activity_date >= today, Activity.activity_date <= week_end
    ).count()
    today_rows = db.query(Activity).filter(Activity.activity_date == today).order_by(Activity.start_time).all()
    upcoming_rows = db.query(Activity).filter(Activity.activity_date > today).order_by(Activity.activity_date, Activity.start_time).limit(8).all()
    recent_rows = note_query.order_by(YouthCaseNote.created_at.desc()).limit(8).all()

    def activity_dict(a):
        return {'id': a.id, 'title': a.title, 'activity_date': a.activity_date, 'start_time': a.start_time, 'end_time': a.end_time, 'location': a.location}

    return {
        'active_youth': active_youth,
        'contacts_due_today': contacts_due_today,
        'overdue_contacts': overdue_contacts,
        'activities_this_week': activities_this_week,
        'total_case_notes': total_case_notes,
        'activities_today': [activity_dict(a) for a in today_rows],
        'upcoming_activities': [activity_dict(a) for a in upcoming_rows],
        'recent_notes': [
            {
                'id': n.id, 'youth_id': n.youth_id, 'youth_name': n.youth.name,
                'note_type': n.note_type, 'note': n.note,
                'created_by_name': n.created_by_name, 'created_at': n.created_at,
            } for n in recent_rows
        ],
    }

@router.get('/youth')
def list_youth(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    q=db.query(Youth)
    if current_user.role not in ('admin','supervisor','manager'): q=q.filter(Youth.assigned_staff_id==current_user.id)
    return [serialize(x, db) for x in q.order_by(Youth.name).all()]

@router.post('/youth')
def create_youth(payload:dict,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    allowed={'name','telephone','email','gender','race','birthdate','enrollment_date','status','assigned_staff_id','next_contact_date','emergency_contact_name','emergency_contact_phone','aces_pre_score','aces_post_score'}
    data={k:v for k,v in payload.items() if k in allowed}
    for k in ('birthdate','enrollment_date','next_contact_date'):
        if data.get(k): data[k]=date.fromisoformat(data[k])
    if current_user.role not in ('admin','supervisor','manager'): data['assigned_staff_id']=current_user.id
    y=Youth(**data); db.add(y); db.commit(); db.refresh(y); return serialize(y, db)

@router.get('/youth/{youth_id}')
def get_youth(youth_id:int,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    return serialize(y, db)

@router.put('/youth/{youth_id}')
def update_youth(youth_id:int,payload:dict,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    allowed={'name','telephone','email','gender','race','birthdate','enrollment_date','status','assigned_staff_id','next_contact_date','emergency_contact_name','emergency_contact_phone','aces_pre_score','aces_post_score'}
    if current_user.role not in ('admin','supervisor','manager'): allowed.discard('assigned_staff_id')
    for k,v in payload.items():
        if k in allowed:
            if k in ('birthdate','enrollment_date','next_contact_date') and v: v=date.fromisoformat(v)
            setattr(y,k,v or None)
    db.commit(); db.refresh(y); return serialize(y, db)

@router.get('/youth/{youth_id}/notes')
def notes(youth_id:int,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    return [{'id':n.id,'note_type':n.note_type,'contact_method':n.contact_method,'note':n.note,'next_action':n.next_action,'next_contact_date':n.next_contact_date,'confidential':n.confidential,'created_by_name':n.created_by_name,'created_at':n.created_at} for n in y.notes]

@router.post('/youth/{youth_id}/notes')
def add_note(youth_id:int,payload:dict,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    n=YouthCaseNote(youth_id=y.id,note_type=payload.get('note_type'),contact_method=payload.get('contact_method'),note=payload['note'],next_action=payload.get('next_action'),next_contact_date=date.fromisoformat(payload['next_contact_date']) if payload.get('next_contact_date') else None,confidential=bool(payload.get('confidential')),created_by_id=current_user.id,created_by_name=current_user.full_name or current_user.email)
    if n.next_contact_date: y.next_contact_date=n.next_contact_date
    db.add(n); db.commit(); return {'id':n.id}

@router.get('/services')
def services(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    return [{'id':s.id,'name':s.name,'category':s.category,'description':s.description,'active':s.active} for s in db.query(Service).order_by(Service.name).all()]

@router.post('/services')
def add_service(payload:dict,current_user=Depends(require_admin),db:Session=Depends(get_db)):
    s=Service(name=payload['name'],category=payload.get('category'),description=payload.get('description'),active=payload.get('active',True)); db.add(s); db.commit(); db.refresh(s); return {'id':s.id}

@router.post('/youth/{youth_id}/services')
def provide_service(youth_id:int,payload:dict,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    row=YouthService(youth_id=youth_id,service_id=int(payload['service_id']),service_date=date.fromisoformat(payload['service_date']) if payload.get('service_date') else date.today(),status=payload.get('status','provided'),notes=payload.get('notes')); db.add(row); db.commit(); return {'id':row.id}

@router.get('/activities')
def activities(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(Activity).order_by(Activity.activity_date).all(); return [{'id':a.id,'title':a.title,'activity_date':a.activity_date,'start_time':a.start_time,'end_time':a.end_time,'location':a.location,'description':a.description,'staff_id':a.staff_id} for a in rows]

@router.post('/activities')
def add_activity(payload:dict,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    a=Activity(title=payload['title'],activity_date=date.fromisoformat(payload['activity_date']),start_time=payload.get('start_time'),end_time=payload.get('end_time'),location=payload.get('location'),description=payload.get('description'),staff_id=payload.get('staff_id') or current_user.id); db.add(a); db.commit(); db.refresh(a)
    for youth_id in payload.get('youth_ids',[]): db.add(ActivityParticipant(activity_id=a.id,youth_id=int(youth_id)))
    db.commit(); return {'id':a.id}

@router.get('/staff')
def staff(current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    return [{'id':u.id,'full_name':u.full_name,'email':u.email,'role':u.role} for u in db.query(User).filter(User.is_active==True).order_by(User.full_name).all()]

@router.get('/youth/{youth_id}/documents')
def documents(youth_id:int,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    return [{'id':d.id,'document_type':d.document_type,'original_filename':d.original_filename,'content_type':d.content_type,'size_bytes':d.size_bytes,'uploaded_at':d.uploaded_at} for d in y.documents]

@router.post('/youth/{youth_id}/documents')
async def upload_document(youth_id:int,document_type:str=Form(...),file:UploadFile=File(...),current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    y=db.get(Youth,youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Youth not found')
    if document_type not in ('employment_verification','school_verification'): raise HTTPException(400,'Invalid document type')
    if file.content_type not in ALLOWED: raise HTTPException(400,'Only PDF, JPG, PNG, WEBP, or DOCX files are allowed')
    content=await file.read(MAX_SIZE+1)
    if len(content)>MAX_SIZE: raise HTTPException(400,'File must be 10 MB or smaller')
    ext=Path(file.filename or '').suffix.lower(); stored=f'{uuid4().hex}{ext}'; (UPLOAD_DIR/stored).write_bytes(content)
    d=YouthDocument(youth_id=youth_id,document_type=document_type,original_filename=Path(file.filename or 'document').name,stored_filename=stored,content_type=file.content_type,size_bytes=len(content),uploaded_by_id=current_user.id)
    db.add(d); db.commit(); db.refresh(d); return {'id':d.id}

@router.get('/documents/{document_id}/download')
def download_document(document_id:int,current_user=Depends(get_current_user),db:Session=Depends(get_db)):
    d=db.get(YouthDocument,document_id)
    if not d: raise HTTPException(404,'Document not found')
    y=db.get(Youth,d.youth_id)
    if not y or not can_access(current_user,y): raise HTTPException(404,'Document not found')
    path=UPLOAD_DIR/d.stored_filename
    if not path.exists(): raise HTTPException(404,'Stored file not found')
    return FileResponse(path,media_type=d.content_type,filename=d.original_filename)
