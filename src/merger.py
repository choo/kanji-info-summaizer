#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

import os, re
import fsutils
from pprint import pprint
import char_utils
from normalizer import Normalizer

ETLCDB_CHAR_CODES_FILE = '../data/input/other/etlcdb_codes.txt'

JOYO_KANJI_PARSED_JSON = '../data/output/kanji_joyo.json'
WIKTIONARY_PARSED_TSV  = '../data/output/extrated.tsv'

OUTPUT_DIR = '../data/output'

normalizer = Normalizer(hira_kata=True)


def merge_joyo(results):
    joyo_kanjis = fsutils.read_json(JOYO_KANJI_PARSED_JSON)
    for rec in joyo_kanjis:
        title = rec['title']
        unicode_hex = hex(ord(title))
        if unicode_hex in results:
            results[unicode_hex].update(rec)
        else:
            ''' print shortage of joyo kanji '''
            pass
            print(rec)
    return results


def merge_wiktionary(results):
    kanjis = fsutils.read_csv(WIKTIONARY_PARSED_TSV)
    cnt = 0
    for rec in kanjis:
        title = rec['title']
        if len(title) > 1:
            continue
        unicode_hex = hex(ord(title))
        if unicode_hex in results:
            results[unicode_hex].update(rec)
            cnt += 1
    print('update {} kanjis with wiktionary data'.format(cnt))
    return results


def _normalize(s):
    return normalizer.normalize(s)

def _extract_yomi(yomis, jo_yomis):
    ret = []
    for yomi in yomis:
        normalized = _normalize(yomi).replace('-', '')
        if not normalized in jo_yomis:
            ret.append(yomi)
    return ret

def _get_elms(data, key):
    ret = []
    if key in data:
        ret = data[key].split(',')
    return ret


def _extract_kunyomi(info, jo_yomis):
    kun_yomis = (_get_elms(info, 'kunyomi_nai') +
                 _get_elms(info, 'kunyomi_gai') +
                 _get_elms(info, 'kunyomi_other'))
    return _extract_yomi(kun_yomis, jo_yomis)

def _extract_onyomi(info, jo_yomis):
    on_yomis = (_get_elms(info, 'onyomi_go') +
                _get_elms(info, 'onyomi_kan') +
                _get_elms(info, 'onyomi_other'))
    return _extract_yomi(on_yomis, jo_yomis)


def format_data(results):
    ret = []
    for code, info in results.items():
        if 'joyo_yomis' in info and info['joyo'] != '1':
            if info['title'] in ['彩', '硫', '磁', '且']:
                ''' 12987, 9816, 31431, 31676 '''
                ## TODO: FIX wiktionary
                continue
            print(info)
            return

        joyo_yomis = info['joyo_yomis'] if 'joyo_yomis' in info else []
        jo_yomis = [_normalize(y['yomi']) for y in joyo_yomis]
        on_yomis  = _extract_onyomi(info, jo_yomis)
        kun_yomis = _extract_kunyomi(info, jo_yomis)
        tmp = {
            'title': info['title'],
            'wik_pageid': info['pageid'],
            'kyujitai': info['kyujitai'] if 'kyujitai' in info else '',
            'sokaku': int(info['sokaku']),
            'busyu' : info['busyu'],
            'busyu_kaku' : int(info['busyu_kaku']),
            'is_joyo' : int(info['joyo']),
            'edu_year': int(info['edu_year']),
            'joyo_yomis': joyo_yomis,
            'on_yomis': on_yomis,
            'kun_yomis': kun_yomis,
        }
        ret.append(tmp)

    #ret.sort(key=lambda x: x['sokaku'])
    ret.sort(key=lambda x: (-x['is_joyo'], x['edu_year'], x['sokaku']))
    hoge = [r['title'] for r in ret]
    print(''.join(hoge))
    return ret


def main():
    image_data_codes = fsutils.read_lines(ETLCDB_CHAR_CODES_FILE)
    ret = {code:{} for code in image_data_codes if char_utils.is_kanji_code(code)}
    print('{} kanjis found in data directory.'.format(len(ret)))
    ret = merge_joyo(ret)
    ret = merge_wiktionary(ret)

    ''' print kanjis not updated '''
    for code, info in ret.items():
        if not 'busyu' in info:
            c = chr(int(code, 16))
            print(c, code, info)
            raise Exception('wiktionary page not found for {}'.format(c))

    results = format_data(ret)
    fsutils.write_json(ret,     '{}/all_tmp.json'.format(OUTPUT_DIR))
    fsutils.write_json(results, '{}/all.json'.format(OUTPUT_DIR))
    fsutils.write_json(results, '{}/all_noindent.json'.format(OUTPUT_DIR), indent=None)


if __name__ == '__main__':
    main()
