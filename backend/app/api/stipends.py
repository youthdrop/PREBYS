from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.stipend import YouthStipend
from app.models.user import User
from app.models.youth import Youth


router = APIRouter()


CURRICULUM_SESSIONS = [
    {
        "value": "Week 1 — Welcome to the Institute",
        "week": "1",
        "title": "Welcome to the Institute",
    },
    {
        "value": "Week 2 — Creating Our Culture",
        "week": "2",
        "title": "Creating Our Culture",
    },
    {
        "value": "Week 3 — Who Am I?",
        "week": "3",
        "title": "Who Am I?",
    },
    {
        "value": "Week 4 — Story of Self",
        "week": "4",
        "title": "Story of Self",
    },
    {
        "value": "Week 5 — Leadership and Peacebuilding",
        "week": "5",
        "title": "Leadership and Peacebuilding",
    },
    {
        "value": "Week 6 — Community Mapping and Peacebuilding",
        "week": "6",
        "title": "Community Mapping and Peacebuilding",
    },
    {
        "value": (
            "Week 7 — Research and Civic Engagement "
            "and Peacebuilding"
        ),
        "week": "7",
        "title": (
            "Research and Civic Engagement "
            "and Peacebuilding"
        ),
    },
    {
        "value": "Weeks 8-10 — Community Surveys for Campaign",
        "week": "8-10",
        "title": "Community Surveys for Campaign",
    },
    {
        "value": "Weeks 11-14 — Community Research",
        "week": "11-14",
        "title": "Community Research",
    },
    {
        "value": "Weeks 15,16 — Data Group",
        "week": "15,16",
        "title": "Data Group",
    },
    {
        "value": "Weeks 15,16 — Narrative Storytelling Group",
        "week": "15,16",
        "title": "Narrative Storytelling Group",
    },
    {
        "value": "Weeks 15,16 — Marketing Group",
        "week": "15,16",
        "title": "Marketing Group",
    },
    {
        "value": "Weeks 17-18 — Presentations",
        "week": "17-18",
        "title": "Presentations",
    },
    {
        "value": "Weeks 19-28 — Campaign and Peacebuilding",
        "week": "19-28",
        "title": "Campaign and Peacebuilding",
    },
    {
        "value": "Weeks 19-28 — Mobile App Campaign",
        "week": "19-28",
        "title": "Mobile App Campaign",
    },
    {
        "value": (
            "Week 28.32 — Celebration, Reflection "
            "and Sustainability"
        ),
        "week": "28.32",
        "title": "Celebration, Reflection and Sustainability",
    },
]


def can_access(
    user: User,
    youth: Youth,
) -> bool:
    return (
        user.role in ("admin", "supervisor", "manager")
        or youth.assigned_staff_id == user.id
    )


def stipend_to_dict(
    stipend: YouthStipend,
) -> dict:
    return {
        "id": stipend.id,
        "youth_id": stipend.youth_id,
        "session_date": stipend.session_date,
        "curriculum_session": stipend.curriculum_session,
        "attendance_status": stipend.attendance_status,
        "amount": stipend.amount,
        "payment_status": stipend.payment_status,
        "payment_date": stipend.payment_date,
        "notes": stipend.notes,
        "created_by_id": stipend.created_by_id,
        "created_by_name": stipend.created_by_name,
        "created_at": stipend.created_at,
    }


@router.get("/curriculum")
def get_curriculum(
    current_user=Depends(get_current_user),
):
    return CURRICULUM_SESSIONS


@router.get("/youth/{youth_id}/stipends")
def list_stipends(
    youth_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    youth = db.get(Youth, youth_id)

    if not youth or not can_access(current_user, youth):
        raise HTTPException(
            status_code=404,
            detail="Youth not found",
        )

    stipends = (
        db.query(YouthStipend)
        .filter(YouthStipend.youth_id == youth_id)
        .order_by(
            YouthStipend.session_date.desc(),
            YouthStipend.id.desc(),
        )
        .all()
    )

    total = (
        db.query(func.coalesce(func.sum(YouthStipend.amount), 0))
        .filter(YouthStipend.youth_id == youth_id)
        .scalar()
    )

    paid_total = (
        db.query(func.coalesce(func.sum(YouthStipend.amount), 0))
        .filter(
            YouthStipend.youth_id == youth_id,
            YouthStipend.payment_status == "paid",
        )
        .scalar()
    )

    pending_total = (
        db.query(func.coalesce(func.sum(YouthStipend.amount), 0))
        .filter(
            YouthStipend.youth_id == youth_id,
            YouthStipend.payment_status != "paid",
        )
        .scalar()
    )

    return {
        "records": [
            stipend_to_dict(stipend)
            for stipend in stipends
        ],
        "total": float(total or 0),
        "paid_total": float(paid_total or 0),
        "pending_total": float(pending_total or 0),
    }


@router.post("/youth/{youth_id}/stipends")
def create_stipend(
    youth_id: int,
    payload: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    youth = db.get(Youth, youth_id)

    if not youth or not can_access(current_user, youth):
        raise HTTPException(
            status_code=404,
            detail="Youth not found",
        )

    curriculum_session = payload.get(
        "curriculum_session",
        "",
    ).strip()

    if not curriculum_session:
        raise HTTPException(
            status_code=400,
            detail="Curriculum session is required",
        )

    if not payload.get("session_date"):
        raise HTTPException(
            status_code=400,
            detail="Session date is required",
        )

    amount = float(payload.get("amount", 50.00))

    if amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Stipend amount cannot be negative",
        )

    payment_date = None

    if payload.get("payment_date"):
        payment_date = date.fromisoformat(
            payload["payment_date"]
        )

    stipend = YouthStipend(
        youth_id=youth_id,
        session_date=date.fromisoformat(
            payload["session_date"]
        ),
        curriculum_session=curriculum_session,
        attendance_status=payload.get(
            "attendance_status",
            "completed",
        ),
        amount=amount,
        payment_status=payload.get(
            "payment_status",
            "pending",
        ),
        payment_date=payment_date,
        notes=payload.get("notes"),
        created_by_id=current_user.id,
        created_by_name=(
            current_user.full_name
            or current_user.email
        ),
    )

    db.add(stipend)
    db.commit()
    db.refresh(stipend)

    return stipend_to_dict(stipend)


@router.put("/stipends/{stipend_id}")
def update_stipend(
    stipend_id: int,
    payload: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stipend = db.get(
        YouthStipend,
        stipend_id,
    )

    if not stipend:
        raise HTTPException(
            status_code=404,
            detail="Stipend not found",
        )

    youth = db.get(
        Youth,
        stipend.youth_id,
    )

    if not youth or not can_access(current_user, youth):
        raise HTTPException(
            status_code=404,
            detail="Stipend not found",
        )

    if "session_date" in payload:
        stipend.session_date = date.fromisoformat(
            payload["session_date"]
        )

    if "curriculum_session" in payload:
        stipend.curriculum_session = payload[
            "curriculum_session"
        ]

    if "attendance_status" in payload:
        stipend.attendance_status = payload[
            "attendance_status"
        ]

    if "amount" in payload:
        stipend.amount = float(payload["amount"])

    if "payment_status" in payload:
        stipend.payment_status = payload[
            "payment_status"
        ]

    if "payment_date" in payload:
        stipend.payment_date = (
            date.fromisoformat(payload["payment_date"])
            if payload["payment_date"]
            else None
        )

    if "notes" in payload:
        stipend.notes = payload["notes"]

    db.commit()
    db.refresh(stipend)

    return stipend_to_dict(stipend)


@router.delete("/stipends/{stipend_id}")
def delete_stipend(
    stipend_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stipend = db.get(
        YouthStipend,
        stipend_id,
    )

    if not stipend:
        raise HTTPException(
            status_code=404,
            detail="Stipend not found",
        )

    youth = db.get(
        Youth,
        stipend.youth_id,
    )

    if not youth or not can_access(current_user, youth):
        raise HTTPException(
            status_code=404,
            detail="Stipend not found",
        )

    db.delete(stipend)
    db.commit()

    return {
        "message": "Stipend deleted",
    }