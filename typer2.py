#!/usr/bin/python3
# coding: utf-8

from PIL import Image, ImageFont, ImageDraw

import string


class SimpleTokenizer:
    """ 简单分词器

        把字符串分割成下面几种单词:
          - 连续的英文字母
          - 连续的数字
          - 其他字符（如中文、空格）单独分词
          - 标点符号与上一个词结合

        例子：
          "hello,world.123 你好，世界！"
          分词结果为：['hello,', 'world.', '123', ' ', '你', '好，', '世', '界！']
    """
    def parse(self, text):
        tokens = []
        i = 0
        while i < len(text):
            if self.is_letter(text[i]):  # 英文
                j = i + 1
                while j < len(text) and self.is_letter(text[j]):
                    j += 1
                tokens.append(text[i:j])
                i = j
            elif text[i].isdigit():  # 数字
                j = i + 1
                while j < len(text) and text[j].isdigit():
                    j += 1
                tokens.append(text[i:j])
                i = j
            elif self.is_punctuation(text[i]):  # 标点
                if tokens:
                    tokens[-1] = tokens[-1] + text[i]
                else:
                    tokens.append(text[i])
                i += 1
            else:  # 其他（中文、空格等）
                tokens.append(text[i])
                i += 1
        return tokens

    @staticmethod
    def is_letter(s):
        return 'a' <= s <= 'z' or 'A' <= s <= 'Z'

    @staticmethod
    def is_punctuation(c):
        return c in string.punctuation or c in '。，！？‘’“”…—《》（）【】'


class TextLayout:
    """ 实现在矩形(box)内的文字排版功能.

    Attributes:
        text: 绘制的字符串
        candidate_fonts: 候选字体
        box_width: 矩形长度
        box_height: 矩形高度
        line_space: 行间距
        right_padding: 右侧最大空白
        tokenizer: 分词器
        draw_font: 绘制使用的字体
        token_lines: 分成行的 token
    """

    def __init__(self, text, condidate_fonts, box_width, box_height, line_space, right_padding, tokenizer):
        self.text = text
        self.candidate_fonts = condidate_fonts
        self.box_width = box_width
        self.box_height = box_height
        self.line_space = line_space
        self.right_padding = right_padding
        self.tokenizer = tokenizer
        self.draw_font = None
        self.token_lines = []

    def _find_font(self):
        """ 遍历候选字体，返回第一个合适的字体作为绘制使用
        """
        if self.draw_font:
            return True
        for font in self.candidate_fonts:
            if self._test_font(font):
                self.draw_font = font
                return True
        return False

    def _test_font(self, font):
        """测试使用 font 字体能否在 box 范围内绘制 text
        """
        # 测试在不分词情况下是否能满足行数要求
        # 因为 分词后的高度 >= 不分词时的高度，如果不分词时就不满足，则直接返回 False
        text_width, text_height = font.getsize(self.text)
        max_line_number = self.box_height // (text_height + self.line_space)  # 最多可容纳多少行
        min_lines = (text_width + self.box_width) // self.box_width  # 最少需要多少行
        if min_lines > max_line_number:
            return False

        # 测试分词分行
        if not self._break_tokens_to_lines(font):
            return False
        if len(self.token_lines) > max_line_number:
            return False

        return True

    def _break_tokens_to_lines(self, font):
        """ 把字符串分成 token，再分组到多个 line 中
        """
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
                if self.right_padding:  # 检查右侧 padding
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
            draw.text((x, y), text, font=self.draw_font, fill=color)
            y += self.draw_font.getsize(text)[1]
            y += self.line_space


if __name__ == '__main__':
    text = '哈哈哈哈哈哈哈hello,world.123 你好，世界！'
    text = '试管医，手记！八细胞：承诺（完整版）'
    image = Image.open('./1.png')
    box_width = int(image.size[0] * 0.8)
    box_height = int(image.size[1] * 0.2)
    left = int(image.size[0] * 0.1)
    top = int(image.size[1] * 0.6)

    # 以 box_height 为上限, 3 为间隔，从大到小创建候选 font
    max_font_size = 300
    condidate_fonts = [
        ImageFont.truetype('./FONT.TTF', sz)
        for sz in range(max_font_size, 0, -3)
    ]

    tl = TextLayout(
        text,
        condidate_fonts,
        box_width, box_height,
        line_space=5,
        right_padding=10,
        tokenizer=SimpleTokenizer()
    )
    tl.draw(left, top, image)
    image.save('./result/sample-out.png')
