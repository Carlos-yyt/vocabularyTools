import chardet
import xlwt
import os
from xml.dom import minidom
import logging

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


def txt2excel(file_path, audio_path):
    """
    将指定的词库（不认识的单词）转化为统一格式。
    todo:支持多种格式的来源，目前支持的格式为：每词三行，单词音标中文各占一行每词三行，单词音标中文各占一行。
    :param file_path:带解析的单词文件
    :param audio_path:音频库
    :return:生成excel形式的单词表
    """
    path, temp_file_name = os.path.split(file_path)  # 分离文件名与扩展名
    filename, extension = os.path.splitext(temp_file_name)
    input_file_url = file_path
    output_file_url = path + '\\' + filename + '.xls'

    """逐行读入"""
    with open(input_file_url, encoding='utf-8'
              ) as file_object:
        lines = []
        for line in file_object:  # 逐行读取
            lines.append(line)

    """写excel"""
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 创建工作簿
    sheet = book.add_sheet('单词页', cell_overwrite_ok=True)  # 创建数据表
    word_sum = int(len(lines) / 3)  # 目前支持的格式为：每词三行，单词音标中文各占一行每词三行，单词音标中文各占一行。
    for i in range(0, word_sum):
        sheet.write(i, 0, lines[i * 3])  # 第一列：单词
        sheet.write(i, 1, lines[i * 3 + 1])  # 第二列：音标
        sheet.write(i, 2, lines[i * 3 + 2])  # 第三列：释义
        sheet.write(i, 3, keep_first_translation(lines[i * 3 + 2]))  # 第四列：简明释义
        sheet.write(i, 4, audio_path + lines[i * 3] + '.mp3')  # 第五列：单词音频文件位置
    book.save(output_file_url)


def wordList_2_YouDao(wordList, file_url, tag, progress):
    """
    根据wordList生成可以导入有道词典的XML文件
    TODO:生成的XML要手动把编码改成utf-8
    :param wordList: 单词表
    :param file_url: 生成的XML文件的地址
    :param tag: 该组单词的分类
    :param progress: 复习进度（默认为1）
    :return:在file_url指定的位置生成一个可以导入有道词典的XML文件
    """
    domTree = minidom.Document()
    # 文档根元素
    rootNode = domTree
    # 新建一个wordbook节点
    wordbook_node = domTree.createElement("wordbook")

    for word in wordList:
        # 创建item节点
        item_node = domTree.createElement("item")
        wordbook_node.appendChild(item_node)

        # 创建word节点,并设置textValue
        word_node = domTree.createElement("word")
        phone_text_value = domTree.createTextNode(word[0].encode('unicode_escape').decode('utf-8'))
        word_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        item_node.appendChild(word_node)

        # 创建trans节点,并设置textValue
        word_node = domTree.createElement("trans")
        # phone_text_value = domTree.createCDATASection(word[1].encode('unicode_escape').decode('utf-8'))
        phone_text_value = domTree.createCDATASection(word[1])
        print(chardet.detect(str.encode(word[1])))
        word_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        item_node.appendChild(word_node)

        # # 创建phonetic节点,并设置textValue
        # word_node = domTree.createElement("phonetic")
        # phone_text_value = domTree.createCDATASection(word[2].encode('unicode_escape').decode('utf-8'))
        # word_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        # item_node.appendChild(word_node)

        # 创建tags节点,并设置textValue
        word_node = domTree.createElement("tags")
        phone_text_value = domTree.createTextNode(tag.encode('unicode_escape').decode('utf-8'))
        word_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        item_node.appendChild(word_node)

        # # 创建progress节点,并设置textValue
        # word_node = domTree.createElement("progress")
        # print(progress,chardet.detect(str.encode(progress.encode('unicode_escape').decode('utf-8'))))
        # phone_text_value = domTree.createTextNode(progress.encode('unicode_escape').decode('utf-8'))
        # word_node.appendChild(phone_text_value)  # 把文本节点挂到name_node节点
        # item_node.appendChild(word_node)

    rootNode.appendChild(wordbook_node)

    with open(file_url, 'w') as f:
        # 缩进 - 换行 - 编码
        domTree.writexml(f, indent='\t', addindent='\t', newl='\n', encoding='utf-8')


def merge_txt(dir_path):
    """
    合并指定文件夹下的所有txt文件
    :param dir_path:指定的文件夹路径
    :return:生成一个txt文件
    """
    res_url = dir_path + "/" + os.path.split(dir_path)[1] + "_all.txt"  # 用最后一个文件夹的名字命名生成的文件
    res_file = open(res_url, "w", encoding='utf-8')
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for file in files:
            res_file.writelines("===The following comes from file < " + file + ' > ===\n\n')
            logging.debug("Copying file "+os.path.join(root, file))
            for line in open(os.path.join(root, file), encoding='utf-8'):
                res_file.writelines(line)
            logging.debug("Copying finished.")
            res_file.writelines("\n\nFile < " + file + ' > ends.\n\n')
    res_file.close()