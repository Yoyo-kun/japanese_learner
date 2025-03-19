Japanese Learner
Japanese Learner 是一款日语、英语单词默写与记忆软件，旨在帮助用户通过分组学习、生成默写题以及管理错题等方式，高效记忆单词和假名。软件支持两种学习模式：键值模式和三列假名模式，并集成了文本转语音（TTS）功能，让学习更加生动有趣。

特性
学习集管理

创建、编辑、删除学习集，支持键值模式（例如：apple りんご）与三列假名模式（例如：a あ ア）。
左侧列表中每个学习集带有独立的小方框按钮，用于标记选中状态，方便生成组合默写题。
错题本作为内置学习集存在，可直接选择、生成题目以及清空。
组合默写题生成

支持从多个选中的学习集中生成组合默写题，方便用户复习多个知识点。
错题本管理

错题本记录用户答错的题目，并根据艾宾浩斯遗忘曲线设定复习时间。
在错题本中，题卡右侧按钮由“错误”变为“移除”，点击后判断是否达到移除条件，满足条件则自动从错题本中移除。
三列假名模式优化

三列模式下，初始显示平假名与片假名（格式如“あ / ア”），点击后可以在平假名与片假名之间交替显示。
文本转语音（TTS）支持

集成 pyttsx3 实现 TTS 功能，支持日语与英语朗读，帮助用户更好地记忆发音。
数据持久化

学习集和错题数据均保存在持久化的数据文件中，确保每次启动软件时都能加载上次的学习内容和错题记录。
安装
克隆项目：

bash
Copy
Edit
git clone https://your.repository.url/japanese_learner.git
cd japanese_learner
创建虚拟环境并安装依赖：

bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
使用方法
启动软件：

在终端中运行：

bash
Copy
Edit
python main.py
添加与管理学习集：

点击左侧“添加组”按钮，使用弹出的编辑器录入学习集名称、模式（键值模式或三列假名模式）、上/下层语音以及单词数据。
编辑和删除学习集同样在左侧操作，错题本不能编辑，但可以清空。
生成组合默写题：

使用左侧列表中每个学习集右侧的小方框按钮进行选择（选中后按钮会显示实心圆点）。
选中一个或多个学习集后，点击“生成组合默写题”按钮，右侧将生成来自选中组的随机题目。
题卡操作：

左侧显示提示词（key 或 romaji），中间区域初始隐藏答案（value 或 “平假名 / 片假名”）。
点击答案区域后显示答案，针对三列模式点击后会在平假名与片假名之间切换显示。
上下层的“🔊”按钮分别调用 TTS 功能进行发音。
右侧按钮在普通题卡中用于标记错误，将题目添加到错题本；在错题本中用于“移除”题目（按艾宾浩斯曲线判断是否达到移除条件）。
构建可执行文件
项目提供了 build_exe.py 脚本，通过 PyInstaller 将项目打包成单个 exe 文件，并保证数据的持久化存储。

运行以下命令打包：

bash
Copy
Edit
python build_exe.py
打包完成后，生成的 exe 文件位于 dist 目录下。

数据存储
学习集数据保存在 data/groups.json 文件中。
错题数据保存在 data/wrong.json 文件中。
在非冻结（开发）状态下，数据存放于 core/data 目录；打包为 exe 后，数据会保存在 exe 同目录下的 data 文件夹中，确保数据跨会话持久保存。

依赖
PyQt5
pyttsx3
packaging
pip
colorama
requests
pywin32
setuptools
certifi
urllib3
idna
charset-normalizer
pyinstaller
详见 requirements.txt

许可
本项目遵循 LICENSE 中的许可协议。

致谢
