import math
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from data.core_data import db_path
from data.database_config import DatabaseManager
from utils.ui_utility import build_menu
from utils.authorization import private, check_user_is_admins

async def ban_user(context, user_id, name, username, admin_id, admin_name, admin_username):
    context.bot_data['list_banned_users'].update({str(user_id): [name, user_id, username]})
    context.bot_data['list_banned_by_admins'].update({str(user_id): [admin_id, admin_name, admin_username, user_id]})

    await DatabaseManager(db_path).insert_data(
            table_name  = 'banned_users', 
            primary_key = 'user_id',
            user_id     = user_id,
            name        = name,
            username    = username
            )

    await DatabaseManager(db_path).insert_data(
            table_name      = 'banned_by_admins',
            primary_key     = 'banned_user_id',
            admin_id        = admin_id,
            admin_name      = admin_name,
            admin_username  = admin_username,
            banned_user_id  = user_id
            )

async def unban_user(context, banned_user_id):
    admin_id = context.bot_data['list_banned_by_admins'][str(banned_user_id)][0]
    
    del context.bot_data['list_banned_users'][str(banned_user_id)]
    del context.bot_data['list_banned_by_admins'][str(banned_user_id)]

    await DatabaseManager(db_path).delete_data(
            table_name  = 'banned_users',
            primary_key = 'user_id',
            value_key   = banned_user_id
            )

    await DatabaseManager(db_path).delete_data(
            table_name  = 'banned_by_admins',
            primary_key = 'banned_user_id',
            value_key   = banned_user_id
            )

def update_ban_list_order(n_rows: int, len_ban_list: int):
    return math.ceil(len_ban_list / n_rows)
