from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from admin.ban.list_ban import ban_user, unban_user, update_ban_list_order
from utils.authorization import private, check_user_is_admins, check_user_is_banned
from utils.ui_utility import build_menu

@private
@check_user_is_banned
@check_user_is_admins
async def list_ban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    list_bu         = context.bot_data['list_banned_users']
    bu_ids          = [int(bu_id) for bu_id in list_bu.keys()]
    navigation      = update.callback_query.data[-4:]
    total_segments  = update_ban_list_order(
            n_rows      = 5,
            len_ban_list= len(list_bu)
            )
    if 'listban_order_segment' not in context.user_data:
        context.user_data['listban_order_segment'] = 1

    order = context.user_data['listban_order_segment']

    if navigation == 'next' and order < total_segments:
        order += 1
        context.user_data['listban_order_segment'] += 1

    elif navigation == 'prev' and order > 1:
        order -= 1
        context.user_data['listban_order_segment'] -= 1

    text        = "Berikut daftar user yang telah di ban:"
    show_rows   = 5*(order-1)
    
    if len(list_bu) > 0:
        button_user_banned_list = [
                InlineKeyboardButton(f'{list_bu[str(chat_id)][0]}', callback_data=f'banned_user_menu_{chat_id}') for chat_id in bu_ids[show_rows:len(bu_ids)]
                ]

    else:
        button_user_banned_list = list()

    raw_button_navigation   = [
            InlineKeyboardButton('Previous', callback_data='banned_user_list_prev') if order != 1 else None,
            InlineKeyboardButton('Menu Admin', callback_data='admin_menu'),
            InlineKeyboardButton('Next', callback_data='banned_user_list_next') if order != total_segments else None
            ]
    button_navigation       = list(filter(None, raw_button_navigation))

    reply_markup = InlineKeyboardMarkup(build_menu(button_user_banned_list, footer_buttons = button_navigation, n_cols = 1))

    await update.callback_query.edit_message_text(
            text        = text,
            reply_markup= reply_markup
            )

@private
@check_user_is_banned
@check_user_is_admins
async def banned_user_menu(update: Update, context: ContextTypes):
    await update.callback_query.answer()

    banned_user_id      = int(update.callback_query.data[17:])
    banned_user_name    = context.bot_data['list_banned_users'][str(banned_user_id)][0]
    banned_user_username= context.bot_data['list_banned_users'][str(banned_user_id)][2]

    admin_id        = context.bot_data['list_banned_by_admins'][str(banned_user_id)][0]
    admin_name      = context.bot_data['list_banned_by_admins'][str(banned_user_id)][1]
    admin_username  = context.bot_data['list_banned_by_admins'][str(banned_user_id)][2]

    text = "<b>Data Banned User</b>\n"
    text+= "-------------------------\n"
    text+= f"<b>Nama:</b> <code>{banned_user_name}</code>\n"
    text+= f"<b>Username:</b> @{banned_user_username}\n"
    text+= "\n"
    text+= "<i>di ban oleh:</i>\n"
    text+= f"<b>Admin:</b> <code>{admin_name}</code>\n"
    text+= f"<b>Username:</b> @{admin_username}"

    button_list = [
            InlineKeyboardButton('Kembali', callback_data='banned_user_list'),
            InlineKeyboardButton('Menu Admin', callback_data='admin_menu'),
            InlineKeyboardButton('Unban User', callback_data=f"unban_user_{banned_user_id}")
            ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))

    await update.callback_query.edit_message_text(
            text        = text,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

@private
@check_user_is_banned
@check_user_is_admins
async def unban_user_process(update: Update, context: ContextTypes):
    await update.callback_query.answer()

    banned_user_id  = int(update.callback_query.data[11:])
    banned_user_name= context.bot_data['list_banned_users'][str(banned_user_id)][0]
    await unban_user(context, banned_user_id)

    text = f"<code>{banned_user_name}</code> <i>telah berhasil di <b>un-ban</b>!</i>"

    button_list = [
            InlineKeyboardButton('Kembali', callback_data='banned_user_list'),
            InlineKeyboardButton('Menu Admin', callback_data='admin_menu')
            ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    await update.callback_query.edit_message_text(
            text        = text,
            parse_mode  = ParseMode.HTML,
            reply_markup= reply_markup
            )

    del context.user_data['listban_order_segment']
