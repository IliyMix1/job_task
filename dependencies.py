from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, TokenBlacklist
from database import get_session
from auth import security, SECRET_KEY, ALGORITHM, JWTError, jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_session)):
    '''Проверяет залогинен ли пользователь'''
    #Достаём токен из заголовка
    token = credentials.credentials

    try:
        #Расшифровываем jwt-токен и достаёт оттуда id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        jti     = payload.get('jti')
        if user_id is None or jti is None:
            raise HTTPException(status_code=401, detail='Authentication required')
        
        #Из токена id достаётся как строка, во избежание конфликтов переводим в int
        user_id = int(user_id)

    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

    result = await session.execute(
        select(TokenBlacklist).where(TokenBlacklist.jti == jti)
    )
    jwt_id = result.scalar_one_or_none()
    if jwt_id is not None:
        raise HTTPException(status_code=401, detail='Authentication required')

    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    #Проверяем есть ли такой пюезр в БД
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    #Проверяем статус юзера
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account was deleted') 

    return user
    #return await select_record(id=int(user_id), model=User, session=session)