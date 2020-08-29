from src import database
from src import tag
import nltk


database.create_dictionaries("Carlos", "我爱背单词", r'data\测试词库.txt',r'H:\Code\GitHub\vocabularyTools\src\audio')  # 导入词库
tag.tag_file(r"data\2020年8月29日.txt", r"data\Carlos_dictionary.db")  # 标记文章
