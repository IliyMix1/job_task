#Для эндпоинтов
from fastapi                import APIRouter, Depends, HTTPException
from schemas                import AuthReg, AuthLogin, ReadProfile, PatchProfile, AdminPatchUser, AdminReadUser, AdminReadAccessRule, AdminCreateAccessRule, AdminPatchAccessRule, ProductCreate, ProductRead, ProductPatch
#Для интеграции с PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm         import joinedload
from sqlalchemy             import select
from database               import get_session, create_record, patch_record
from models                 import User, Access_rule, Product
from dependencies           import get_current_user

from auth                   import verify_password, hash_password, create_access_token
from permissions            import can_read_own_profile, can_update_own_profile, can_delete_own_profile, can_read_all_products, can_create_products, can_update_all_products, can_delete_all_products, can_read_all_users, can_update_all_users, can_delete_all_users, can_read_access_rules, can_create_access_rules, can_update_access_rules, can_delete_access_rules

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


@common_router.get('/admin/users', response_model=list[AdminReadUser], tags=['Admin'])
async def get_all_users(admin = Depends(can_read_all_users), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User)
    )
    users = result.scalars().all()
    return users

@common_router.patch('/admin/users/{user_id}', response_model=AdminReadUser, tags=['Admin'])
async def patch_user(user_id: int, schema: AdminPatchUser, admin = Depends(can_update_all_users), session: AsyncSession = Depends(get_session)):
    return await patch_record(id=user_id, model=User, schema=schema, session=session)

@common_router.delete('/admin/users/{user_id}', tags=['Admin'])
async def delete_user(user_id: int, admin = Depends(can_delete_all_users), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    user.is_active = False
    await session.commit()
    return {'message': f'User {user_id} was deleted'}

@common_router.get('/admin/access_rules', response_model=list[AdminReadAccessRule], tags=['Admin'])
async def get_access_rules(admin = Depends(can_read_access_rules), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Access_rule)
    )
    return result.scalars().all()

@common_router.post('/admin/access_rules', response_model=AdminReadAccessRule, tags=['Admin'])
async def create_access_rule(schema: AdminCreateAccessRule, admin = Depends(can_create_access_rules), session: AsyncSession = Depends(get_session)):
    return await create_record(model=Access_rule, schema=schema, session=session)

@common_router.patch('/admin/access_rules/{role_id}/{resource_id}', response_model=AdminReadAccessRule, tags=['Admin'])
async def patch_access_rule(role_id: int, resource_id: int, schema: AdminPatchAccessRule, admin = Depends(can_update_access_rules), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Access_rule).where(Access_rule.role_id == role_id, Access_rule.resource_id == resource_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail='Access rule not found')
    
    #Находим те столбцы, которые были в запросе и изменяем их(пустые - пропускаем)    
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    await session.commit()
    await session.refresh(record)
    return record

@common_router.delete('/admin/access_rules/{role_id}/{resource_id}', tags=['Admin'])
async def delete_access_rule(role_id: int, resource_id: int, admin = Depends(can_delete_access_rules), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Access_rule).where(Access_rule.role_id == role_id, Access_rule.resource_id == resource_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail='Access rule not found')
    
    await session.delete(record)
    await session.commit()
    return {'message': 'Access-rule was successfully deleted'}


@common_router.get('/products', response_model=list[ProductRead], tags=['Products'])
async def get_all_products(user = Depends(can_read_all_products), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product)
    )
    return result.scalars().all()

@common_router.post('/products', response_model=ProductRead, tags=['Products'])
async def create_product(schema: ProductCreate, user = Depends(can_create_products), session: AsyncSession = Depends(get_session)):
    return await create_record(model=Product, schema=schema, session=session) 

@common_router.patch('/products/{product_id}', response_model=ProductRead, tags=['Products'])
async def patch_product(product_id: int, schema: ProductPatch, user = Depends(can_update_all_products), session: AsyncSession = Depends(get_session)):
    return await patch_record(id=product_id, model=Product, schema=schema, session=session)

@common_router.delete('/products/{product_id}', tags=['Products'])
async def delete_product(product_id: int, user = Depends(can_delete_all_products), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    
    await session.delete(product)
    await session.commit()
    return {'message': 'Product was successfully deleted'}