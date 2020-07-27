import os
import sqlite3
import string
from nltk.stem import WordNetLemmatizer
import nltk
import logging
import re

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

    # briefTranslation = ""
    # for char in translation:
    #     if u'\u4e00' <= char <= u'\u9fff':  # 中文的范围
    #         briefTranslation = briefTranslation + char
    #     else:
    #         break
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
    todo:将查表改成事先读入缓存
    :param passage:待处理的文本
    :param database_url:指定的生词词库
    :return:返回标注后的文本。
    """

    '''连接数据库'''
    disk_db = sqlite3.connect(database_url)
    mem_db = sqlite3.connect(':memory:')
    mem_db.executescript("".join(line for line in disk_db.iterdump()))  # 把数据库内容从磁盘转到内存

    mem_db.row_factory = dict_factory
    curs = mem_db.cursor()

    newPassage = ""
    paragraphs = passage.split('\n')  # 将文章分割成段落
    for curPara in paragraphs:
        words = nltk.word_tokenize(curPara)  # 将段落分割成单词
        for curWord in words:
            if curWord not in string.punctuation:  # 如果不是标点符号
                lowWord = curWord.lower()  # 把所有单词中的大写字母转换成小写字母
                pos = get_wordnet_pos(nltk.pos_tag(lowWord)[0][1]) or wordnet.NOUN  # 获取词性
                rootWord = lemmatizer.lemmatize(lowWord, pos)  # 词形还原

                sqlExec = """
                    SELECT translation, IPA, audio
                    FROM words
                    WHERE word='%s'
                    """ % rootWord

                cursor = curs.execute(sqlExec)
                resultDict = cursor.fetchone()
                if resultDict is not None:  # 查到了单词
                    newPassage += curWord + "(" + keep_first_translation(resultDict['translation']) + ")" + " "
                else:
                    newPassage += curWord + " "
            else:
                newPassage.rstrip()  # 删除末尾的空格
                newPassage += curWord + " "  # 标点符号
        newPassage += "\n"  # 复原的时候加上回车符

    return newPassage


def tag_file(file_url, database_url):
    """
    对文本文件进行标记
    :param file_url:文件路径
    :param database_url: 生词数据库路径
    :return: 返回一个标注好的txt文件
    """
    with open(file_url, encoding='UTF-8') as file_object:
        passage = file_object.read()
        newPassage = tag_passage(passage, database_url)
    path, temp_filename = os.path.split(file_url)
    new_filename, extension = os.path.splitext(temp_filename)
    new_file_url = path + '\\' + new_filename + '_标注版.txt'
    logging.debug("new_file_url")
    logging.debug(new_file_url)
    print(new_file_url)

    with open(new_file_url, 'w', encoding='UTF-8') as new_file:
        newPassage += '\n'
        new_file.write(newPassage)
    print(newPassage)
