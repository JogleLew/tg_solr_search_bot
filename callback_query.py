#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bot_const
import bot_global
import telegram
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def escape(text):
    return text.replace("<", "&lt;").replace(">", "&gt;")

def format_result(solr_result):
    r = ''
    for idx, hit in enumerate(solr_result):
        r = r + str(idx + 1) + '. ' + '<b>' + escape(hit['sender'][0] if 'sender' in hit else '') + '</b>: ' + escape(hit['content'][0]) + '\n'
    return r

def callback_query(bot, update):
    callback_data = update.callback_query.data
    origin_message_id = update.callback_query.message.message_id
    args = callback_data.split(',')
    if args[0] == 'choose':
        bot.deleteMessage(chat_id=int(args[1]), message_id=origin_message_id)
        bot.sendMessage(chat_id=int(args[1]), text='点击跳转', reply_to_message_id=int(args[2]))
    elif args[0] == 'list':
        p = args[1:]
        chat_id, target_chat_id, msg_id, page, query = int(p[0]), int(p[1]), int(p[2]), int(p[3]), ",".join(p[4:])
        query_text = bot_global.value(query, "")
        if page < 0:
            bot.answer_callback_query(update.callback_query.id)
            return
        solr = bot_global.value('solr', None)
        if solr is not None:
            solr_result = list(solr.search('chat:"%d" AND content:%s' % (target_chat_id, query_text), **{"start": page * 10, "rows": 10}))
            if len(solr_result) == 0:
                bot.answer_callback_query(update.callback_query.id)
                return
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
                    InlineKeyboardButton('上一页', callback_data=('list,%d,%d,%d,%d,%s' % (chat_id, target_chat_id, msg_id, page - 1, query))), 
                    InlineKeyboardButton('下一页', callback_data=('list,%d,%d,%d,%d,%s' % (chat_id, target_chat_id, msg_id, page + 1, query))) 
                ]
            ]
            motd_markup = InlineKeyboardMarkup(motd_keyboard)
            bot.edit_message_text(
                chat_id=chat_id, 
                message_id=msg_id,
                text=format_result(solr_result) + "\n- 第 %s 页 -" % page, 
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                chat_id=chat_id, 
                message_id=msg_id,
                reply_markup=motd_markup
            )
            bot.answer_callback_query(update.callback_query.id)
    elif args[0] == 'search':
        p = args[1:]
        chat_id, target_chat_id = p[0], p[1]
        bot_global.assign("search_" + chat_id, target_chat_id)
        bot.send_message(chat_id, "请输入关键字进行查询")
        bot.answer_callback_query(update.callback_query.id)

_handler = CallbackQueryHandler(callback_query)
