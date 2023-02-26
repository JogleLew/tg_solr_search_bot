#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pysolr
import logging
import requests
import traceback
from telegram.ext import Updater, CommandHandler
import bot_const
import bot_global
import search_cmd
import callback_query
import text_msg
import media_msg

# config logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# connect solr
solr = pysolr.Solr(bot_const.SOLR_URL, always_commit=True, auth=requests.auth.HTTPBasicAuth(bot_const.SOLR_USERNAME, bot_const.SOLR_PASSWORD))
bot_global.assign('solr', solr)

# config bot
updater = Updater(token=bot_const.BOT_TOKEN, use_context=False)
dispatcher = updater.dispatcher
dispatcher.add_handler(search_cmd._handler)
dispatcher.add_handler(callback_query._handler)
dispatcher.add_handler(text_msg._handler)
dispatcher.add_handler(media_msg._handler)

updater.start_polling()
