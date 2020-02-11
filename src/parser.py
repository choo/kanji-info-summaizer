#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

import os, re
import fsutils
from pprint import pprint
import line_extractor, info_extractor


INPUT_FILEPATH = '../data/jawiktionary-latest-pages-articles.xml'
MIDDLE_RESULT = '../data/extrated_raw_lines.tsv'
RESULT_PATH = '../data/extrated.tsv'

FORCE_EXTRACT_LINE = False
#FORCE_EXTRACT_LINE = True


def get_flatten_kanji_list():
    json_content = fsutils.read_json('../data/kanji_elm_school.json')
    ret = []
    for kanjis in json_content:
        for k in kanjis:
            ret.append(k)
    return ret


def check_data(results):
    kanjis = fsutils.read_json('../data/kanji_elm_school.json')
    joyo_count = 0
    edu_kanjis = [[] for _ in range(6)]
    for rec in results:
        if rec['joyo'] > 0:
            joyo_count += 1
        if rec['edu_year'] > 0:
            edu_kanjis[rec['edu_year'] - 1].append(rec['title'])

    print(' JOYO: {}'.format(joyo_count))
    #pprint(edu_kanjis)

    for i in range(6):
        lacks, extras = _check_lack_extras(kanjis[i], edu_kanjis[i])
        print(' ------- {} --------- '.format(i))
        print(sorted(lacks), sorted(extras))
        print('{} / {}'.format(len(edu_kanjis[i]), len(kanjis[i])))
        print()


def _check_lack_extras(a, b):
    lacks = []
    for v in a:
        if not v in b:
            lacks.append(v)
    extras = []
    for v in b:
        if not v in a:
            extras.append(v)
    return lacks, extras



if __name__ == '__main__':
    if FORCE_EXTRACT_LINE or not os.path.exists(MIDDLE_RESULT):
        line_extractor.write_tsv(INPUT_FILEPATH, MIDDLE_RESULT)
    extracted = fsutils.read_csv(MIDDLE_RESULT)
    results = info_extractor.write_tsv(extracted, RESULT_PATH)

    check_data(results)

