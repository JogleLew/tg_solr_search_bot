#!/usr/bin/env python
# -*- coding: utf-8 -*-

import text_msg
import bot_const
import bot_global
import telegram
from telegram.ext import MessageHandler, Filters

def media_msg(bot, update):
    message = update.edited_message or update.message
    print(message)

    solr = bot_global.value('solr', None)
    if solr is not None:
        content_body = {
            'date': message.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'chat': message.chat_id,
            'id': message.message_id,
            'from': message.from_user.id,
            'sender': bot_global.get_sender_name(message)
        }
        if message.forward_from:
            content_body['forward_from'] = message.forward_from.id
        if message.forward_from_chat:
            content_body['forward_from_chat'] = message.forward_from_chat.id
        if message.reply_to_message:
            content_body['reply_to_message'] = message.reply_to_message.message_id
        if message.sticker:
            content_body['type'] = 'sticker'
            content_body['file_id'] = message.sticker.file_id
            if message.sticker.emoji:
                content_body['content'] = message.sticker.emoji
        elif message.photo:
            content_body['type'] = 'photo'
            content_body['file_id'] = message.photo[-1].file_id
            if message.caption:
                content_body['content'] = message.caption
        elif message.video:
            content_body['type'] = 'video'
            content_body['file_id'] = message.video.file_id
            if message.caption:
                content_body['content'] = message.caption
        elif message.document:
            content_body['type'] = 'document'
            content_body['file_id'] = message.document.file_id
            if message.document.file_name:
                content_body['content'] = message.document.file_name
        elif message.audio:
            content_body['type'] = 'audio'
            content_body['file_id'] = message.audio.file_id
            if message.audio.title:
                content_body['content'] = message.audio.title
        elif message.voice:
            content_body['type'] = 'voice'
            content_body['file_id'] = message.voice.file_id
        else:
            content_body['type'] = 'other'
            content_body['file_id'] = ''

        solr.add([content_body])

_handler = MessageHandler(
    ~Filters.text, 
    media_msg
)
