import xlwt
import os


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
