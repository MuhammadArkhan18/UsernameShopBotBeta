import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ConversationHandler
from functools import wraps
from data.core_data import id_maingroup, bot_id
from utils.ui_utility import build_menu

logger = logging.getLogger(__name__)

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id     = update.effective_chat.id
        list_users  = context.bot_data['list_users']
        if str(user_id) not in list_users:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def owneronly(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        message = update.callback_query.message if update.callback_query else update.message
        if update.effective_user.id == bot_id:
            return
        if not message.is_topic_message:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def private(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        chat_type = update.effective_chat.type

        if chat_type != "private":
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def maingroup_only(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        if update.effective_chat.id != id_maingroup:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def check_user_in_conversation(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        list_users = context.bot_data['list_users']
        if str(update.effective_chat.id) in list_users:
            await context.bot.send_message(
                    chat_id     = update.effective_chat.id,
                    text        = "<i>Selesaikan percakapan dengan Owner terlebih dahulu yaa</i>",
                    parse_mode  = ParseMode.HTML
                    )
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def check_user_is_admins(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        is_user_admin = await check_user_is_owners(update, context)

        if not is_user_admin:
            return

        return await func(update, context, *args, **kwargs)
    return wrapped

async def check_user_is_owners(update, context):
    try:
        member = await context.bot.get_chat_member(
                chat_id = id_maingroup,
                user_id = update.effective_user.id
                )

        valid_statuses = [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
                ]

        if member.status not in valid_statuses:
            return False

        return True
    except BadRequest as e:
        logger.warning("ERROR %s | %s | @ %s : %s", update.effective_user.first_name, update.effective_user.id, update.effective_user.username, e)
        return False

def check_conversation_available(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id     = update.effective_chat.id

        if (len(context.bot_data['admin_in_broadcast']) != 0) and (user_id not in context.bot_data['admin_in_broadcast']):
            text = "Mohon maaf fitur sedang digunakan oleh Admin lain"
            button_list = [
                    InlineKeyboardButton("Kembali", callback_data='start_menu')
                    ]
            reply_markup= InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

            await update.callback_query.edit_message_text(
                    text        = text,
                    reply_markup= reply_markup
                    )
            return ConversationHandler.END

        return await func(update, context, *args, **kwargs)
    return wrapped

def check_user_is_banned(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        if str(user_id) in context.bot_data['list_banned_users']:
            if str(user_id) in context.bot_data['list_users']:
                del context.bot_data['list_users'][str(user_id)]
            elif user_id in context.bot_data['admin_in_broadcast']:
                context.bot_data['admin_in_broadcast'].remove(user_id)
                del context.user_data['MESSAGE_ID']
                del context.user_data['BROADCAST_IDs']
                del context.user_data['NOTIFICATION_IDs']
            elif 'listban_order_segment' in context.user_data:
                del context.user_data['listban_order_segment']
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def check_user_in_order(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_chat.id
        if str(user_id) in context.bot_data['list_users']:
            text = "<i>Sesi check dengan Owner sedang berjalan</i>"
            await context.bot.send_message(
                    chat_id     = user_id,
                    text        = text,
                    parse_mode  = ParseMode.HTML
                    )
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
