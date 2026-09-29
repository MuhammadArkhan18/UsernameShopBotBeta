from telegram.ext import filters

USER_CONTENT_ONLY = (
        filters.TEXT |
        filters.ATTACHMENT |
        filters.LOCATION |
        filters.CONTACT
        )
