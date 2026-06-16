#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
#rom schemas.schemas        import AuthReg, AuthLogin, AuthUserCreate, AuthStudentCreate
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, select_record, create_record
#from models.models          import User, Student

from auth                   import verify_password, hash_password, create_access_token

auth_router = APIRouter('/auth', tags=['Auth'])

@auth_router.post('/reg')
async def reg():
    pass