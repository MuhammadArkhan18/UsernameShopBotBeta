#-----------------------------------IMPORTING PACKAGES----------------------------------
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, filters, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler
from utils.filters import USER_CONTENT_ONLY
from utils.monitor import monitor_threads
from utils.identification import user_id, group_id
from data.core_data  import TOKEN, id_maingroup, db_path
from data.database_config import DatabaseManager
from temp.temp_data import initiate_temp_data
from menu.start_menu import start
from menu.admin_menu import admin_menu
from menu.ban_menu import list_ban_menu, banned_user_menu, unban_user_process
from conversation_clients.order import order, order_user_session, order_owner_session, ban_user_order
from broadcast.broadcast_users import broadcast_users, process_broadcast, finish_broadcast, cancel_broadcast
#--------------------------------FOR DEBUGGING PURPOSES---------------------------------

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)

#-------------------------------SET UP DATABASE MANAGER---------------------------------
db_helper = DatabaseManager(db_path)

#-----------------------INITIATE REQUIRED ELEMENTS FOR BOT------------------------------
async def on_startup(application):
    #Initiate the database of the bot
    await db_helper.init_db()
    #Initiate temporary data for the bot
    await initiate_temp_data(application)

#------------------------------------SET UP THE BOT-------------------------------------
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    
    #Set up the handlers
    start_handler               = CommandHandler('start', start)
    userid_handler              = CommandHandler('userid', user_id)
    groupid_handler             = CommandHandler('groupid', group_id)
    order_handler               = CallbackQueryHandler(order, pattern="^order$")
    monitor_threads_handler     = MessageHandler(filters.Chat(chat_id=id_maingroup) & filters.StatusUpdate.FORUM_TOPIC_CLOSED, monitor_threads)
    order_user_session_handler  = MessageHandler(USER_CONTENT_ONLY & ~filters.COMMAND, order_user_session)
    order_owner_session_handler = MessageHandler(filters.Chat(chat_id=id_maingroup) & (USER_CONTENT_ONLY & ~filters.COMMAND), order_owner_session)
    
    startmenu_handler           = CallbackQueryHandler(start, pattern="^start_menu$")
    adminmenu_handler           = CallbackQueryHandler(admin_menu, pattern="^admin_menu$")
    listbanmenu_handler         = CallbackQueryHandler(list_ban_menu, pattern='^banned_user_list((_next|_prev))?$')
    banuser_order_handler       = CallbackQueryHandler(ban_user_order, pattern="^ban_user_")
    banned_user_menu_handler    = CallbackQueryHandler(banned_user_menu, pattern='^banned_user_menu_')
    unban_user_process_handler  = CallbackQueryHandler(unban_user_process, pattern='^unban_user_')

    broadcast_handler = ConversationHandler(
            entry_points= [CallbackQueryHandler(broadcast_users, pattern='^broadcast_users$')],
            states      = {
                "process_broadcast" : [
                    MessageHandler(filters.ChatType.PRIVATE & USER_CONTENT_ONLY & ~filters.COMMAND, process_broadcast),
                    CallbackQueryHandler(finish_broadcast, pattern="^finish_broadcast$")
                    ]
                },
            fallbacks   = [CallbackQueryHandler(cancel_broadcast, pattern="^cancel$")]
            )

    #Registrates the handlers
    application.add_handler(start_handler)
    application.add_handler(userid_handler)
    application.add_handler(groupid_handler)
    application.add_handler(order_handler)
    application.add_handler(startmenu_handler)
    application.add_handler(adminmenu_handler)
    application.add_handler(listbanmenu_handler)
    application.add_handler(banned_user_menu_handler)
    application.add_handler(unban_user_process_handler)
    application.add_handler(banuser_order_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(monitor_threads_handler)
    application.add_handler(order_owner_session_handler)
    application.add_handler(order_user_session_handler)
    
    #Start the bot via polling method
    application.run_polling()
