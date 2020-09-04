import chardet

from src import tag
from src import dictionaries

passage_url = r"H:\Code\GitHub\vocabularyTools\src\data\2020年8月29日.txt"

dictionaries.merge_txt(r"D:\OneDrive\留学英语\00=TOEFL\01=阅读\00=TPO-阅读-原文-[40~52]")
# database.create_dictionaries("Carlos", "我爱背单词", r'data\测试词库.txt', r'H:\Code\GitHub\vocabularyTools\src\audio')  # 导入词库
tag.tag_file(passage_url, r"data\Carlos_dictionary.db")  # 标记文章
