import json
import os
import time
import sys

# 根据运行环境设置数据存放路径
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(os.path.dirname(sys.executable), "data")
else:
    base_dir = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

DATA_PATH = os.path.join(base_dir, "groups.json")
WRONG_PATH = os.path.join(base_dir, "wrong.json")

class StudyGroup:
    def __init__(self, name, group_type, items, upper_lang="日语", lower_lang="日语"):
        self.name = name
        self.type = group_type  # 1: 键值模式, 2: 三列模式
        self.items = items
        self.upper_lang = upper_lang
        self.lower_lang = lower_lang

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "items": self.items,
            "upper_lang": self.upper_lang,
            "lower_lang": self.lower_lang
        }

def load_groups():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            groups = []
            for g in data:
                groups.append(StudyGroup(
                    g.get("name", ""),
                    g.get("type", 1),
                    g.get("items", []),
                    g.get("upper_lang", "日语"),
                    g.get("lower_lang", "日语")
                ))
            return groups
        except Exception as e:
            print("加载学习集失败:", e)
            return []

def save_groups(groups):
    data = [g.to_dict() for g in groups]
    directory = os.path.dirname(DATA_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 错题本相关功能

def load_wrong_items():
    if not os.path.exists(WRONG_PATH):
        return []
    with open(WRONG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print("加载错题本失败:", e)
            return []

def save_wrong_items(wrong_items):
    directory = os.path.dirname(WRONG_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(WRONG_PATH, "w", encoding="utf-8") as f:
        json.dump(wrong_items, f, ensure_ascii=False, indent=4)

def add_wrong_item(item_data, group_type, upper_lang, lower_lang):
    wrong_items = load_wrong_items()
    unique_id = ""
    if group_type == 1:
        unique_id = "kv_" + item_data.get("key", "")
    else:
        unique_id = "tri_" + item_data.get("romaji", "") + "_" + item_data.get("hira", "")
    existing = None
    for wi in wrong_items:
        if wi.get("unique_id") == unique_id:
            existing = wi
            break
    current_time = time.time()
    base_interval = 600  # 10分钟
    if existing:
        existing["error_count"] += 1
        interval = base_interval * (2 ** (existing["error_count"] - 1))
        existing["next_review"] = current_time + interval
    else:
        new_item = {
            "unique_id": unique_id,
            "group_type": group_type,
            "data": item_data,
            "upper_lang": upper_lang,
            "lower_lang": lower_lang,
            "error_count": 1,
            "next_review": current_time + base_interval
        }
        wrong_items.append(new_item)
    save_wrong_items(wrong_items)
