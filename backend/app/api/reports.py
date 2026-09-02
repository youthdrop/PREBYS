from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.entities import Intake

router = APIRouter()


@router.get('/summary')
def reports_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Intake)
    if start_date:
        q = q.filter(Intake.created_at >= start_date)
    if end_date:
        q = q.filter(Intake.created_at <= end_date)
    items = q.all()
    return {
        'intakes_count': len(items),
        'time_saved_total': round(sum(item.time_saved_hours or 0 for item in items), 2),
        'by_judge': sorted([
            {'judge': k, 'count': v} for k, v in _group_counts(items, 'judge')
        ], key=lambda x: x['count'], reverse=True),
        'by_prosecutor': sorted([
            {'prosecutor': k, 'count': v} for k, v in _group_counts(items, 'prosecutor')
        ], key=lambda x: x['count'], reverse=True),
        'court_dates': [
            {
                'name': item.name,
                'case_numbers': item.case_numbers,
                'next_court_date': item.next_court_date,
                'next_court_time': item.next_court_time,
                'court_site': item.court_site,
            }
            for item in items if item.next_court_date
        ],
    }


def _group_counts(items, relation_name: str):
    counts = {}
    for item in items:
        rel = getattr(item, relation_name)
        name = rel.name if rel else 'Unassigned'
        counts[name] = counts.get(name, 0) + 1
    return counts.items()
