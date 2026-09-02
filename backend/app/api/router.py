from fastapi import APIRouter
from app.api import auth, resources, reports, users, youth

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(resources.router, prefix='/resources', tags=['resources'])
api_router.include_router(reports.router, prefix='/reports', tags=['reports'])
api_router.include_router(users.router, prefix='/users', tags=['users'])

api_router.include_router(youth.router, prefix='/mis', tags=['youth-mis'])
