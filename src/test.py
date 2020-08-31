from src import tag

passage_url = r"D:\OneDrive\留学英语\标注生词软件\2020年8月29日.txt"
# database.create_dictionaries("Carlos", "我爱背单词", r'data\测试词库.txt', r'H:\Code\GitHub\vocabularyTools\src\audio')  # 导入词库
tag.tag_file(passage_url, r"data\Carlos_dictionary.db")  # 标记文章

