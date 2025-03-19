#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont()
    font.setFamily("Microsoft YaHei")  # 或其它你喜欢的字体
    font.setPointSize(40)  # 设置为 40pt
    app.setFont(font)

    # 加载自定义样式
    style_path = os.path.join(os.path.dirname(__file__), "resources", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
