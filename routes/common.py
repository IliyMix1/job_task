#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas                import AuthReg, AuthLogin, ReadProfile, PatchProfile
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models                 import User
from dependencies           import get_current_user

from auth                   import verify_password, hash_password, create_access_token
from permissions            import can_read_own_profile, can_update_own_profile, can_delete_own_profile

common_router = APIRouter()

@common_router.get('/')
async def root():
    return {'message': "You've entered the main page"}


@common_router.get('/mock')
async def mock_view():
    return {'message': 'OK'}

@common_router.get('/my/profile', response_model=ReadProfile, tags=['My'])
async def get_profile(session: AsyncSession = Depends(get_session), user = Depends(can_read_own_profile)):
    result = await session.execute(
        select(User).where(User.user_id == user.user_id)
    )
    profile = result.scalar_one_or_none()
    return profile

@common_router.patch('/my/profile', response_model=ReadProfile, tags=['My'])
async def patch_profile(schema: PatchProfile, session: AsyncSession = Depends(get_session), user = Depends(can_update_own_profile)):
    return await patch_record(id=user.user_id, model=User, schema=schema, session=session)

@common_router.delete('/my/profile', tags=['My'])
async def delete_profile(session: AsyncSession = Depends(get_session), user = Depends(can_delete_own_profile)):
    user.is_active = False
    await session.commit()
    return {'message': 'Account was successfully deleted'}