#!/usr/bin/python3
# coding: utf-8

from PIL import Image, ImageFont, ImageDraw


class Tokenizer:
    """ 分词器
    """
    def parse(self, text):
        return [s for s in text]


class TextLayout:
    """ 实现在矩形(box)内的文字排版功能.

    Attributes:
        text: 绘制的字符串
        font_size_range: 字体大小范围
        box_width: 矩形长度
        box_height: 矩形高度
        line_space: 行间距
        right_padding: 右侧最大空白
        tokenizer: 分词器
        font: 绘制使用的字体
        token_lines: 分成行的 token
    """

    def __init__(self, text, font_file, font_size_range, box_width, box_height, line_space, right_padding, tokenizer):
        self.text = text
        self.font_file = font_file
        self.font_size_range = font_size_range
        self.box_width = box_width
        self.box_height = box_height
        self.line_space = line_space
        self.right_padding = right_padding
        self.tokenizer = tokenizer
        self.font = None
        self.token_lines = []

    # 寻找合适的字体
    def _find_font(self):
        if self.font:
            return True
        for size in reversed(self.font_size_range):
            font = ImageFont.truetype(self.font_file, size)
            if self._test_font(font):
                self.font = font
                return True
        return False

    # 测试使用 font 字体能否在 box 范围内绘制 text
    def _test_font(self, font):
        # 检查在不分词情况下是否能满足行数要求
        # 因为 分词后的高度 >= 不分词时的高度，如果不分词时不满足，则直接返回 False
        text_width, text_height = font.getsize(self.text)
        max_line_number = self.box_height // (text_height + self.line_space)  # 最多可容纳多少行
        min_lines = (text_width + self.box_width) // self.box_width  # 最少需要多少行
        if min_lines > max_line_number:
            return False

        if not self._break_tokens_to_lines(font):
            return False

        if len(self.token_lines) > max_line_number:
            return False

        return True

    # 把 token 分成多个 line
    def _break_tokens_to_lines(self, font):
        tokens = self.tokenizer.parse(self.text)
        token_lines = []
        cur_line = []
        cur_width = 0
        for token in tokens:
            token_width = font.getsize(token)[0]
            if cur_width + token_width <= self.box_width:
                cur_width += token_width
                cur_line.append(token)
            else:
                padding = self.box_width - cur_width
                if padding > self.right_padding:
                    return False
                token_lines.append(cur_line)
                cur_line = [token]
                cur_width = token_width
        if cur_line:
            token_lines.append(cur_line)

        self.token_lines = token_lines
        return True

    def draw(self, x, y, image, color=255):
        if not self._find_font():
            raise RuntimeError('Failed to find suitable font')
        draw = ImageDraw.Draw(image)
        for tokens in self.token_lines:
            text = ''.join(tokens)
            draw.text((x, y), text, font=self.font, fill=color)
            y += self.font.getsize(text)[1]
            y += self.line_space


if __name__ == '__main__':
    text = '谋杀我的完美偶像一二三四五六七八九十'
    image = Image.open('./1.png')
    box_width = int(image.size[0] * 0.8)
    box_height = int(image.size[1] * 0.2)
    left = int(image.size[0] * 0.1)
    top = int(image.size[1] * 0.6)

    # 以 box_height 为字体大小上限, 3 为间隔
    max_font_size = box_height
    min_font_size = 5
    font_size_range = range(min_font_size, max_font_size, 3)

    tl = TextLayout(
        text,
        './FONT.ttf', font_size_range,
        box_width, box_height,
        line_space=10,
        right_padding=10,
        tokenizer=Tokenizer()
    )
    tl.draw(left, top, image)
    image.save('./result/sample-out.png')
