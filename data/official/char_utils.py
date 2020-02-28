#! /usr/bin/env python3
# -*- coding: utf-8 -*-

NUM_START = '0x0030' # 0
NUM_END   = '0x0039' # 9
LATIN_UPPER_START = '0x0041' # A
LATIN_UPPER_END   = '0x005a' # Z
LATIN_LOWER_START = '0x0061' # a
LATIN_LOWER_END   = '0x007a' # z

HIRA_START = '0x3041' # ぁ
HIRA_END   = '0x3096' # ゖ
KATA_START = '0x30a1' # ァ
KATA_END   = '0x30fa' # ヺ
KANJI_START = '0x4e00' # 一(ichi)
KANJI_END   = '0x9fff' #


def is_num(char):
    unicode_hex = hex(ord(char))
    if NUM_START <= unicode_hex <= NUM_END:
        return True
    return False

def is_alpha(char):
    unicode_hex = hex(ord(char))
    if (LATIN_UPPER_START <= unicode_hex <= LATIN_UPPER_END or
        LATIN_LOWER_START <= unicode_hex <= LATIN_LOWER_END):
        return True
    return False

def is_alphanum(char):
    if is_num(char) or is_alpha(char):
        return True
    return False


def is_kanji(char):
    unicode_hex = hex(ord(char))
    return is_kanji_code(unicode_hex)

def is_kanji_code(unicode_hex):
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

def contains_kanji(s):
    for c in s:
        if is_kanji(c):
            return True
    return False


def is_hiragana_word(s):
    ''' mark will not be judged '''
    for c in s:
        if is_katakana(c) or is_kanji(c) or is_alphanum(c):
            return False
    return True

def is_katakana_word(s):
    ''' mark will not be judged '''
    for c in s:
        if is_hiragana(c) or is_kanji(c) or is_alphanum(c):
            return False
    return True

