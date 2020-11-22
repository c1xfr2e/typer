# coding: utf-8

from PIL import Image, ImageFont, ImageDraw

import string


def is_chinese(c):
    return u'\u4e00' <= c <= u'\u9fff'


def is_punctuation(c):
    return c in string.punctuation or c in '。，？‘’“”《》'


# 分词
def tokenize(str):
    return [s for s in str]


# 验证使用 font 字体能否在长 max_width, 高 max_height 的矩形内绘制 text
def validate_font(font, text, tokens, max_width, max_height, line_space=0):
    # 检查在不分词情况下是否能满足行数要求
    # 因为 分词后的高度 >= 不分词时的高度，如果不分词时不满足，则直接返回 False
    text_width, text_height = font.getsize(text)
    max_line_number = max_height // (text_height + line_space)  # 最多可容纳多少行
    min_required_lines = (text_width + max_width) // max_width  # 最少需要多少行
    if min_required_lines > max_line_number:
        return False, None

    lines = make_token_lines(font, tokens, max_width)
    if len(lines) > max_line_number:
        return False, None

    return True, lines


# 遍历不同 font size 的字体，选择最大的可用字体
def find_fitting_font(font_sizes, text, tokens, max_width, max_height, line_space=0):
    for size in reversed(font_sizes):
        font = ImageFont.truetype('./FONT.TTF', size)
        fit, lines = validate_font(font, text, tokens, max_width, max_height, line_space)
        if fit:
            return font, lines

    return None, None


# 根据行宽度，把 token 归集成 line
def make_token_lines(font, tokens, line_width):
    lines = []
    cur_line = []
    cur_width = 0
    for token in tokens:
        token_width = font.getsize(token)[0]
        if cur_width + token_width <= line_width:
            cur_width += token_width
            cur_line.append(token)
        else:
            lines.append(cur_line)
            cur_line = [token]
            cur_width = token_width
    if cur_line:
        lines.append(cur_line)

    return lines


def draw_lines(x, y, image, font, token_lines, line_height, color=255):
    draw = ImageDraw.Draw(image)
    for tokens in token_lines:
        text = ''.join(tokens)
        draw.text((x, y), text, font=font, fill=color)
        y += line_height


if __name__ == '__main__':
    text = '谋杀我的完美完美完美完美完美完美偶像偶像谋杀我的完美完美完美完美完美完美偶像偶像'
    image = Image.open("./1.png")
    width, height = int(image.size[0] * 0.8), int(image.size[1] * 0.2)
    x, y = int(image.size[0] * 0.1), int(image.size[1] * 0.6)

    tokens = tokenize(text)

    # 以矩形的 height 为上限，大小间隔为 5 的序列作为候选 font size
    min_font_size, max_font_size = 5, height
    candidate_font_sizes = range(min_font_size, max_font_size, 5)
    font, lines = find_fitting_font(candidate_font_sizes, text, tokens, width, height, 0)
    if not font:
        print('fitting font is not found')
        exit()

    line_height = font.getsize(text)[1]
    draw_lines(x, y, image, font, lines, line_height)
    image.save('./result/sample-out.png')
