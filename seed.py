import asyncio

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from database import async_session
from models   import Role, Resource, Access_rule

#Перечисляем информацию, которую добавим в БД
#Используем список словарей, чтобы НАГЛЯДНО указать SQLAlchemy какие конкретно поля заполнять
ROLES = (
    {'role_name': 'user'}, 
    {'role_name': 'admin'}, 
    {'role_name': 'manager'}
    )

RESOURCES = (
    {'resource_name': 'users'}, 
    {'resource_name': 'profile'}, 
    {'resource_name': 'products'}
    )

ACCESS_RULES = (
    #ВСЕ ПОЛЬЗОВАТЕЛИ
    {
        'role':     'admin',
        'resource': 'users',
        'can_create':     True,
        'can_read_own':   True,
        'can_read_all':   True,
        'can_update_own': True,
        'can_update_all': True,
        'can_delete_own': True,
        'can_delete_all': True
    },
    #ПРОФИЛЬ
    {
        'role':     'user',
        'resource': 'profile',
        'can_create':     False,
        'can_read_own':   True,
        'can_read_all':   False,
        'can_update_own': True,
        'can_update_all': False,
        'can_delete_own': True,
        'can_delete_all': False
    },
    {
        'role':     'admin',
        'resource': 'profile',
        'can_create':     True,
        'can_read_own':   True,
        'can_read_all':   True,
        'can_update_own': True,
        'can_update_all': True,
        'can_delete_own': True,
        'can_delete_all': True
    },
    #ПРОДУКТЫ
    {
        'role':     'admin',
        'resource': 'products',
        'can_create':     True,
        'can_read_own':   True,
        'can_read_all':   True,
        'can_update_own': True,
        'can_update_all': True,
        'can_delete_own': True,
        'can_delete_all': True
    },
    {
        'role':     'user',
        'resource': 'products',
        'can_create':     False,
        'can_read_own':   True,
        'can_read_all':   True,
        'can_update_own': False,
        'can_update_all': False,
        'can_delete_own': False,
        'can_delete_all': False
    },
)


async def seed_data():
    '''Функция для автозаполнения таблиц стандартными данными'''
    #Начинаем асинхронную сессию(в эндпоинтах это делается автоматически через Depends(get_session))
    async with async_session() as session:
        #Заполняем таблицу с ролями
        await session.execute(
            insert(Role).values(ROLES).on_conflict_do_nothing(index_elements=['role_name'])
        )
        #Заполняем таблицу с ресурсами
        await session.execute(
            insert(Resource).values(RESOURCES).on_conflict_do_nothing(index_elements=['resource_name'])
        )

        #Получаем список всех ролей
        result = await session.execute(select(Role))
        all_roles = result.scalars().all()
        #Получаем список всех ресурсов
        result = await session.execute(select(Resource))
        all_resources = result.scalars().all()
        
        #Получаем словарь вида: {роль: id}
        role_data = {}
        for role in all_roles:
            role_data[role.role_name] = role.role_id
        #Получаем словарь вида: {ресурс: id}
        resource_data = {}
        for resource in all_resources:
            resource_data[resource.resource_name] = resource.resource_id
        

        #Пробегаюсь по списку правил и пересобираю словарь для отправки в БД(вместо role -> role_id, вместо resource -> resource_id)
        access_rules_for_insert = []
        for rule in ACCESS_RULES:
            access_rules_for_insert.append({
                'role_id':     role_data[rule['role']],         #Достаю из словаря с ролями id по ключу
                'resource_id': resource_data[rule['resource']], #Достаю из словаря с ресурсами id по ключу
                'can_create':     rule['can_create'],
                'can_read_own':   rule['can_read_own'],
                'can_read_all':   rule['can_read_all'],
                'can_update_own': rule['can_update_own'],
                'can_update_all': rule['can_update_all'],
                'can_delete_own': rule['can_delete_own'],
                'can_delete_all': rule['can_delete_all']
                })

        #Сразу создаём объект, чтобы обращаться к нему
        access_insert = insert(Access_rule)
        await session.execute(
            access_insert.values(access_rules_for_insert).on_conflict_do_update(index_elements=['role_id', 'resource_id'], 
                set_={     #Если вдруг роль-ресурс уже существует - изменям права доступа(сделано, чтобы удобно менять их прям из конфига)
                'can_create':     access_insert.excluded.can_create,
                'can_read_own':   access_insert.excluded.can_read_own,
                'can_read_all':   access_insert.excluded.can_read_all,
                'can_update_own': access_insert.excluded.can_update_own,
                'can_update_all': access_insert.excluded.can_update_all,
                'can_delete_own': access_insert.excluded.can_delete_own,
                'can_delete_all': access_insert.excluded.can_delete_all
            })
        )

        #Добавляем изменения в БД
        await session.commit()

if __name__ == '__main__':
    asyncio.run(seed_data())