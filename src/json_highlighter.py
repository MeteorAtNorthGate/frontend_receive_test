from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # 1. 键名 (Key) - 蓝色
        # 使用正向先行断言 (?=\s*:)，这是合法的
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#268bd2"))
        key_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression(r'"[^"\\]*"(?=\s*:)'), key_format))

        # 2. 字符串值 (String Value) - 绿色
        # 修改点：使用 \K 替代 (?<=:\s*)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#859900"))
        self.highlighting_rules.append((QRegularExpression(r':\s*\K"[^"\\]*"'), string_format))

        # 3. 数字 (Number) - 橘色
        # 考虑到你的数据中有 "800."  和 "0.0E+0" [cite: 5] 这种科学计数法
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#cb4b16"))
        self.highlighting_rules.append((QRegularExpression(r'\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'), number_format))

        # 4. 布尔值和 Null - 紫色
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#6c71c4"))
        self.highlighting_rules.append((QRegularExpression(r'\b(true|false|null)\b'), keyword_format))

    def highlightBlock(self, text):
        for expression, format in self.highlighting_rules:
            # 检查正则表达式是否有效，防止程序崩溃
            if not expression.isValid():
                continue
                
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)