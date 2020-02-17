#! /usr/bin/env python3
# -*- coding: utf-8 -*-

HIRA_START = '0x3041' # ぁ
HIRA_END   = '0x3096' # ゖ
KATA_START = '0x30a1' # ァ
KATA_END   = '0x30fa' # ヺ
KANJI_START = '0x4e00' # 一(ichi)
KANJI_END   = '0x9fff' #


def is_kanji(char):
    unicode_hex = hex(ord(char))
    if KANJI_START <= unicode_hex <= KANJI_END:
        return True
    return False

def is_hiragana(char):
    unicode_hex = hex(ord(char))
    if HIRA_START <= unicode_hex <= HIRA_END:
        return True
    return False

def is_katakana(char):
    unicode_hex = hex(ord(char))
    if KATA_START <= unicode_hex <= KATA_END:
        return True
    return False

def is_japanese_letter(char):
    unicode_hex = hex(ord(char))
    if (_IS_HIRAGANA(unicode_hex) or _IS_KATAKANA(unicode_hex) or
        _IS_KANJI(unicode_hex)):
        return True
    return False
