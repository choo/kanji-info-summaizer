import os, re
import fsutils
from pprint import pprint

def write_tsv(records, output_path):
    ret = []
    check = []
    for rec in records:
        try:
            joyo, joyo_yomi = _extract_joyo(rec)
            edu_year, edu_yomi = _extract_edu(rec)
            sokaku = _extract_sokaku(rec['sokaku'])
            busyu, busyu_kaku = _extract_busyu(rec['busyu'])
            jiscode = _extract_jiscode(rec)
        except Exception as e:
            pass
            #pprint(rec)
            #print(e)

        kunyomi_nai, kunyomi_gai = _extract_kunyomi(rec)
        if 'onyomi' in rec:
            check.append(rec['onyomi'])

        ret.append({
            'pageid': rec['pageid'],
            'title': rec['title'],
            'joyo': joyo,
            'edu_year': edu_year,
            'sokaku': sokaku,
            'busyu' : busyu,
            'busyu_kaku': busyu_kaku,
            'yomi': ','.join(joyo_yomi + edu_yomi), # FIXME: remove {{PAGENAME}}
            'jis': jiscode,
            'kunyomi_nai': kunyomi_nai,
            'kunyomi_gai': kunyomi_gai,
        })
        if joyo == 0 and edu_year > 0:
            pprint(rec)

        #char_code = hex(ord(kanji))
        #fsutils.write_file(content, '{}/{}.txt'.format('check', char_code))


    #check = sorted(list(set(check)))
    #pprint(check)

    fsutils.write_csv(ret, output_path)
    print(' ********* COMPLETED ********* ')
    return ret


def _extract_joyo(rec):
    if not 'joyo_kanji' in rec:
        return 0, []
    tmp = re.search(r'常用漢字\|?(.*?)\]\]', rec['joyo_kanji']).group(1)
    yomi = []
    if not '2010年追加' in tmp:
        yomi = tmp.split(r' ')
    return  1, yomi


def _extract_edu(rec):
    if not 'edu_kanji' in rec:
        return 0, []
    edu_year = int(re.search(r'第(\d)学年', rec['edu_kanji']).group(1))
    tmp = re.search(r'学年\|?(.*?)\]\]', rec['edu_kanji']).group(1)
    yomi = tmp.split(r' ')
    return edu_year, yomi


def _extract_sokaku(s):
    matched = re.search(r'総画\|(\d+)', s)
    if matched:
        ret = matched.group(1)
    else:
        ''' *[[総画]] : [[Wiktionary:漢字総画索引_20画|20画]] '''
        ret = re.search(r'漢字総画索引_(\d+)画', s).group(1)
    return ret


def _extract_busyu(s):
    ''' '*{{部首|鳥|0}}', '''
    matched = re.search(r'{{部首\|(.+?)\}\}', s)
    if matched:
        tmp = matched.group(1).split('|')
        busyu= tmp[0]
        busyu_kaku = tmp[1]
    else:
        ''' *[[部首]] : [[Wiktionary:漢字索引 部首 香|香]] + 11画 '''
        busyu = re.search(r'部首\s(.+?)\|', s).group(1)
        busyu_kaku = re.search(r'\+\s(\d+)画', s).group(1)
    return busyu, busyu_kaku


def _extract_jiscode(rec):
    '''
    jiscode が欠けている常用漢字
     {'pageid': '968', 'title': '根'}
     {'pageid': '972', 'title': '胃'}
     {'pageid': '30567', 'title': '列'}
    '''
    if not 'jiscode' in rec:
        return ''
    s = rec['jiscode']
    ret = ''
    matched = re.search(r'16進(?:.+)([a-zA-Z0-9\?\*]{4})', s)
    if matched:
        ''' ** [[JIS]]*** 16進：6157 '''
        ''' * JIS:** 16進:3960 '''
        ret = matched.group(1)
    else:
        matched = re.search(r'\[\[JIS\]\]:\s([a-zA-Z0-9\?\*]{4})', s)
        if matched:
            ret = matched.group(1)
        else:
            pass
            #print(s)
    return ret


'''
32978 騰
* 訓読み,** 常用漢字表内,**: 常用漢字表内の訓読みはありません。,** 常用漢字表内,**: [[あげる|あ-げる]]、[[あがる|あ-がる]]
常用漢字表内 
'''
def _extract_kunyomi(rec):
    '''
    '* 訓読み,** [[およぶ]]、[[こえる]]、すばしこ・い',
    '* 訓読み,** かすがい、こえ',
    '''
    if not 'kunyomi' in rec:
        return '', ''
    s = rec['kunyomi']

    ''' [[常用]][[漢字]] -> 常用漢字, [[常用漢字]] -> 常用漢字 '''
    #s = re.sub(r'\[\[常用\]\]\[\[漢字\]\]', '常用漢字', s)
    #s = re.sub(r'\[\[常用漢字\]\]', '常用漢字', s)
    s = s.replace('[[常用]][[漢字]]', '常用漢字')
    s = s.replace('[[常用漢字]]', '常用漢字')

    s = re.sub(r'常用漢字表内の訓読みはありません。', '', s)
    s = re.sub(r'[\*\:\s,、：]', '', s) # *, :, \s, ',', '、'

    ''' 訓読み -> '', [[訓読み]] -> '' '''
    s = s.replace('[[訓読み]]', '')
    s = s.replace('訓読み', '')

    tmp = re.search(r'(.*?)(?:(?:常用漢字)?表内)(.*)', s)
    if tmp:
        ''' "常用漢字表内" にて suffix と b に分類する '''
        ''' "常用漢字表内" 以前に読みと思われるものが存在する例はない '''
        suffix, b = tmp.group(1), tmp.group(2)
        if re.search(r'\[\[(.+?)\]\]', suffix):
            pprint(rec)
            print(suffix)
            raise Exception(' error in extracting kunyomi')

        #print(b)
        tmp = re.search(r'(.*?)(?:(?:常用漢字)?表外)(.*)', b)
        if tmp:
            ''' "常用漢字表外" にて group({1, 2}) に分類する '''
            #print(len(tmp.groups()))
            joyo_nai = _split(tmp.group(1), rec)
            joyo_gai = _split(tmp.group(2), rec)
        else:
            ''' 「表内」の記載あり、かつ「表外」の記載なし '''
            pass
            #nai = tmp.group(1)
            #joyo_nai = _split(b)
            joyo_nai = _split(b, rec)
            joyo_gai = ''
    else:
        ''' 「表内」の記載なし '''
        ''' TODO: 表内か表外か判別不可のため, 区別しないようにすべきか検討 '''
        ''' cf.) 25318 好 '''
        joyo_nai = ''
        joyo_gai = _split(s, rec)
        if (joyo_gai == '' and
                rec['kunyomi'] != '*訓読み'  and
                rec['kunyomi'] != '* 訓読み' and
                (not s in ['-', '', 'なし', '無し'])):
            pass
            #_debug_yomi(s, rec)
    return joyo_nai, joyo_gai


def _split(yomi, rec=None):
    '''
        TODO: [[w:徳川慶喜|...]] を削除. 下記両方
            - 漢字や英数字があるものを削除する
            - [[w: ... を削除する
    '''
    s = yomi
    ret = []
    regex = re.compile(r'(\[\[(.+?)\]\])')
    while re.search(regex, s):
        tmp = re.search(regex, s)
        t = tmp.group(2)
        if t.find('|') >= 0:
            t = t[t.find('|') + 1:]
        ret.append(t)
        s = s.replace(tmp.group(1), '')
    if s:
        ''' [[]] に囲まれていないもの. そんなに数はないし、ほぼ表外 '''
        if not s in ['人名読み', ]:
            pass
            #_debug_yomi(s, rec)
    return ','.join(ret)


def _debug_yomi(s, rec):
    print(rec['pageid'], rec['title'])
    print(rec['kunyomi'])
    print(s, '\n')


