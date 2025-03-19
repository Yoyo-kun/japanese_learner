import time, random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QListWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QScrollArea,
    QMessageBox, QSpacerItem, QSizePolicy, QAbstractItemView, QListWidgetItem, QToolButton
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QCursor

from core.models import load_groups, save_groups, StudyGroup, load_wrong_items, save_wrong_items, add_wrong_item
from ui.group_editor import GroupEditor
from core.tts import speak


class GroupListItemWidget(QWidget):
    """
    自定义学习集列表条目：
      左侧显示学习集名称，
      右侧显示一个小按钮（QToolButton），点击时切换选中状态，并显示或隐藏实心圆点标记。
    """
    def __init__(self, group_name, parent=None):
        super().__init__(parent)
        self.group_name = group_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(self.group_name)
        layout.addWidget(self.label)
        # 去掉或调整 addStretch()，例如换成一个较小的间隔：
        # layout.addStretch()
        layout.addSpacing(100)  # 加一个固定间距，而不是弹性间距
        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(47, 47)  # 增大按钮尺寸
        self.toggle_button.toggled.connect(self.on_toggled)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)

    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setText("⬤")
        else:
            self.toggle_button.setText("")


class CardWidget(QWidget):
    """
    单个卡片组件，固定 500×200 像素，采用水平布局分为三个块：
      - 左侧块：显示提示词与上层播放按钮
      - 中间块：显示答案（点击显示/切换）与下层播放按钮
      - 右侧块：显示标记错误 / 移除按钮
    """
    def __init__(self, item_data, group_type, upper_lang, lower_lang, on_mark_wrong=None, is_wrong=False, wrong_item=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.group_type = group_type
        self.upper_lang = upper_lang
        self.lower_lang = lower_lang
        self.on_mark_wrong = on_mark_wrong  # 回调函数
        self.answer_visible = False  # 默认答案隐藏

        # 针对三列模式，默认显示平假名，同时新增标记，用于判断是否已经切换为单一显示
        if self.group_type == 2:
            self.use_hiragana = True
            self.toggled = False

        self.is_wrong = is_wrong
        self.wrong_item = wrong_item

        # 固定卡片整体大小为 500×200 像素
        self.setFixedSize(500, 200)
        self.init_ui()

    def init_ui(self):
        bold_font = QFont()
        bold_font.setPointSize(20)
        bold_font.setBold(True)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # ---------- 左侧块：提示词 + 上层 TTS ----------
        left_widget = QWidget()
        left_widget.setFixedWidth(150)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        left_widget.setLayout(left_layout)
        left_widget.setStyleSheet("background-color: #d0eaff;")

        self.prompt_label = QLabel()
        self.prompt_label.setFont(bold_font)
        self.prompt_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.prompt_label, stretch=1)

        self.tts_upper_button = QPushButton("🔊")
        self.tts_upper_button.setFixedWidth(50)
        self.tts_upper_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.tts_upper_button.clicked.connect(self.play_tts_upper)
        left_layout.addWidget(self.tts_upper_button, alignment=Qt.AlignCenter)

        main_layout.addWidget(left_widget)

        # ---------- 中间块：答案区域 + 下层 TTS ----------
        mid_widget = QWidget()
        mid_widget.setFixedWidth(150)
        mid_layout = QVBoxLayout()
        mid_layout.setContentsMargins(5, 5, 5, 5)
        mid_layout.setSpacing(5)
        mid_widget.setLayout(mid_layout)
        mid_widget.setStyleSheet("background-color: #dfffd0;")

        self.answer_label = QLabel()
        self.answer_label.setFont(bold_font)
        self.answer_label.setAlignment(Qt.AlignCenter)
        self.answer_label.setStyleSheet("color: #888;")
        self.answer_label.installEventFilter(self)
        mid_layout.addWidget(self.answer_label, stretch=1)

        self.tts_lower_button = QPushButton("🔊")
        self.tts_lower_button.setFixedWidth(50)
        self.tts_lower_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.tts_lower_button.clicked.connect(self.play_tts_lower)
        mid_layout.addWidget(self.tts_lower_button, alignment=Qt.AlignCenter)

        main_layout.addWidget(mid_widget)

        # ---------- 右侧块：标记错误 / 移除按钮 ----------
        right_widget = QWidget()
        right_widget.setFixedWidth(150)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        right_widget.setLayout(right_layout)
        right_widget.setStyleSheet("background-color: #ffe0e0;")

        self.mark_wrong_button = QPushButton("错误")
        self.mark_wrong_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.mark_wrong_button.clicked.connect(self.mark_wrong)
        # 如果是错题本中的题目，则显示“移除”
        if self.is_wrong:
            self.mark_wrong_button.setText("移除")
        right_layout.addStretch(1)
        right_layout.addWidget(self.mark_wrong_button, alignment=Qt.AlignCenter)
        right_layout.addStretch(1)

        main_layout.addWidget(right_widget)

        self.setup_text()

    def setup_text(self):
        if self.group_type == 1:
            # 键值模式：左侧显示 key，中间显示 value（初始隐藏）
            key = self.item_data.get("key", "")
            value = self.item_data.get("value", "")
            self.prompt_label.setText(key)
            self._answer_text = value
            self.update_answer_label()
        else:
            # 三列模式：左侧显示 romaji，中间显示平假名与片假名（初始显示为“平假名 / 片假名”）
            romaji = self.item_data.get("romaji", "")
            hira = self.item_data.get("hira", "")
            kata = self.item_data.get("kata", "")
            self.prompt_label.setText(romaji)
            self._answer_text_hira = hira
            self._answer_text_kata = kata
            self.update_answer_label()

    def update_answer_label(self):
        if not self.answer_visible:
            self.answer_label.setText("******")
        else:
            if self.group_type == 1:
                self.answer_label.setText(self._answer_text)
            else:
                # 三列模式：初始显示时显示平假名和片假名，点击后切换显示
                if not self.toggled:
                    self.answer_label.setText(f"{self._answer_text_hira} / {self._answer_text_kata}")
                else:
                    if self.use_hiragana:
                        self.answer_label.setText(self._answer_text_hira)
                    else:
                        self.answer_label.setText(self._answer_text_kata)

    def eventFilter(self, source, event):
        if source is self.answer_label and event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                if not self.answer_visible:
                    self.answer_visible = True
                    self.update_answer_label()
                else:
                    # 针对三列模式：点击后切换平/片假名显示（并标记已切换）
                    if self.group_type == 2:
                        self.toggled = True
                        self.use_hiragana = not self.use_hiragana
                        self.update_answer_label()
            return True
        return super().eventFilter(source, event)

    def play_tts_upper(self):
        text = self.prompt_label.text()
        if text and text != "******":
            if self.upper_lang == "英语":
                text_to_speak = " ".join(list(text))
            else:
                text_to_speak = text
            speak(text_to_speak)

    def play_tts_lower(self):
        if not self.answer_visible:
            return
        if self.group_type == 1:
            text = self._answer_text
        else:
            text = self._answer_text_hira if self.use_hiragana else self._answer_text_kata
        if text and text != "******":
            if self.lower_lang == "英语":
                text_to_speak = " ".join(list(text))
            else:
                text_to_speak = text
            speak(text_to_speak)

    def mark_wrong(self):
        if self.on_mark_wrong:
            if self.is_wrong:
                self.on_mark_wrong(self.wrong_item)
            else:
                self.on_mark_wrong(self.item_data, self.group_type, self.upper_lang, self.lower_lang)
                QMessageBox.information(self, "提示", "已添加到错题本。")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日语学习助手")
        self.resize(1000, 600)

        self.study_groups = load_groups()
        self.current_mode = "group"  # "group"（正常组）、"wrong"（错题本）或 "combined"
        self.current_group = None  # 当前选中组（group模式下）

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # --------- 左侧：自定义学习集列表（带右侧小按钮） + 按钮 ---------
        self.left_scroll_area = QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        left_container = QWidget()
        left_panel = QVBoxLayout(left_container)

        # 使用 QListWidget 添加自定义项，取消系统选择（只依靠右侧的小按钮）
        self.group_list = QListWidget()
        self.group_list.setSelectionMode(QAbstractItemView.NoSelection)
        left_panel.addWidget(self.group_list)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加组")
        self.btn_edit = QPushButton("修改组")
        self.btn_delete = QPushButton("删除组")
        self.btn_add.clicked.connect(self.add_group)
        self.btn_edit.clicked.connect(self.edit_group)
        self.btn_delete.clicked.connect(self.delete_group)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        left_panel.addLayout(btn_layout)

        # 新增按钮：生成组合默写题（依赖右侧小按钮的选中状态）
        self.btn_generate_combined = QPushButton("生成组合默写题")
        self.btn_generate_combined.clicked.connect(self.generate_combined_test)
        left_panel.addWidget(self.btn_generate_combined)

        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        left_panel.addSpacerItem(spacer)

        self.left_scroll_area.setWidget(left_container)
        main_layout.addWidget(self.left_scroll_area, 2)

        # --------- 右侧：一键显示全部答案按钮 + 卡片区域（滚动区域） ---------
        right_panel = QVBoxLayout()
        self.show_all_button = QPushButton("一键显示全部答案")
        self.show_all_button.clicked.connect(self.show_all_answers)
        right_panel.addWidget(self.show_all_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cards_container = QWidget()
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setSpacing(20)
        self.scroll_area.setWidget(self.cards_container)
        right_panel.addWidget(self.scroll_area)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget, 5)

        self.load_group_list()

    def load_group_list(self):
        self.group_list.clear()
        # 添加所有用户创建的学习集
        for g in self.study_groups:
            item = QListWidgetItem()
            widget = GroupListItemWidget(g.name)
            item.setSizeHint(widget.sizeHint())
            self.group_list.addItem(item)
            self.group_list.setItemWidget(item, widget)
        # 添加系统内置的“错题本”
        item = QListWidgetItem()
        widget = GroupListItemWidget("错题本")
        item.setSizeHint(widget.sizeHint())
        self.group_list.addItem(item)
        self.group_list.setItemWidget(item, widget)

    def get_checked_groups(self):
        checked = []
        for index in range(self.group_list.count()):
            item = self.group_list.item(index)
            widget = self.group_list.itemWidget(item)
            if widget.toggle_button.isChecked():
                checked.append(widget.group_name)
        return checked

    def refresh_cards(self, group: StudyGroup):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        items = group.items[:]
        random.shuffle(items)
        row = 0
        col = 0
        max_col = 3  # 每行显示3个卡片
        for item_data in items:
            card = CardWidget(
                item_data,
                group.type,
                group.upper_lang,
                group.lower_lang,
                on_mark_wrong=self.handle_mark_wrong
            )
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def refresh_wrong_cards(self, wrong_items):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        row = 0
        col = 0
        max_col = 3
        for wi in wrong_items:
            data = wi.get("data", {})
            group_type = wi.get("group_type", 1)
            upper_lang = wi.get("upper_lang", "日语")
            lower_lang = wi.get("lower_lang", "日语")
            card = CardWidget(data, group_type, upper_lang, lower_lang,
                              on_mark_wrong=self.handle_remove_wrong,
                              is_wrong=True,
                              wrong_item=wi)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def refresh_combined_cards(self, combined_items):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        row = 0
        col = 0
        max_col = 3
        for entry in combined_items:
            if entry.get("is_wrong", False):
                card = CardWidget(entry["item_data"], entry["group_type"], entry["upper_lang"], entry["lower_lang"],
                                  on_mark_wrong=self.handle_remove_wrong,
                                  is_wrong=True,
                                  wrong_item=entry["wrong_item"])
            else:
                card = CardWidget(entry["item_data"], entry["group_type"], entry["upper_lang"], entry["lower_lang"],
                                  on_mark_wrong=self.handle_mark_wrong)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= max_col:
                col = 0
                row += 1

    def show_all_answers(self):
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item.widget() and hasattr(item.widget(), "answer_visible"):
                item.widget().answer_visible = True
                item.widget().update_answer_label()

    def add_group(self):
        dlg = GroupEditor(parent=self)
        if dlg.exec_():
            new_group = dlg.get_group()
            if any(g.name == new_group.name for g in self.study_groups):
                QMessageBox.warning(self, "错误", "该组名称已存在，请重新输入。")
                return
            self.study_groups.append(new_group)
            save_groups(self.study_groups)
            self.load_group_list()

    def edit_group(self):
        # 仅允许编辑单个学习集（非“错题本”）
        checked = self.get_checked_groups()
        if len(checked) != 1:
            QMessageBox.warning(self, "错误", "请选择单个学习集进行修改。")
            return
        group_name = checked[0]
        if group_name == "错题本":
            QMessageBox.warning(self, "错误", "错题本不能编辑。")
            return
        group = next((g for g in self.study_groups if g.name == group_name), None)
        if group:
            dlg = GroupEditor(group, parent=self)
            if dlg.exec_():
                edited_group = dlg.get_group()
                if edited_group.name != group.name and any(g.name == edited_group.name for g in self.study_groups):
                    QMessageBox.warning(self, "错误", "该组名称已存在，请重新输入。")
                    return
                group.name = edited_group.name
                group.type = edited_group.type
                group.items = edited_group.items
                group.upper_lang = edited_group.upper_lang
                group.lower_lang = edited_group.lower_lang
                save_groups(self.study_groups)
                self.load_group_list()

    def delete_group(self):
        checked = self.get_checked_groups()
        if not checked:
            QMessageBox.warning(self, "错误", "请选择要删除的组。")
            return
        for group_name in checked:
            if group_name == "错题本":
                reply = QMessageBox.question(self, "确认删除", "确定要清空错题本吗？", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    save_wrong_items([])
                    if self.current_mode == "wrong":
                        self.refresh_wrong_cards([])
            else:
                reply = QMessageBox.question(self, "确认删除", f"确定要删除学习集「{group_name}」吗？", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.study_groups = [g for g in self.study_groups if g.name != group_name]
                    save_groups(self.study_groups)
        self.load_group_list()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def generate_combined_test(self):
        checked = self.get_checked_groups()
        if not checked:
            QMessageBox.warning(self, "错误", "请选择至少一个学习集。")
            return
        combined = []
        current_time = time.time()
        for group_name in checked:
            if group_name == "错题本":
                wrong_items = load_wrong_items()
                due_items = [wi for wi in wrong_items if wi.get("next_review", 0) <= current_time]
                for wi in due_items:
                    combined.append({
                        "item_data": wi.get("data", {}),
                        "group_type": wi.get("group_type", 1),
                        "upper_lang": wi.get("upper_lang", "日语"),
                        "lower_lang": wi.get("lower_lang", "日语"),
                        "is_wrong": True,
                        "wrong_item": wi
                    })
            else:
                group = next((g for g in self.study_groups if g.name == group_name), None)
                if group:
                    for data in group.items:
                        combined.append({
                            "item_data": data,
                            "group_type": group.type,
                            "upper_lang": group.upper_lang,
                            "lower_lang": group.lower_lang,
                            "is_wrong": False
                        })
        if not combined:
            QMessageBox.information(self, "提示", "所选学习集没有可用的题目。")
            return
        random.shuffle(combined)
        self.current_mode = "combined"
        self.refresh_combined_cards(combined)

    def handle_mark_wrong(self, item_data, group_type, upper_lang, lower_lang):
        add_wrong_item(item_data, group_type, upper_lang, lower_lang)

    def handle_remove_wrong(self, wrong_item):
        current_time = time.time()
        if current_time >= wrong_item.get("next_review", 0):
            wrong_items = load_wrong_items()
            wrong_items = [wi for wi in wrong_items if wi.get("unique_id") != wrong_item.get("unique_id")]
            save_wrong_items(wrong_items)
            QMessageBox.information(self, "提示", "已移除错题。")
            if self.current_mode == "wrong" or self.current_mode == "combined":
                self.refresh_wrong_cards(wrong_items)
        else:
            QMessageBox.warning(self, "提示", "未达到移除条件。")
