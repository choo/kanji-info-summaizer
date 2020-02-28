import os, re
import fsutils
import char_utils
from pprint import pprint
from normalizer import Normalizer


KUN_EXCEPTION_PATH = './data/kun_exceptions.tsv'
ON_EXCEPTION_PATH = './data/on_exceptions.tsv'

def write_tsv(records, output_path):
    normalizer = Normalizer(hira_kata=True, kogaki_dakuon=True)
    ret = []
    check = []
    for rec in records:
        try:
            # [[Category:教育漢字 第1学年|せい]]
            joyo, joyo_yomi = _extract_joyo(rec)
            edu_year, edu_yomi = _extract_edu(rec, joyo)
            sokaku = _extract_sokaku(rec['sokaku'])
            busyu, busyu_kaku = _extract_busyu(rec['busyu'])
            jiscode = _extract_jiscode(rec)
            kuten = _extract_kuten(rec)

            ''' nai -> 常用漢字表内, gai -> 常用漢字表外, other -> それ以外 '''
            kunyomi_nai, kunyomi_gai, kunyomi_other = _extract_kunyomi(rec)
            onyomi_go, onyomi_kan, onyomi_other = _extract_onyomi(rec)
        except Exception as e:
            pass
            #pprint(rec)
            #print(e)

        if joyo_yomi and len(joyo_yomi) > 0:
            tmp = ','.join([onyomi_go, onyomi_kan, onyomi_other,
                kunyomi_nai, kunyomi_gai, kunyomi_other])
            tmp = normalizer.normalize(tmp)
            tmp = tmp.replace('-', '')
            for y in joyo_yomi + edu_yomi:
                y = normalizer.normalize(y)
                if not y in tmp:
                    ## TODO: FIX wiktionary
                    #print(rec['pageid'], rec['title'], y, tmp) # => yomi lacks
                    pass
                    break

        ret.append({
            'pageid': rec['pageid'], # https://ja.wiktionary.org/wiki/?curid={pageid}
            'title': rec['title'],
            'is_kanji': 1 if char_utils.is_kanji(rec['title'][0]) else 0,
            'joyo': joyo,
            'edu_year': edu_year,
            'sokaku': sokaku,
            'busyu' : busyu,
            'busyu_kaku': busyu_kaku,
            'joyo_yomi': ','.join(joyo_yomi + edu_yomi),
            'onyomi_go' : onyomi_go,
            'onyomi_kan': onyomi_kan,
            'onyomi_other': onyomi_other,
            'kunyomi_nai': kunyomi_nai,
            'kunyomi_gai': kunyomi_gai,
            'kunyomi_other': kunyomi_other,
            'jis': jiscode,
            'kuten': kuten,
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
    if rec['title'] == '磁':
        ''' wiktionary fixed '''
        return 1, []
    if not 'joyo_kanji' in rec:
        return 0, []
    tmp = re.search(r'常用漢字\|?(.*?)\]\]', rec['joyo_kanji']).group(1)
    yomis = [y for y in tmp.split(r' ') \
                if not y.startswith('2010年') and y != '{{PAGENAME}}']
    return  1, yomis


def _extract_edu(rec, is_joyo):
    if rec['title'] == '磁':
        ''' wiktionary fixed '''
        return 6, []
    if not 'edu_kanji' in rec:
        if is_joyo: # 常用漢字かつ非教育漢字は 7 とする
            return 7, []
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

def _extract_kuten(rec):
    if not 'kuten' in rec:
        return ''
    s = rec['kuten']
    ret, suffixes = ['', '', ''], ['面', '区', '点']
    for i in range(len(ret)):
        tmp = re.search(r'(\d+)' + suffixes[i], s)
        if tmp:
            ret[i] = tmp.group(1)
    #if ret[0] and 1 < int(ret[0]):
    #    ''' not １面 '''
    #    print(rec)
    #if ret[1] and 48 <= int(ret[1]) <= 83:
    #    ''' 第２水準漢字 '''
    #    print(rec)
    return ','.join(ret)


def _clean_yomi_info(s):
    ''' [[常用]][[漢字]] -> 常用漢字, [[常用漢字]] -> 常用漢字 '''
    #s = re.sub(r'\[\[常用\]\]\[\[漢字\]\]', '常用漢字', s)
    #s = re.sub(r'\[\[常用漢字\]\]', '常用漢字', s)
    s = s.replace('[[常用]][[漢字]]', '常用漢字')
    s = s.replace('[[常用漢字]]', '常用漢字')

    ''' "常用漢字表内の音読みはありません" は存在しない '''
    s = re.sub(r'常用漢字表内の訓読みはありません。', '', s)
    s = re.sub(r'（常用漢字表内）', '', s)
    s = re.sub(r'（常用漢字表外）', '', s)
    s = re.sub(r'[\*\:\s,：]', '', s) # *, :, \s, ',', '、'

    ''' 訓読み -> '', [[訓読み]] -> '', 音読み -> '', [[音読み]] -> '' '''
    s = s.replace('[[訓読み]]', '')
    s = s.replace('訓読み', '')
    s = s.replace('[[音読み]]', '')
    s = s.replace('音読み', '')

    return s


def _load_exception(filepath):
    rows = fsutils.read_csv(filepath)
    ret = {}
    for r in rows:
        if 'ok' in r and r['ok'] != '':
            ret[r['title']] = r['yomi'].split('、')
    return ret


def _extract_kunyomi(rec):
    exceptions = _load_exception(KUN_EXCEPTION_PATH)
    joyo_nai, joyo_gai, other = '', '', ''
    if not 'kunyomi' in rec:
        return joyo_nai, joyo_gai, other
    s = _clean_yomi_info(rec['kunyomi'])

    tmp = re.search(r'(.*?)(?:(?:常用漢字)?表内)(.*)', s)
    if tmp:
        ''' "常用漢字表内" にて a, b に分類するが a に読みが存在する例はない '''
        a, b = tmp.group(1), tmp.group(2)
        if re.search(r'\[\[(.+?)\]\]', a):
            if rec['title'] in exceptions:
                yomis = exceptions[rec['title']]
                ret['other'] += yomis
            else:
                pprint(rec)
                raise Exception(' error in extracting kunyomi')

        tmp = re.search(r'(.*?)(?:(?:常用漢字)?表外)(.*)', b)
        if tmp:
            ''' "常用漢字表外" にて group({1, 2}) に分類する '''
            joyo_nai = _extract_kun_link(tmp.group(1), rec, exceptions)
            joyo_gai = _extract_kun_link(tmp.group(2), rec, exceptions)
        else:
            ''' 「表内」の記載あり、かつ「表外」の記載なし '''
            joyo_nai = _extract_kun_link(b, rec, exceptions)
    else:
        ''' 「表内」の記載なし '''
        ''' TODO: 表内か表外か判別不可のため, 区別しないようにすべきか検討 '''
        ''' cf.) 25318 好 '''
        other = _extract_kun_link(s, rec, exceptions)
    return joyo_nai, joyo_gai, other


def _extract_kun_link(s, rec=None, exceptions={}):
    links, _ = _extract_link_text(s, rec, exceptions)
    ret = []
    for t in links:
        if not char_utils.contains_kanji(t):
            ret.append(t)
        if not char_utils.is_hiragana_word(t):
            ''' 漢字を含まない && ひらがな以外があるのはカタカナ語の訓読み '''
            pass
            #_debug_yomi(t, rec)
        if t.startswith('w'): 
            ''' [[w:...]] となっていて漢字を含まないのは ミサゴ だけ '''
            pass
            _debug_yomi(t, rec)
    return ','.join(ret)


def _extract_onyomi(rec=None):
    exceptions = _load_exception(ON_EXCEPTION_PATH)
    go, kan, other = '', '', '' # 呉音, 漢音, その他（唐音, 宋音, 唐宋音, 慣用音）
    if not 'onyomi' in rec:
        return go, kan, other
    s = _clean_yomi_info(rec['onyomi'])
    links, left = _extract_link_text(s, rec)
    ret = {'go': [], 'kan': [], 'other': []}
    key = 'other'
    for t in links:
        if t == '呉音':
            key = 'go'
        elif t == '漢音':
            key = 'kan'
        elif t.endswith('音'):
            key = 'other'
        else:
            if not char_utils.contains_kanji(t):
                ret[key].append(t)
                if not char_utils.is_katakana_word(t):
                    ''' 漢字を含まない && カタカナ以外が含まれるのはひらがなの音読み '''
                    ''' 訓読みなのに音読みの項目に書かれているものを抽出 '''
                    pass
                    #_debug_yomi(t, rec)
    if left:
        if rec['title'] in exceptions:
            #_debug_yomi(left, rec)
            yomis = exceptions[rec['title']]
            ret['other'] += yomis
    return (','.join(ret['go']),
            ','.join(ret['kan']),
            ','.join(ret['other']))


def _extract_link_text(s, rec, exceptions={}):
    ''' [[hoge]][[fuga]] -> ['hoge', 'fuga'] '''
    ret = []
    regex = re.compile(r'(\[\[(.+?)\]\])')
    while re.search(regex, s):
        tmp = re.search(regex, s)
        t = tmp.group(2)
        if t.find('|') >= 0:
            t = t[t.find('|') + 1:]
        ret.append(t)
        s = s.replace(tmp.group(1), '')
    if rec['title'] in exceptions:
        ret += exceptions[rec['title']]
    return ret, s # ''' s は [[]] に囲まれていない残骸 '''



def _debug_yomi(s, rec):
    e = ['－', '-', '―', '、', '（', '）', '\(', '\)', '表外', '表外漢字', '常用漢字表外', '無し']
    regex = re.compile('|'.join(e))
    if re.sub(regex, '', s) != '':
        elms = ['', rec['pageid'], rec['title'], s]
        print('\t'.join(elms))
        #print(rec['kunyomi'])

