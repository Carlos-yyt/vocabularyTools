import os

from src import dictionaries
from src import database

#dictionaries.txt2excel(os.path.abspath(r'data\测试词库.txt'), os.path.abspath('audio'))
database.create_dictionaries("Carlos", "我爱背单词", "file_url")
