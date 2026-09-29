from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from utils.ui_utility import build_menu
from utils.authorization import private, check_user_is_admins, check_user_is_banned

@private
@check_user_is_banned
@check_user_is_admins
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if 'listban_order_segment' in context.user_data:
        del context.user_data['listban_order_segment']

    name = update.effective_user.first_name
    
    text = f"<b>Halo</b> <code>{name}</code><b>!</b>\n"
    text+= "--------------------------\n"
    text+= "Berikut menu khusus untuk admin"

    button_list = [
            InlineKeyboardButton("Broadcast Pesan", callback_data = 'broadcast_users'),
            InlineKeyboardButton("Banned User List", callback_data = 'banned_user_list'),
            InlineKeyboardButton("Kembali", callback_data = 'start_menu')
            ]

    reply_markup= InlineKeyboardMarkup(build_menu(button_list, n_cols = 1))

    await update.callback_query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup
            )
