from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from temp.temp_data import del_user
from data.core_data import db_path
from data.database_config import DatabaseManager
from utils.ui_utility import build_menu
from utils.authorization import private, check_conversation_available, check_user_is_banned
from telegram.ext import ContextTypes, ConversationHandler

@private
@check_user_is_banned
@check_conversation_available
async def broadcast_users(update: Update, context: ContextTypes):
    await update.callback_query.answer()
    context.bot_data['admin_in_broadcast'].append(update.effective_chat.id)

    message_id  = update.callback_query.message.message_id
    text        = "<b>Broadcast Pesan</b>\n"
    text        +="-----------------------------\n"
    text        +="Pilih <i>Kirim Broadcast</i> jika sudah selesai mengirimkan pesanmu."

    context.user_data["MESSAGE_ID"]         = message_id
    context.user_data["BROADCAST_IDs"]      = list()
    context.user_data["NOTIFICATION_IDs"]   = list()

    button_list = [
            InlineKeyboardButton('Kirim Broadcast', callback_data='finish_broadcast'),
            InlineKeyboardButton('Batal', callback_data='cancel')
            ]
    reply_markup= InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    await update.callback_query.edit_message_text(
            text        = text,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

    return "process_broadcast"

@check_user_is_banned
async def process_broadcast(update: Update, context: ContextTypes):
    context.user_data["BROADCAST_IDs"].append(update.message.message_id)
 
    return "process_broadcast"

@private
@check_user_is_banned
async def finish_broadcast(update: Update, context: ContextTypes):
    raw_users_id_data   = await DatabaseManager(db_path).read_data_all('users', 'user_id')
    users_id_data       = [row[0] for row in raw_users_id_data]
    message_id          = context.user_data["MESSAGE_ID"]
    message_ids         = context.user_data["BROADCAST_IDs"]
    notif_message_ids   = context.user_data["NOTIFICATION_IDs"]

    text = "<b>Broadcast Pesan</b>\n"
    text+= "-----------------------------\n"
    text+= "<i>Berikut hasil broadcastnya</i>"

    if len(message_ids) < 1:
        data = await update.callback_query.message.reply_text(
                text        = "<i>Kirim pesan broadcastnya dulu yaa</i>",
                parse_mode  = ParseMode.HTML
                )
        
        notif_message_ids.append(data.message_id)
        return "process_broadcast"

    await context.bot.edit_message_text(
            chat_id     = update.effective_chat.id,
            text        = text,
            parse_mode  = ParseMode.HTML,
            message_id  = message_id
            )

    for user_id in users_id_data:
        try:
            await context.bot.copy_messages(
                    chat_id     = user_id,
                    from_chat_id= update.effective_chat.id,
                    message_ids = message_ids
                    )
        except Exception as e:
            await DatabaseManager(db_path).delete_data(
                    table_name  = 'users',
                    primary_key = 'user_id',
                    value_key   = user_id
                    )

    if len(notif_message_ids) >= 1:
        await context.bot.delete_messages(
                chat_id     = update.effective_chat.id,
                message_ids = notif_message_ids
                )

    await context.bot.delete_messages(
            chat_id     = update.effective_chat.id,
            message_ids = message_ids
            )

    text1 = "<i>Broadcast kamu telah berhasil terkirim</i>"
    button_list = [
            InlineKeyboardButton("Kembali", callback_data = 'start_menu')
            ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols = 1))

    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        = text1,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

    del context.user_data["MESSAGE_ID"]
    del context.user_data["BROADCAST_IDs"]
    del context.user_data["NOTIFICATION_IDs"]
    context.bot_data['admin_in_broadcast'].remove(update.effective_chat.id)

    return ConversationHandler.END

@private
@check_user_is_banned
async def cancel_broadcast(update: Update, context: ContextTypes):
    message_ids         = context.user_data["BROADCAST_IDs"]
    notif_message_ids   = context.user_data["NOTIFICATION_IDs"]
    
    text = "Kamu telah membatalkan broadcast, silahkan kembali"

    button_list = [
            InlineKeyboardButton("Kembali", callback_data='start_menu')
            ]
    reply_markup= InlineKeyboardMarkup(build_menu(button_list, n_cols = 1))

    await update.callback_query.edit_message_text(
            text        = text,
            reply_markup= reply_markup
            )

    if len(notif_message_ids) >= 1:
        await context.bot.delete_messages(
                chat_id     = update.effective_chat.id,
                message_ids = notif_message_ids
                )
    
    if len(message_ids) >= 1:
        await context.bot.delete_messages(
                chat_id     = update.effective_chat.id,
                message_ids = message_ids
                )

    del context.user_data["MESSAGE_ID"]
    del context.user_data["BROADCAST_IDs"]
    del context.user_data["NOTIFICATION_IDs"]
    context.bot_data['admin_in_broadcast'].remove(update.effective_chat.id)

    return ConversationHandler.END
