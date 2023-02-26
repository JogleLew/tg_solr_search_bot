#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import threading
import bot_const
import bot_global
from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def escape(text):
    return text.replace("<", "&lt;").replace(">", "&gt;")

def format_result(solr_result):
    r = ''
    for idx, hit in enumerate(solr_result):
        r = r + str(idx + 1) + '. ' + '<b>' + escape(hit['sender'][0] if 'sender' in hit else '') + '</b>: ' + escape(hit['content'][0]) + '\n'
    return r

def delete_msg(message):
    message.delete()

def search(bot, update, args):
    solr = bot_global.value('solr', None)
    message = update.message
    target_chat_id = message.chat_id
    if target_chat_id in bot_const.PRIVATE_CHAT_SEARCH_ENABLE:
        result_message = message.reply_text("为避免 Spam，请私聊 bot 发送 /search 使用群聊搜索功能")
        t = threading.Timer(10, delete_msg, args=(message, ))
        t.start()
        t = threading.Timer(10, delete_msg, args=(result_message, ))
        t.start()
        return
    if target_chat_id == -1001828386705:
        target_chat_id = -1001331033307

    # Private chat
    if target_chat_id > 0:
        if len(" ".join(args).strip()) == 0:
            msg = bot.send_message(target_chat_id, "请稍候...")
            chat_allow_search = []
            for cid in bot_const.PRIVATE_CHAT_SEARCH_ENABLE:
                r = bot.get_chat_member(chat_id=cid, user_id=target_chat_id)
                if r.status == "left" or r.status == "kicked":
                    continue
                r = bot.get_chat(chat_id=cid)
                chat_allow_search.append((cid, r.title))

            if len(chat_allow_search) == 0:
                msg.edit_text("您无权限搜索任何群聊记录。")
            else:
                msg = msg.edit_text("请在下方选择群聊，然后输入查询关键字")
                msg.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(ctitle, callback_data="search,%s,%s" % (message.chat_id, cid))] for cid, ctitle in chat_allow_search
                    ])
                )
            return

    # Group chat
    if len(" ".join(args).strip()) == 0:
        message.reply_text("使用方法：/search 你要查找的关键字")
        return
    if solr is not None:
        solr_result = list(solr.search('chat:"%d" AND content:%s' % (target_chat_id, " ".join(args)), **{"rows": 10}))
        if len(format_result(solr_result)) == 0:
            bot.send_message(chat_id=update.message.chat_id, text='没有找到相关内容')
        else:
            new_msg = bot.send_message(
                chat_id=update.message.chat_id, 
                text=format_result(solr_result) + "\n- 第 0 页 -", 
                parse_mode='HTML'
            )
            current_page = 0
            uid = str(uuid.uuid4())[-4:]
            bot_global.assign("query_" + uid, " ".join(args))
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

_handler = CommandHandler('search', search, pass_args=True)
