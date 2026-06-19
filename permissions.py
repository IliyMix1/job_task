from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy   import select
from dependencies import get_current_user
from fastapi      import Depends, HTTPException
from database     import get_session
from models       import User, Resource, Access_rule

class PermissionChecker():
    def __init__(self, resource_name: str, permission_name: str):
        self.resource_name = resource_name
        self.permission_name = permission_name

    async def __call__(self, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
        allowed_permissions = {
            'can_create',
            'can_read_own',
            'can_read_all',
            'can_update_own',
            'can_update_all',
            'can_delete_own',
            'can_delete_all',
        }

        if self.permission_name not in allowed_permissions:
            raise HTTPException(status_code=500, detail='Invalid permission name')
        
        #Соединяем таблицы по id ресурса и достаём запись, фильтруя по роли юзера и имени ресура
        #Теперь мы понимаем какие разрешения есть у конкретной роли на конкретном ресурсе 
        result = await session.execute(
            select(Access_rule).join(Resource, Access_rule.resource_id == Resource.resource_id)
            .where(Access_rule.role_id == user.role_id, self.resource_name == Resource.resource_name)
        )
        rule = result.scalar_one_or_none()

        #Записи нет в БД - кидаем ошибку
        if rule is None:
            raise HTTPException(status_code=403, detail='Forbidden')
        
        #Залезаем в SQLAlchemy объект и достаём оттуда атрибут, который равен permission_name(он либо True, либо False) 
        has_permission = getattr(rule, self.permission_name)

        if not has_permission:
            raise HTTPException(status_code=403, detail='Forbidden')
        
        return user