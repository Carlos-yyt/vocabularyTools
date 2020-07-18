import os

from src import dictionaries
from src import database
from src import tag

# dictionaries.txt2excel(os.path.abspath(r'data\测试词库.txt'), os.path.abspath('audio'))
# database.create_dictionaries("Carlos", "我爱背单词", r'data\测试词库.txt')

tag.tag_file(r"data\testPassage.txt", r"data\Carlos_dictionary.db")
