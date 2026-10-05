import logging, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import Forbidden, RetryAfter
from temp.temp_data import del_user
from data.core_data import db_path
from data.database_config import DatabaseManager
from utils.ui_utility import build_menu
from utils.authorization import private, check_conversation_available, check_user_is_banned, check_user_is_admins
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

@private
@check_user_is_banned
@check_user_is_admins
@check_conversation_available
async def broadcast_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.bot_data['admin_in_broadcast'].append(update.effective_chat.id)

    message_id  = update.callback_query.message.message_id
    text        = "<b>Broadcast Pesan</b>\n"
    text        +="-----------------------------\n"
    text        +="Pilih <i>Kirim Broadcast</i> jika sudah selesai mengirimkan pesanmu."
    text        +="<b>(Bata Waktu 10 Menit jika tidak ada aktivitas dari Admin di sesi ini)</b>"

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
@check_user_is_admins
async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["BROADCAST_IDs"].append(update.message.message_id)
 
    return "process_broadcast"

@private
@check_user_is_banned
@check_user_is_admins
async def finish_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

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

    if notif_message_ids:
        await context.bot.delete_messages(
                chat_id     = update.effective_chat.id,
                message_ids = notif_message_ids
                )

    context.application.create_task(
            run_broadcast(context, update.effective_chat.id,  users_id_data, message_ids),
            update=update
            )

    text1 = "<i>Broadcast sedang dikirim, hasilnya akan ditampilkan di sini.</i>"

    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        = text1,
            parse_mode  = ParseMode.HTML
            )

    del context.user_data["MESSAGE_ID"]
    del context.user_data["BROADCAST_IDs"]
    del context.user_data["NOTIFICATION_IDs"]

    return ConversationHandler.END

@private
@check_user_is_banned
@check_user_is_admins
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

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

@private
@check_user_is_banned
@check_user_is_admins
async def timeout_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_id = context.user_data['MESSAGE_ID']
    
    text  = "<b>Sesi Telah Ditutup</b>"
    
    await context.bot.edit_message_text(
            chat_id     = update.effective_chat.id,
            text        = text,
            parse_mode  = ParseMode.HTML,
            message_id  = message_id
            )

    text1 = "<i>Sesi <b>Broadcast</b> anda telah habis, silahkan kembali</i>"
    
    button_list = [
            InlineKeyboardButton('Kembali', callback_data='start_menu')
            ]
    reply_markup= InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        = text1,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

    del context.user_data['MESSAGE_ID']
    del context.user_data['BROADCAST_IDs']
    context.bot_data['admin_in_broadcast'].remove(update.effective_chat.id)

    return ConversationHandler.END

async def run_broadcast(context, admin_chat, user_ids, message_ids):
    sent = blocked = failed = 0
    
    try:
        for uid in user_ids:
            result = await send_to_user(context,uid, admin_chat, message_ids)
            if result == "ok":
                sent += 1
            elif result == "blocked":
                blocked += 1
            else:
                failed += 1
            await asyncio.sleep(0.05 * len(message_ids))
    
    finally:
        for i in range(0, len(message_ids), 100):
            
            try:
                await context.bot.delete_messages(
                        chat_id = admin_chat,
                        message_ids = message_ids[i:i+100]
                        
                        )
            except Exception as e:
                logger.warning("Failed to delete messages: %s", e)
        
        context.bot_data['admin_in_broadcast'].remove(admin_chat)
    
    text = "<b>Broadcast selesai</b>\n"
    text+= f"Terkirim: {sent}\n"
    text+= f"Terblokir: {blocked}\n"
    text+= f"Gagal: {failed}"

    button_list = [
            InlineKeyboardButton('Kembali', callback_data='start_menu')
            ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    await context.bot.send_message(
            chat_id     = admin_chat,
            text        = text,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

async def send_to_user(context, user_id, from_chat, message_ids):
    for i in range(0, len(message_ids), 100):
        chunk = message_ids[i:i + 100]

        for _ in range(3):
            try:
                await context.bot.copy_messages(
                        chat_id     = user_id,
                        from_chat_id= from_chat,
                        message_ids = chunk
                        )
                break

            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)

            except Forbidden:
                await DatabaseManager(db_path).delete_data(
                        table_name  = 'users',
                        primary_key = 'user_id',
                        value_key   = user_id
                        )
                return "blocked"

            except Exception as e:
                logger.warning("Failed to send broadcast messages to %s: %s", user_id, e)
                return "failed"
        
        else:
            return "failed"
    
    return "ok"
