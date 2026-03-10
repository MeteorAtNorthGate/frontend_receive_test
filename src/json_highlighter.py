from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # 键名 (Key) - 蓝色
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#268bd2"))
        key_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression(r'"[^"\\]*"(?=\s*:)'), key_format))

        # 字符串值 (String Value) - 绿色
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#859900"))
        self.highlighting_rules.append((QRegularExpression(r'(?<=:\s*)"[^"\\]*"'), string_format))

        # 数字 (Number) - 橘色
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#cb4b16"))
        self.highlighting_rules.append((QRegularExpression(r'\b[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'), number_format))

        # 布尔值和 Null - 紫色
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#6c71c4"))
        self.highlighting_rules.append((QRegularExpression(r'\b(true|false|null)\b'), keyword_format))

    def highlightBlock(self, text):
        for expression, format in self.highlighting_rules:
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)