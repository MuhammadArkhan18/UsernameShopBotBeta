import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Unhandled error ", exc_info=context.error)
