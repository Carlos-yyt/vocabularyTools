import os

from src import dictionaries

dictionaries.txt2excel(os.path.abspath(r'data\测试词库.txt'), os.path.abspath('audio'))
