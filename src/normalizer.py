#! /usr/bin/env python3
#-*- coding: utf-8 -*-

import unicodedata
import time


class Normalizer(object):

    def __init__(self, hira_kata = False, kogaki_dakuon = False, latin_case = False):
        '''
            hira_kata: hira -> kata only
            kana_all: include kogaki, dakuon
            latin_case: upper -> lower
        '''
        self.hira_kata = hira_kata
        self.kogaki_dakuon = kogaki_dakuon
        self.latin_case = latin_case

        self.trans_table = self._init_trans_table()

    def normalize(self, s):
        ret = unicodedata.normalize('NFKC', s)
        return ret.translate(self.trans_table)

    def _init_trans_table(self):
        ret = {}
        if self.hira_kata and self.kogaki_dakuon:
            ret.update(self._make_kogaki_table())
            ret.update(self._make_dakuon_table())
            ret.update(self._make_kana_all_table())
        elif self.kogaki_dakuon:
            ret.update(self._make_kogaki_table())
            ret.update(self._make_dakuon_table())
        elif self.hira_kata:
            ret.update(self._make_kana_table())

        if self.latin_case:
            ret.update(self._make_latin_table())
        return ret


    def _make_trans_table(self, s, t):
        return {ord(x): ord(y) for x, y in zip(s, t)}

    def _make_kogaki_table(self):
        '''
            小書き文字 -> 通常文字
            ㇷ゚は unicode でも 3 byte 文字で Python での扱いが難しいため含めない(TODO: 要確認)
        '''
        return self._make_trans_table(
            'ぁぃぅぇぉっゃゅょゎゕゖ' + 
            'ァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ',
            'あいうえおつやゆよわかけ' + 
            'アイウエオカクケシスツトヌハヒフヘホムヤユヨラリルレロワ'
        )

    def _make_dakuon_table(self):
        '''
            濁音・半濁音 -> 清音
        '''
        return self._make_trans_table(
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゔ' +
            'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヴ',
            'かきくけこさしすせそたちつてとはひふへほはひふへほふ' +
            'カキクケコサシスセソタチツテトハヒフヘホハヒフヘホフ',
        )

    def _make_kana_table(self):
        '''
            ひらがな -> カタカナ
        '''
        return self._make_trans_table(
            'ぁぃぅぇぉあいうえおかきくけこさしすせそたちつてと' +
            'なにぬねのはひふへほまみむめもやゆよらりるれろわゎゐゑをん' +
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょっんゔゕゖ',
            'ァィゥェォアイウエオカキクケコサシスセソタチツテト' +
            'ナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヮヰヱヲン' +
            'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポャュョッンヴヵヶ'
        )

    def _make_kana_all_table(self):
        '''
            ひらがな     -> カタカナ
            小書き文字   -> 通常文字
            濁音・半濁音 -> 清音
        '''
        return self._make_trans_table(
            'ぁぃぅぇぉあいうえおかきくけこさしすせそたちつてと' +
            'なにぬねのはひふへほまみむめもやゆよらりるれろわゎゐゑをん' +
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょっんゔゕゖ',
            'アイウエオアイウエオカキクケコサシスセソタチツテト' +
            'ナニヌネノハヒフヘホマミムメモヤユヨラリルレロワワヰヱヲン' +
            'カキクケコサシスセソタチツテトハヒフヘホハヒフヘホヤユヨツンフカケ'
        )

    def _make_latin_table(self):
        '''
            latin alphabet
        '''
        return self._make_trans_table(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'abcdefghijklmnopqrstuvwxyz'
        )


