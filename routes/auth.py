#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas                import AuthReg, AuthCreateAccount, AuthLogin
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
#from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, create_record
from models                 import User, Role

from auth                   import verify_password, hash_password, create_access_token

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

@auth_router.post('/reg')
async def reg(schema: AuthReg, session: AsyncSession = Depends(get_session)):
    #Проверяем существует ли такой email
    result = await session.execute(
        select(User).where(User.email == schema.email)
    )
    user = result.scalar_one_or_none()

    if user is not None:
        raise HTTPException(status_code=409, detail='Email already taken')
    
    
    #Получаем id стандартной роли
    result = await session.execute(
        select(Role).where(Role.role_name == 'user')
    )
    role = result.scalar_one_or_none()
    #Если роли нет - значит нужно заполнить БД
    if role is None:
        raise HTTPException(status_code=500, detail='Default role is not initiated')

    data = AuthCreateAccount(
        role_id=role.role_id,
        first_name=schema.first_name,
        last_name=schema.last_name,
        patronymic=schema.patronymic,
        email=schema.email,
        hashed_password=hash_password(schema.password)
    )

    await create_record(model=User, schema=data, session=session)
    return {'message': 'Account successfully created'}


@auth_router.post('/login')
async def login(schema: AuthLogin, session: AsyncSession = Depends(get_session)):
    #Проверяем существует ли такой email в БД
    result = await session.execute(
        select(User).where(User.email == schema.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail='Account with this email does not exist')
    
    #Проверяем верно ли введён пароль
    #hashed_password = hash_password(user.password)
    is_correct = verify_password(password_plain=schema.password, password_hashed=user.hashed_password)
    if not is_correct:
        raise HTTPException(status_code=401, detail='Wrong password, please try again')
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Account was deleted') 


    token = create_access_token({'sub': str(user.user_id)})
    return {'access_token': token, 'token_type': 'bearer'}