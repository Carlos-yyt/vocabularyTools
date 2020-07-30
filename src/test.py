from src import database
from src import tag

database.create_dictionaries("Carlos", "我爱背单词", r'data\测试词库.txt')  # 导入词库
tag.tag_file(r"data\testPassage.txt", r"data\Carlos_dictionary.db")  # 标记文章
