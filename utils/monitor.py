import telegram
from temp.temp_data import del_user
from utils.ui_utility import build_menu
from utils.authorization import owneronly
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def monitor_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread_id   = update.message.message_thread_id
    recipient_id= context.bot_data['list_threads'][str(thread_id)]

    await close_order(recipient_id, thread_id, context)

async def close_order(recipient_id, thread_id, context):
    await del_user(context, recipient_id)

    text = "Sesi chat telah ditutup oleh Owner, silahkan kembali ke menu utama"
    button_list     = [
            InlineKeyboardButton("Kembali", callback_data="start_menu")
            ]
    reply_markup    = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    await context.bot.send_message(
            chat_id         = recipient_id,
            text            = text,
            reply_markup    = reply_markup
            )
