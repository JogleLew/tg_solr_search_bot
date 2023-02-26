#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GlobalVar:
    var_set = {}

def assign(var_name, var_value):
    GlobalVar.var_set[var_name] = var_value

def value(var_name, default_value):
    if not var_name in GlobalVar.var_set:
        GlobalVar.var_set[var_name] = default_value
        return default_value
    return GlobalVar.var_set[var_name]

def get_sender_name(message):
    real_sender = message.from_user
    if message.forward_from:
        real_sender = message.forward_from
    username = real_sender.first_name
    if real_sender.last_name:
        username = username + " " + real_sender.last_name
    if message.forward_from_chat:
        username = message.forward_from_chat.title
    return username

def get_real_sender_name(message):
    real_sender = message.from_user
    username = real_sender.first_name
    if real_sender.last_name:
        username = username + " " + real_sender.last_name
    return username

def dump_to_file():
    with open('data/dump.txt', 'w') as f:
        f.write(json_dump(GlobalVar.var_set))
