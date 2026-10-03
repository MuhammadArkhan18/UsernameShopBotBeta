import telegram
from html import escape
from temp.temp_data import input_user, del_user
from utils.ui_utility import build_menu
from utils.monitor import close_order
from utils.authorization import restricted, owneronly, private, check_user_is_banned, check_user_in_order
from data.core_data import id_maingroup
from data.database_config import DatabaseManager
from admin.ban.list_ban import ban_user
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden

@private
@check_user_is_banned
@check_user_in_order
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    first_name  = update.effective_user.first_name
    user_id     = update.effective_user.id
    username    = update.effective_user.username

    text = "Kamu sudah terhubung dengan ownernya, silahkan pesan username dan nego di sini."
    text1 = "<b>Data Pembeli</b> \n"
    text1+= "---------------- \n"
    text1+= f"<b>Nama</b> : <code>{escape(first_name)}</code> \n"
    text1+= f"<b>ID</b> : <code>{user_id}</code> \n"
    if username:
        text1+= f"<b>Username</b> : @{escape(username)}\n"
    else:
        text1+= f'<b>Profile</b> : <a href="tg://user?id={user_id}">Tap Di sini</a>'

    topic = await context.bot.create_forum_topic(
            chat_id = id_maingroup,
            name    = f"Chat {first_name}"
            )

    topic_id = topic.message_thread_id
    await input_user(
            context     = context,
            first_name  = first_name,
            chat_id     = user_id,
            username    = username,
            thread_id   = topic_id
            )

    button_list = [
            InlineKeyboardButton("Ban User", callback_data = f"ban_user_{user_id}")
            ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    await update.callback_query.edit_message_text(text = text)
    await context.bot.send_message(
            chat_id             = id_maingroup,
            text                = text1,
            parse_mode          = ParseMode.HTML,
            message_thread_id   = topic_id,
            reply_markup        = reply_markup
            )

@private
@check_user_is_banned
@restricted
async def order_user_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id     = update.effective_chat.id
    topic_id    = context.bot_data['list_users'][str(user_id)][3]

    try:
        message = await context.bot.forward_message(
                chat_id             = id_maingroup,
                from_chat_id        = user_id,
                message_id          = update.message.message_id,
                message_thread_id   = topic_id
                )

        if message.message_thread_id != topic_id:
            await context.bot.delete_message(
                    chat_id = id_maingroup,
                     message_id = message.message_id
                    )
            await close_order(user_id, topic_id, context)
            return
    
    except BadRequest as e:
        print("ERROR: ", e)
        await close_order(user_id, topic_id, context)
        return

@owneronly
@check_user_is_banned
async def order_owner_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_id = context.bot_data['list_threads'].get(str(update.message.message_thread_id))
    if recipient_id is None:
        return
    
    try:
        await update.message.copy(
                chat_id = recipient_id
                )
    except Exception as e:
        print(e)
        text = "<i>Pengguna telah ban atau hapus riwayat percakapan dengan bot ini</i>"
        await update.message.reply_text(
                text        = text,
                parse_mode  = ParseMode.HTML
                )

@owneronly
@check_user_is_banned
async def ban_user_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ban_user_id         = int(update.callback_query.data[9:])
    
    if str(ban_user_id) not in context.bot_data['list_users']:
        await update.callback_query.answer('Sesi sudah ditutup atau user sudah diban')
        return
    else:
        await update.callback_query.answer()
    
    ban_user_name       = context.bot_data['list_users'][str(ban_user_id)][0]
    ban_user_username   = context.bot_data['list_users'][str(ban_user_id)][2]
    thread_id           = context.bot_data['list_users'][str(ban_user_id)][3]

    admin_id        = update.effective_user.id
    admin_name      = update.effective_user.first_name
    admin_username  = update.effective_user.username

    await ban_user(
            context         = context,
            user_id         = ban_user_id,
            name            = ban_user_name,
            username        = ban_user_username,
            admin_id        = admin_id,
            admin_name      = admin_name,
            admin_username  = admin_username
            )

    await del_user(context, ban_user_id)

    text = f"<b>Pembeli</b> <code>{escape(ban_user_name)}</code> <b>telah di-banned</b>"
    text1= "<b>Anda telah diban oleh Owner. Selama ban belum dicabut, anda tidak memiliki akses apapun di bot ini</b>"

    await update.callback_query.edit_message_text(
            text        = text,
            parse_mode  = ParseMode.HTML
            )

    try:
        await context.bot.send_message(
                chat_id     = ban_user_id,
                text        = text1,
                parse_mode  = ParseMode.HTML
                )

    except Forbidden as e:
        return
