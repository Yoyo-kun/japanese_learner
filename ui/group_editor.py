from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox, QMessageBox
)
from core.models import StudyGroup

class GroupEditor(QDialog):
    def __init__(self, group=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("学习集编辑器")
        self.resize(900, 900)
        self.group = group
        self.result_group = None

        self.init_ui()
        if self.group:
            self.load_group_data()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 学习集名称
        name_layout = QHBoxLayout()
        name_label = QLabel("学习集名称：")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # 学习集类型
        type_layout = QHBoxLayout()
        type_label = QLabel("学习集类型：")
        self.type_combo = QComboBox()
        self.type_combo.addItem("键值模式", 1)
        self.type_combo.addItem("三列假名模式", 2)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # 上层语音语言选择
        upper_lang_layout = QHBoxLayout()
        upper_lang_label = QLabel("上层语音语言：")
        self.upper_lang_combo = QComboBox()
        self.upper_lang_combo.addItem("日语")
        self.upper_lang_combo.addItem("英语")
        upper_lang_layout.addWidget(upper_lang_label)
        upper_lang_layout.addWidget(self.upper_lang_combo)
        layout.addLayout(upper_lang_layout)

        # 下层语音语言选择
        lower_lang_layout = QHBoxLayout()
        lower_lang_label = QLabel("下层语音语言：")
        self.lower_lang_combo = QComboBox()
        self.lower_lang_combo.addItem("日语")
        self.lower_lang_combo.addItem("英语")
        lower_lang_layout.addWidget(lower_lang_label)
        lower_lang_layout.addWidget(self.lower_lang_combo)
        layout.addLayout(lower_lang_layout)

        # 提示信息
        self.instructions_label = QLabel()
        layout.addWidget(self.instructions_label)

        # 批量数据输入
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存")
        self.btn_cancel = QPushButton("取消")
        self.btn_save.clicked.connect(self.save_group)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.type_combo.currentIndexChanged.connect(self.update_instructions)
        self.update_instructions()

    def update_instructions(self):
        group_type = self.type_combo.currentData()
        if group_type == 1:
            self.instructions_label.setText("请输入：key value\n示例：apple りんご")
        else:
            self.instructions_label.setText("请输入：romaji hira kata\n示例：a あ ア")

    def load_group_data(self):
        self.name_edit.setText(self.group.name)
        idx = self.type_combo.findData(self.group.type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        if hasattr(self.group, "upper_lang"):
            upper_idx = self.upper_lang_combo.findText(self.group.upper_lang)
            if upper_idx >= 0:
                self.upper_lang_combo.setCurrentIndex(upper_idx)
        if hasattr(self.group, "lower_lang"):
            lower_idx = self.lower_lang_combo.findText(self.group.lower_lang)
            if lower_idx >= 0:
                self.lower_lang_combo.setCurrentIndex(lower_idx)

        lines = []
        if self.group.type == 1:
            for item in self.group.items:
                key = item.get("key", "")
                value = item.get("value", "")
                lines.append(f"{key} {value}")
        else:
            for item in self.group.items:
                romaji = item.get("romaji", "")
                hira = item.get("hira", "")
                kata = item.get("kata", "")
                lines.append(f"{romaji} {hira} {kata}")
        self.text_edit.setPlainText("\n".join(lines))

    def save_group(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "学习集名称不能为空。")
            return
        # 防止用户手动创建名称为“错题本”的组
        if name == "错题本":
            QMessageBox.warning(self, "错误", "该名称为系统保留名称，请使用其他名称。")
            return
        group_type = self.type_combo.currentData()
        upper_lang = self.upper_lang_combo.currentText()
        lower_lang = self.lower_lang_combo.currentText()

        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "错误", "请输入至少一个有效条目。")
            return

        lines = text.splitlines()
        items = []
        for i, line in enumerate(lines, 1):
            parts = line.split()
            if group_type == 1:
                if len(parts) != 2:
                    QMessageBox.warning(self, "错误", f"第 {i} 行格式不正确，应为2个字段：key value。")
                    return
                items.append({"key": parts[0], "value": parts[1]})
            else:
                if len(parts) != 3:
                    QMessageBox.warning(self, "错误", f"第 {i} 行格式不正确，应为3个字段：romaji hira kata。")
                    return
                items.append({"romaji": parts[0], "hira": parts[1], "kata": parts[2]})

        self.result_group = StudyGroup(name, group_type, items, upper_lang, lower_lang)
        self.accept()

    def get_group(self):
        return self.result_group
