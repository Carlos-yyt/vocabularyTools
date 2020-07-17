import sqlite3


def create_dictionaries(user_name, src_type, src_file_url):
    """
    根据用户提供的单词表创建一个该用户的生词表
    :param user_name:用户的名称
    :param src_type:用户提供的单词表的类型
    :param src_file_url:用户提供的单词表的文件位置
    :return:生成一个.db文件
    """
    database_name = './data/' + user_name + '_dictionary.db'
    conn = sqlite3.connect(database_name)
    curs = conn.cursor()

    """
    数据库建表，
    基础4项：单词、释义、国际音标、音频文件地址
    拓展：遇到的次数、
    """
    sql_exec = '''
    CREATE TABLE words(
    word    TEXT    PRIMARY KEY,
    translation  TEXT,
    IPA VARCHAR(255),
    audio   VARCHAR(255),
    times   INT
    )
    '''
    curs.execute(sql_exec)
    conn.commit()
    conn.close()
