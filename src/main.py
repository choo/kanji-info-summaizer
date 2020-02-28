#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

import official_pdf_analyzer, parser, merger

def main():
    official_pdf_analyzer.main()
    parser.main()
    merger.main()

if __name__ == '__main__':
    main()
