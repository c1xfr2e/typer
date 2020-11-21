# coding: utf-8

# 不可使用 PIL 及 Python 标准库以外的第三方库
from types import FunctionType
from PIL import Image, ImageFont, ImageDraw


def is_chinese(c):
    return u'\u4e00' <= c <= u'\u9fff'


# 备用字体的最小、最大字号
MIN_FONT_SIZE = 5
MAX_FONT_SIZE = 100


# 分词
def tokenize(str):
    return [s for s in str]


# 验证使用 font 字体能否在长 max_width, 高 max_height 的矩形内绘制 text
def validate_font(font, text, max_width, max_height, line_space=0):
    '''
    检查在不分词情况下 max_height 是否能满足行数要求
    分词时的长度 >= 不分词时的长度，如果不分词时长度就不够，则返回 False
    '''
    text_width, text_height = font.getsize(text)
    max_lines = max_height // (text_height + line_space)  # 最多可容纳多少行
    required_lines = (text_width + max_width) // max_width  # 实际需要多少行
    if required_lines > max_lines:
        return False

    return True


# 遍历不同 font size 的字体，选择最大的可用字体
def find_fitting_font(font_sizes, text, max_width, max_height, line_space=0):
    for size in reversed(font_sizes):
        font = ImageFont.truetype('./FONT.TTF', size)
        if validate_font(font, text, max_width, max_height, line_space):
            return font
    return None


# 根据行宽度，把 token 归集成 line
def make_token_lines(font, tokens, line_width):
    lines = []
    cur_line_tokens = []
    cur_line_width = 0
    for token in tokens:
        token_width = font.getsize(token)[0]
        if cur_line_width + token_width <= line_width:
            cur_line_width += token_width
            cur_line_tokens.append(token)
        else:
            lines.append(cur_line_tokens)
            cur_line_tokens = []
            cur_line_width = 0

    return lines


if __name__ == '__main__':
    text = '谋杀我吧'
    image = Image.open("./1.png")
    width, height = int(image.size[0] * 0.8), int(image.size[1] * 0.2)
    x, y = int(image.size[0] * 0.1), int(image.size[1] * 0.6)

    # 以矩形的 height 为上限，大小间隔为 5 的序列作为候选 font size
    min_font_size, max_font_size = 5, height
    candidate_font_sizes = range(min_font_size, max_font_size, 5)
    font = find_fitting_font(candidate_font_sizes, text, width, height, 0)
    if not font:
        print('fitting font is not found')
        exit()

    draw = ImageDraw.Draw(image)
    draw.text((x, y), text, font=font, fill=255)
    image.save('./result/sample-out.png')

    # font_sizes = range(5, 101)
    # size = find_fitting_font_size(font_sizes, validate_font_size)
    # text = 'This could be a single line text but its too long to fit in one.'
    # for i, ft in enumerate(fonts):
    #     print(i + 1, ft.getsize(text))
