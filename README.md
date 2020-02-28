
常用漢字について
================

- [常用漢字一覧](https://ja.wikipedia.org/wiki/%E5%B8%B8%E7%94%A8%E6%BC%A2%E5%AD%97%E4%B8%80%E8%A6%A7)
- 第一水準も含めた一覧は, [漢字辞典 > JIS第1水準の漢字](https://kanjitisiki.com/jis1/)


JIS X 0208 での漢字コード範囲
=============================

cf.)
- https://ja.wikipedia.org/wiki/JIS_X_0208
- http://www.shuiren.org/chuden/teach/code/main4.htm
- [JIS X 0208 コード表](http://www.asahi-net.or.jp/~ax2s-kmtn/ref/jisx0208.html)

2 byte(16 bit)
区: 上位 byte (hex 表記での上位 2 桁)
    0x21-- を 1区とし, 0x22-- を 2 区 ... とする
点: 下位 byte (hex 表記での下位 2 桁)

区も点も 21xx - 7Exx までの 94 個含まれる

* 01～08区
    - 0x2121 - 0x
    - 非漢字453字
        - ひらがな(4区), カタカナ(5区)
        - ラテン文字/数字(3区), ギリシャ文字(6区), キリル文字(7区)
        - 罫線素片(8区), 記号など
        - 1,2区 記号
        - 3区   英数字
        - 4区   ひらがな
        - 5区   カタカナ
        - 6区   ギリシア文字
        - 7区   キリル文字


* 16～47区
    - 0x3021 - 0x4F7E
        - 実際に登録されているのは 0x4F53 の '腕' まで
    - 「第1水準」漢字2,965字
    - 1946年に告示された「当用漢字表（法令・公用文書・新聞・雑誌および一般社会で、使用する漢字の範囲を示したもの）」1,850字と
      当時の「人名用漢字別表」120字を全て含んでいます。

* 48～83区
    - 「第2水準」漢字3,384字
    - 弌 など


Extract joyo kanji information from PDF
----------------------------------------

- [政府による公式の常用漢字表](https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/pdf/joyokanjihyo_20101130.pdf)

```
$ wget https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/pdf/joyokanjihyo_20101130.pdf -P ./data/official
$ pdftotext ./data/official/joyokanjihyo_20101130.pdf -f 11 -l 161 -nopgbrk -raw ./data/official/joyokanjihyo.txt
```

### postprocess
- correct indentation of first approx.) 20 characters


Wikitionary 解析
================

About Data
----------

- URLs
    - [wiktionary download page](https://dumps.wikimedia.org/jawiktionary/20200101/)
    - [latest files download directory](https://dumps.wikimedia.org/jawiktionary/latest/)
- pages-articles というファイルのもので本文も全て含まれる
    - `jawiktionary-latest-pages-articles.xml.bz2`

```
wget https://dumps.wikimedia.org/jawiktionary/latest/jawiktionary-latest-pages-articles.xml.bz2 -P ./data
bunzip2 data/jawiktionary-latest-pages-articles.xml.bz2
```

About Format
-------------

- wikipedia の書式
    [チートシート](https://colo-ri.jp/develop/archives/mediawiki_cheatsheet.pdf)


About libraries
----------------


### gensim_...

- マークアップ全ては parse してくれない


### mwparserfromhell

sample output for mwparserfromhell
```
['スタブ', '\n', 'DEFAULTSORT:', '\n', '漢字', '\n', 'span', 'lang', 'ja', 'xml:lang', 'ja', 'style', 'font-size:350%', 'PAGENAME', 'span', '\n', '部首', '水', '14', '\n', '総画', '17', '\n', '異体字', ': ', 'span', 'style', 'font-size:250%', '𤂳', 'span', '（', '同字', '）', '\n\n', '字源', '\n', '形声文字', '形声', '』。水+音符', '算', '。\n\n', '意義', '\n', '馬を洗う。\n', '飲む。舐める。\n', 'Category:漢字', '\n\n', 'jpn', '\n', 'Category:', 'jpn', '\n\n', 'pron', 'jpn', '\n', '音読み\n', 'サン\n', '訓読み\n', '洗う', 'あら-う', '\n\n', 'noun', '\n', 'Category:', 'jpn', ' ', 'noun', 'さん', '\n', '\n\n', 'prov', '\n', '熟語1', '\n\n', 'zho', '\n', 'Category:', 'zho', '??', '\n', 'trans_link', 'zh', 'PAGENAME', '\n', 'ローマ字表記', '\n', '普通話', '\n', 'ピンイン', ': \n', 'ウェード式', ': \n', '広東語', '\n', 'イェール式', ': \n', '閩南語', '\n', 'POJ', ': \n', 'pron', 'zho', '\n', '\n', 'file:', ' \n', 'noun', ' \n', 'Category:', 'zho', '_', 'noun', '??', '\n', '\n', 'prov', ' \n', '熟語2', '\n\n', 'kor', ' \n', 'Category:', 'kor', '??', '\n', 'kor-hanja', 'hangeul', '??', 'eumhun', '??', 'rv', '??', 'mr', '??', 'y', '??', '\n\n', '\n', 'prov', '\n\n', 'vie', '\n', 'Category:', 'vie', '??', '\n', 'trans_link', 'vi', 'PAGENAME', '\n', 'ローマ字表記', '\n', 'Quốc ngữ', ': ', '????', '\n\n', 'コード等', '\n', 'unicode_code\n', '16進 ', ' \n', '\n', 'JIS X 0208(-1978,1983,1990) \n', 'JIS', '\n', '16進: ????\n', 'Shift JIS', '\n', '16進: ????\n', '区点', ': ??区??点\n', 'JIS X 0213(2004) \n', 'JIS', '\n', '16進: ????\n', 'Shift JIS', '\n', '16進: ????\n', '区点', ': ??区??点\n', '四角号碼', ': ????', 'sub', '?', 'sub', '\n', '倉頡入力法', ': ????']
```





