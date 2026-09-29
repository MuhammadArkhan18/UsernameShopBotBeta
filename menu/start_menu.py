import telegram
from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from data.core_data import db_path
from data.database_config import DatabaseManager
from utils.ui_utility import build_menu
from utils.authorization import private, check_user_in_conversation, check_user_is_owners, check_user_is_banned
from telegram.ext import ContextTypes

@private
@check_user_is_banned
@check_user_in_conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_command = False
    if update.message and update.message.entities:
        for entity in update.message.entities:
            if entity.type == MessageEntity.BOT_COMMAND and entity.offset == 0:
                is_command = True
                break

    if is_command:
        id_user         = update.effective_user.id
        user_name       = update.effective_user.first_name
        user_username   = update.effective_user.username

        await context.bot.delete_message(
                chat_id = update.effective_chat.id,
                message_id = update.message.message_id
                )

        await DatabaseManager(db_path).insert_data('users', 'user_id', user_id=id_user, name=user_name, username=user_username)

    text = "<b>Selamat Datang di UsernameShop</b>! \n"
    text+= "~~~~~~~~~~~~~~~~~~~~~ \n"
    text+= "Berikut menu utama di toko kami."
    button_list = [
            InlineKeyboardButton("Beli Username", callback_data='order')
            ]
    if await check_user_is_owners(update, context):
        button_list += [
                InlineKeyboardButton("Menu Admin", callback_data='admin_menu')
                ]

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols = 1))

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
                text        = text,
                parse_mode  = telegram.constants.ParseMode.HTML,
                reply_markup= reply_markup
                )
        return

    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        =text,
            parse_mode  =telegram.constants.ParseMode.HTML,
            reply_markup=reply_markup
            )
