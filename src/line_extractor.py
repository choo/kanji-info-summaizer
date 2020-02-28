#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

import os, re, time
import xml.etree.ElementTree as ET
import fsutils
from pprint import pprint

NAMESPACE = '{http://www.mediawiki.org/xml/export-0.10/}'

def write_tsv(input_filepath, output_file):
    '''
        get('hoge'):  getting the value with attribute 'hoge'
        find('fuga').text:  getting the content of tag whose name 'fuga'
    '''
    ret = []

    s = time.time()
    print('parsing xml file starts...')
    tree = ET.parse(input_filepath)
    print('took {} s'.format((time.time() - s))) # about 12 sec

    root = tree.getroot()
    print('{} page items found'.format(len(root))) # 259118 items as of 2020/01/14

    for cnt, page_elm in enumerate(root):
        pageid_tag   = page_elm.find(make_tagname('id'))
        title_tag    = page_elm.find(make_tagname('title'))
        revision_tag = page_elm.find(make_tagname('revision'))
        text_tag     = None
        if revision_tag:
            text_tag = revision_tag.find(make_tagname('text'))

        if (pageid_tag is None or title_tag is None or text_tag is None):
            continue

        pageid = str(pageid_tag.text)
        title  = str(title_tag.text)
        content_str = str(text_tag.text)

        #''' extracted_raw_lines.tsv に書き出されないページのダンプ '''
        #if title == '美':
        #    print(pageid, title)
        #    #pprint(content_str)

        if is_kanji_page(title, content_str):
            try:
                lines = [line.strip() for line in content_str.split('\n')]
                info  = _extract_info_lines(pageid, title, lines)
                ret.append(info)

                #if pageid == '13925': # 桜 (onyomi lacks)
                #if pageid == '188013':
                #    pprint(lines)

                #lines = [line.strip() for line in content_str.split('\n')]
                #for i, line in enumerate(lines):
                #    if '** 音読み' in line:
                #        print(pageid, title, '\n'.join(lines[i - 1:i + 1]), '\n')
            except Exception as e:
                print(' ---------- some error ------ ')
                print(pageid, title, e)
                print(' ---------- some error ------ ')
        else:
            #_debug_content()
            pass

    print(len(ret))
    if len(ret) > 0:
        fsutils.write_csv(ret, output_file)
        print(' WRITTEN !!!!!!!!!!!')
    return ret


def make_tagname(name):
    ''' '{http://www.mediawiki.org/xml/export-0.10/}title' '''
    return '{}{}'.format(NAMESPACE, name)


def is_kanji_page(title, content):
    return (title.find('テンプレート') < 0 and
            re.search(r'==\s?(?:\[\[)?漢字(?:\]\])?\s?==', content))
            #re.search(r'\[\[Category\:漢字\]\]', content))



####################################
###   extraction logic
####################################

def _extract_info_lines(pageid, title, lines):
    ret = {
        'pageid': pageid, # https://ja.wiktionary.org/wiki/?curid={pageid}
        'title': title,
        'busyu': _extract_busyu(lines),
        'sokaku': _extract_sokaku(lines),
        'edu_kanji': _extract_kanji_cat(lines, '教育漢字'),
        'joyo_kanji': _extract_kanji_cat(lines, '常用漢字'),
        'onyomi': _extract_yomi(pageid, title, lines, '音読み'),
        'kunyomi': _extract_yomi(pageid, title, lines, '訓読み'),
        #'unicode': '', # unicode のデータはない場合がほとんど (1000 / 7000 文字くらい)
        'jiscode': _extract_jis(lines),
        'kuten': _extract_kuten(lines),
    }
    return ret


def _extract_busyu(lines):
    ret = None
    for l in lines:
        if re.match(r'\*\s?(?:\{\{|\[\[)部首', l) and not '（越南𡨸喃）' in l:
            ''' * {{部首, *[[部首 '''
            if ret is not None:
                print('\n'.join([' ********************* ', ret, l]))
                raise Exception("there's already {} ".format('部首'))
            ret = l
    return ret


def _extract_sokaku(lines):
    ret = None
    for l in lines:
        if ((re.match(r'\*\s?(?:\{\{|\[\[)総画', l) and
                not '（中国・韓国）' in l and l != '*[[総画]]') or
                re.match(r'┃\{\{総画', l)):
            if ret is not None:
                print('\n'.join([' ********************* ', ret, l]))
                raise Exception("there's already {} ".format('総画'))
            ret = l
    return ret


def _extract_kanji_cat(lines, category):
    ''' [[Category:教育漢字 第2学年|けい]] '''
    ''' [[Category:常用漢字|きよく きょく]]'''
    def _is_category(line):
        return re.match(r'\[\[(?:category|Category|カテゴリ)', line)
        #return 'category' in line or 'Category' in line
    ret = None
    for l in lines:
        if _is_category(l) and category in l:
            if ret is not None:
                if '2010年追加' in l:
                    ret += '2010年追加'
                else:
                    print(ret, l)
                    print(' ********************* ')
                    raise Exception("there's already {} ".format(category))
            ret = l
    return ret


def _extract_yomi(pageid, title, lines, yomi):
    ''' '音読', '訓読' と送り仮名なし表記は見出しとしては存在しない '''
    ret = None
    s = -1
    for i, l in enumerate(lines):
        if s < 0 and (re.match(r'\*\*?\s?(?:\[\[)?' + yomi, l)):
            if ret is not None:
                if pageid == '13094' or pageid == '14935':
                    ''' 13094:生(訓読み表外)、14935:糸(旧字体の訓読み) は '''
                    ''' 2番目のものは ignore '''
                    continue
                print('\n'.join([' ********************* ', ret, l]))
                raise Exception("there's already {} ".format(yomi))
            s = i
        elif s >= 0 and (not l or re.match(r'==', l) or
                         not re.match(r'\*[\*\:]', l)):
            ''' 空行か == 始まりか (** か *: か :[[)始まりでなければ終わり  '''
            ret = ','.join(lines[s:i])
            s = -1
    if s > 0 and ret is None:
        ret = ','.join(lines[s:])
    return ret


def _extract_jis(lines):
    ret = None
    for i, l in enumerate(lines):
        if '[[JIS]]' in l:
            ''' 2箇所以上に該当するのは JIS X 0208 と JIS X 0213 がある場合で, '''
            ''' その場合は JIS X 0213 を優先する '''
            ret = l + lines[i + 1]

    if ret is None: # "* JIS:... " となっている page もある
        for i, l in enumerate(lines):
            if re.match(r'\*\s(?:\'*?)JIS(?:\'*?)[\:：]', l):
                if ret is not None:
                    pprint(lines)
                    print(' ********************* ')
                    raise Exception("there's already {} ".format('jis'))
                ret = l + lines[i + 1]
    return ret


def _extract_kuten(lines):
    ret = None
    for i, l in enumerate(lines):
        if '[[区点]]' in l or l.startswith('** 区点'):
            ''' 2箇所以上に該当するのは JIS X 0208 と JIS X 0213 がある場合で, '''
            ''' その場合は JIS X 0213 を優先する '''
            ret = l
    return ret


def _debug_content(title, content_str):
    print(' *********************************** ' )
    print(title)
    pprint(content_str)
    print(title)
    print(' *********************************** ' )
    print()

