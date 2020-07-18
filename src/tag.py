import sqlite3
import string
from nltk.stem import WordNetLemmatizer
import nltk
import logging

lemmatizer = WordNetLemmatizer()

from nltk.corpus import wordnet


def keep_first_translation(translation):
    """
    提取单词含义中的第一个意思作为解释
    :param translation:单词的完整释义
    :return: 单词的第一个释义
    """
    briefTranslation = ""
    for char in translation:
        if u'\u4e00' <= char <= u'\u9fff':  # 中文的范围
            briefTranslation = briefTranslation + char
        else:
            break
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


def tag_word(lowWord):
    """
    todo：增加统计信息
    各一个单词加注释，如果在生词库中的话
    :param lowWord: 带加注的单词
    :return: 处理后的结果
    """
    lowWord = lowWord.lower()  # 把所有单词中的大写字母转换成小写字母
    pos = get_wordnet_pos(nltk.pos_tag(lowWord)) or wordnet.NOUN  # 获取词性
    rootWord = lemmatizer.lemmatize(lowWord, pos)  # 词形还原

    sqlExec = """
    SELECT translation, IPA, audio
    FROM words
    WHERE word='%s'
    """ % rootWord


def tag_passage(passage, database_url):
    """
    根据指定的生词词库标注一段文本
    todo:增加功能，比如：生成单词表
    :param passage:待处理的文本
    :param database_url:指定的生词词库
    :return:返回标注后的文本。
    """

    '''连接数据库'''
    conn = sqlite3.connect(database_url)
    curs = conn.cursor()

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

                result = curs.execute(sqlExec)
                if len(list(result)) != 0:  # 查到了单词
                    # todo: 无法解析数据库返回的结果 2020年7月18日
                    for row in result:
                        translation = row[0]
                        print(translation)
                    print(result.fetchall())
                    newPassage += curWord + "(" + keep_first_translation(result.fetchall()[0][0]) + ")"
                else:
                    newPassage += curWord
            else:
                newPassage += curWord
        newPassage += "\n"

    return newPassage


def tag_file(file_url, database_url):
    with open(file_url, encoding='UTF-8') as file_object:
        passage = file_object.read()
        newPassage = tag_passage(passage, database_url)
    print(newPassage)
