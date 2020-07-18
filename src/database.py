import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)


def create_dictionaries(dictionary_name, src_type, src_file_url):
    """
    根据用户提供的单词表创建一个该用户的生词表
    todo:支持多种格式的来源，目前支持的格式为：每词三行，单词音标中文各占一行每词三行，单词音标中文各占一行。
    :param dictionary_name:用户的名称
    :param src_type:用户提供的单词表的类型
    :param src_file_url:用户提供的单词表的文件位置
    :return:生成一个.db文件
    """
    database_name = './data/' + dictionary_name + '_dictionary.db'
    conn = sqlite3.connect(database_name)
    curs = conn.cursor()

    """
    数据库建表，
    基础4项：单词、释义、国际音标、音频文件地址
    拓展：遇到的次数、
    """
    sql_exec = '''
    CREATE TABLE IF NOT EXISTS words(
    word    TEXT    PRIMARY KEY,
    translation  TEXT,
    IPA VARCHAR(255),
    audio   VARCHAR(255),
    times   INT
    )
    '''
    curs.execute(sql_exec)

    """逐行导入数据库"""
    with open(src_file_url, encoding='utf-8') as file_object:
        for index, line in enumerate(file_object):  # 逐行读取
            if index % 3 == 0:
                _word = line.strip('\n')  # 第一列：单词
                logging.debug(_word)
            elif index % 3 == 1:
                _translation = line.strip('\n')  # 第二列：释义
                logging.debug(_translation)
            else:
                _ipa = line.strip('\n')  # 第三列：国际音标
                logging.debug(_ipa)
                _audio = './audio/' + _word + '.mp3'  # 第四列：音频文件地址
                logging.debug(_audio)
                sql_exec = "INSERT OR IGNORE INTO words VALUES (?,?,?,?,?)"  # ignore:防止用户提供的题库有重复单词
                curs.execute(sql_exec, (_word, _translation, _ipa, _audio, 0))  # 遇到的次数 初始为0

    conn.commit()
    conn.close()
