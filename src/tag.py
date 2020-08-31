import os
import sqlite3
import string
import xlwt
from nltk.stem import WordNetLemmatizer
import nltk
import logging
import re
import src.dictionaries

china = re.compile(r'[\u4e00-\u9fa5]+')  # 匹配连续中文

logging.basicConfig(level=logging.NOTSET)
lemmatizer = WordNetLemmatizer()

from nltk.corpus import wordnet


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def keep_first_translation(translation):
    """
    提取单词含义中的第一个意思作为解释
    :param translation:单词的完整释义
    :return: 单词的第一个释义
    """
    briefTranslation = china.findall(translation)[0]  # 默认取第一个解释
    return briefTranslation


def get_wordnet_pos(tag):
    """
    把NLTK标注出的词性（POS Tag）转化成NLTK词形还原（Lemmatization）所需格式
    :param tag:NLTK标注出的词性
    :return:LTK词形还原（Lemmatization）时所需的参数
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def tag_passage(passage, database_url):
    """
    根据指定的生词词库标注一段文本
    todo:增加功能，比如：生成单词表、
    :param passage:待处理的文本
    :param database_url:指定的生词词库
    :return:返回标注后的文本、生词表（每一行包括：单词、释义、音标、音频地址）。
    """

    '''连接数据库'''
    disk_db = sqlite3.connect(database_url)
    mem_db = sqlite3.connect(':memory:')
    mem_db.executescript("".join(line for line in disk_db.iterdump()))  # 把数据库内容从磁盘转到内存

    mem_db.row_factory = dict_factory
    curs = mem_db.cursor()

    newPassage = ""
    wordList_pure = []  # 一词一行的纯单词表，用于导入其他软件。
    wordList_learn = []  # 每一行包括：单词、释义、音标，用于直接学习。
    paragraphs = passage.split('\n')  # 将文章分割成段落
    for curPara in paragraphs:
        words = nltk.word_tokenize(curPara)  # 将段落分割成单词
        for curWord in words:
            if curWord[0] not in string.punctuation:  # 如果第一个不是标点符号。为什么是第一个：it's会被拆分成it和's，其中's应该忽略。
                lowWord = curWord.lower()  # 把所有单词中的大写字母转换成小写字母
                pos = get_wordnet_pos(nltk.pos_tag(lowWord)[0][1]) or wordnet.NOUN  # 获取词性
                rootWord = lemmatizer.lemmatize(lowWord, pos)  # 词形还原

                sqlExec = """
                    SELECT translation, IPA, audio, audio
                    FROM words
                    WHERE word='%s'
                    """ % rootWord

                cursor = curs.execute(sqlExec)
                resultDict = cursor.fetchone()
                if resultDict is not None:  # 查到了单词
                    if rootWord not in wordList_pure:  # 第一次出现的生词
                        wordList_pure.append(rootWord)
                        wordList_learn_line = [rootWord, resultDict['translation'], resultDict['IPA'],
                                               resultDict['audio']]
                        wordList_learn.append(wordList_learn_line)  # 包括：单词、释义、音标、音频地址，用于直接学习。
                    newPassage += curWord + "(" + keep_first_translation(resultDict['translation']) + ")" + " "
                else:
                    newPassage += curWord + " "
            else:
                newPassage.rstrip()  # 删除末尾的空格
                newPassage += curWord + " "  # 标点符号
        newPassage += "\n"  # 复原的时候加上回车符

    return newPassage, wordList_learn


def tag_file(file_url, database_url):
    """
    对文本文件进行标记
    :param file_url:文件路径
    :param database_url: 生词数据库路径
    :return: 返回一个标注好的txt文件
    """
    with open(file_url, encoding='UTF-8') as file_object:
        passage = file_object.read()
        newPassage, wordList = tag_passage(passage, database_url)  # newPassage为新标注好的文章、wordList为单词表（单词、释义、音标、音频地址）
    path, temp_filename = os.path.split(file_url)
    new_filename, extension = os.path.splitext(temp_filename)

    # 为每一个待翻译的文章建立文件夹
    path = path.strip()
    path = path.rstrip("\\")
    path = path + "\\" + new_filename
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

    print(path)
    new_passage_url = path + '\\' + new_filename + '_标注版.txt'
    new_wordList_url = path + '\\' + new_filename + '_纯单词表.txt'
    new_wordList_learn_url = path + '\\' + new_filename + '_可点读的单词表.xls'
    new_wordList_print_url = path + '\\' + new_filename + '_可打印学习的单词表.txt'
    new_wordList_youdao_url = path + '\\' + new_filename + '_可以导入有道词典.xml'
    logging.debug("new_file_url")
    logging.debug(new_passage_url)

    # 生成标注的文章
    with open(new_passage_url, 'w', encoding='UTF-8') as new_file:
        newPassage += '\n'
        new_file.write(newPassage)

    # 生成纯单词表
    with open(new_wordList_url, 'w', encoding='UTF-8') as new_file:
        for word in wordList:
            new_file.write(word[0] + '\n')  # 只写单词

    # 生成点读的单词表
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 创建工作簿
    sheet = book.add_sheet('单词页', cell_overwrite_ok=True)  # 创建数据表
    sheet.col(1).width = 256 * 20
    for i in range(0, len(wordList)):
        sheet.write(i, 0, xlwt.Formula(
            'HYPERLINK("%s";"%s")' % (wordList[i][3], wordList[i][0])))  # 第一列：显示单词，点击的时候跳转音频文件的超链接。
        sheet.write(i, 1, wordList[i][1])  # 第二列：释义
        sheet.write(i, 2, wordList[i][2])  # 第三列：音标
    book.save(new_wordList_learn_url)

    # 生成可打印学习的单词表
    with open(new_wordList_print_url, 'w', encoding='UTF-8') as new_file:
        for word in wordList:
            new_file.write('{:20s}{:20s}{}'.format(word[0], word[1], " " * (25 - len(word[1])) + word[2] + '\n'))

    # 生成可以导入有道词典的XML文件
    with open(new_wordList_youdao_url, 'w', encoding='utf-8') as new_file:
        src.dictionaries.wordList_2_YouDao(wordList, new_wordList_youdao_url, "know", "1")


def tag_files_and_mer(dir_url, database_url):
    pass
