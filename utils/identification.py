import telegram
from utils.authorization import private, maingroup_only, check_user_in_conversation
from telegram import Update
from telegram.ext import ContextTypes

@private
@check_user_in_conversation
async def user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_user = update.effective_user.id
    text = f"User id anda: `{id_user}`"
    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        = text,
            parse_mode  = telegram.constants.ParseMode.MARKDOWN_V2
            )

@maingroup_only
async def group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_group= update.effective_chat.id
    text    = f"id grup anda: `{id_group}`"
    await context.bot.send_message(
            chat_id     = update.effective_chat.id,
            text        = text,
            parse_mode  = telegram.constants.ParseMode.MARKDOWN_V2
            )
