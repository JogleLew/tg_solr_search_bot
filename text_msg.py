#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import copy
import random
import requests
import datetime
import bot_const
import bot_global
import telegram
import base64
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

choose_from = lambda a: a[random.randint(0, len(a) - 1)] 

def escape(text):
    return text.replace("<", "&lt;").replace(">", "&gt;")

def format_result(solr_result):
    r = ''
    for idx, hit in enumerate(solr_result):
        r = r + str(idx + 1) + '. ' + '<b>' + escape(hit['sender'][0] if 'sender' in hit else '') + '</b>: ' + escape(hit['content'][0]) + '\n'
    return r

def text_msg(bot, update):
    message = update.edited_message or update.message
    print(message)
    if message is None:
        return

    if message.chat_id > 0 and bot_global.value("search_%s" % message.chat_id, None):
        target_chat_id = int(bot_global.value("search_%s" % message.chat_id, None))
        r = bot.get_chat_member(chat_id=target_chat_id, user_id=message.from_user.id)
        if r.status == "left" or r.status == "kicked":
            message.reply_text("您无权限查询群聊记录")
        else:
            solr = bot_global.value('solr', None)
            if solr is not None and message.text:
                solr_result = list(solr.search('chat:"%d" AND content:%s' % (target_chat_id, message.text), **{"rows": 10}))
                if len(format_result(solr_result)) == 0:
                    message.reply_text(text='没有找到相关内容')
                else:
                    new_msg = bot.send_message(
                        chat_id=message.chat_id, 
                        text=format_result(solr_result) + "\n- 第 0 页 -", 
                        parse_mode='HTML'
                    )
                    uid = str(uuid.uuid4())[-4:]
                    bot_global.assign("query_" + uid, message.text)
                    current_page = 0
                    motd_keyboard = [
                        [
                            InlineKeyboardButton(str(idx + 1), url="https://t.me/c/%s/%s" % (str(target_chat_id)[4:], hit['id']))
                            for idx, hit in enumerate(solr_result) if idx < 5
                        ],
                        [
                            InlineKeyboardButton(str(idx + 1), url="https://t.me/c/%s/%s" % (str(target_chat_id)[4:], hit['id']))
                            for idx, hit in enumerate(solr_result) if idx >= 5
                        ],
                        [
                            InlineKeyboardButton('上一页', callback_data=('list,%d,%d,%d,%d,%s' % (message.chat_id, target_chat_id, new_msg.message_id, current_page - 1, "query_" + uid))), 
                            InlineKeyboardButton('下一页', callback_data=('list,%d,%d,%d,%d,%s' % (message.chat_id, target_chat_id, new_msg.message_id, current_page + 1, "query_" + uid))) 
                        ]
                    ]
                    motd_markup = InlineKeyboardMarkup(motd_keyboard)
                    bot.edit_message_reply_markup(
                        chat_id=message.chat_id, 
                        message_id=new_msg.message_id, 
                        reply_markup=motd_markup
                    )

    # message recording
    solr = bot_global.value('solr', None)
    if solr is not None:
        content_body = {
            'date': message.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'type': 'text',
            'chat': message.chat_id,
            'id': message.message_id,
            'from': message.from_user.id,
            'sender': bot_global.get_sender_name(message),
            'content': message.text
        }
        if message.forward_from:
            content_body['forward_from'] = message.forward_from.id
        if message.forward_from_chat:
            content_body['forward_from_chat'] = message.forward_from_chat.id
        if message.reply_to_message:
            content_body['reply_to_message'] = message.reply_to_message.message_id
        solr.add([content_body])

_handler = MessageHandler(Filters.text, text_msg)
