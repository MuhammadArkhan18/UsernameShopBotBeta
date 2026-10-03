from telegram.ext import Application
from data.core_data import db_path
from data.database_config import DatabaseManager

async def initiate_temp_data(application: Application):
    if "list_users" not in application.bot_data:
        application.bot_data['list_users']  = {}

    if 'list_threads' not in application.bot_data:
        application.bot_data['list_threads']= {}

    if 'list_banned_users' not in application.bot_data:
        application.bot_data['list_banned_users'] = {}

    if 'list_banned_by_admins' not in application.bot_data:
        application.bot_data['list_banned_by_admins'] = {}

    if 'admin_in_broadcast' not in application.bot_data:
        application.bot_data['admin_in_broadcast'] = list()

    data_user_threads = await DatabaseManager(db_path).read_data_all('user_order_threads', 'user_id', 'name', 'username', 'thread_id')

    data_banned_users = await DatabaseManager(db_path).read_data_all('banned_users', 'user_id', 'name', 'username')

    data_banned_by_admins = await DatabaseManager(db_path).read_data_all('banned_by_admins', 'admin_id', 'admin_name', 'admin_username', 'banned_user_id')

    if len(data_user_threads) >= 1:
        for user_data in data_user_threads:
            user_id     = user_data[0]
            name        = user_data[1]
            username    = user_data[2]
            thread_id   = user_data[3]

            application.bot_data['list_users'].update({str(user_id): [name, user_id, username, thread_id]})
            application.bot_data['list_threads'].update({str(thread_id): user_id})

    if len(data_banned_users) >= 1:
        for banned_user_data in data_banned_users:
            banned_user_id      = banned_user_data[0]
            banned_user_name    = banned_user_data[1]
            banned_user_username= banned_user_data[2]

            application.bot_data['list_banned_users'].update({str(banned_user_id): [banned_user_name, banned_user_id, banned_user_username]})

    if len(data_banned_by_admins) >= 1:
        for banned_by_admin_data in data_banned_by_admins:
            admin_id        = banned_by_admin_data[0]
            admin_name      = banned_by_admin_data[1]
            admin_username  = banned_by_admin_data[2]
            banned_user_id  = banned_by_admin_data[3]

            application.bot_data['list_banned_by_admins'].update({str(banned_user_id): [admin_id, admin_name, admin_username, banned_user_id]})

async def input_user(context, first_name, chat_id, username, thread_id):
    context.bot_data['list_users'].update({str(chat_id): [first_name, chat_id, username, thread_id]})
    context.bot_data['list_threads'].update({str(thread_id): chat_id})
    
    await DatabaseManager(db_path).insert_data(
            table_name  = 'user_order_threads',
            primary_key = 'user_id',
            user_id     = chat_id, 
            name        = first_name, 
            username    = username, 
            thread_id   = thread_id
            )

async def del_user(context, chat_id):
    del context.bot_data['list_threads'][str(context.bot_data['list_users'][str(chat_id)][3])]
    del context.bot_data['list_users'][str(chat_id)]
    
    await DatabaseManager(db_path).delete_data(
            table_name  = 'user_order_threads',
            primary_key = 'user_id',
            value_key   = chat_id
            )
