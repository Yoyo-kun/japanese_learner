import os
import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_data_files

def main():
    # 收集资源文件：resources 下所有 .qss 文件
    datas = collect_data_files('resources', includes=['*.qss'])
    # 收集 core/data 下所有 .json 文件
    datas += collect_data_files(os.path.join('core', 'data'), includes=['*.json'])

    # 将收集的数据转换为命令行参数的形式
    # 注意：在 Windows 下分隔符使用 os.pathsep，一般为 ";"
    add_data_args = []
    for src, dest in datas:
        add_data_args.append('--add-data')
        add_data_args.append(f'{src}{os.pathsep}{dest}')

    # 构造 PyInstaller 的参数列表
    opts = [
        'main.py',                      # 入口脚本
        '--name=japanese_learner',      # 生成的 exe 名称
        '--onefile',                    # 生成单个 exe 文件
        '--windowed',                   # 不显示命令行窗口
        '--clean',                      # 清理临时文件
    ]
    opts += add_data_args

    print("正在打包，请稍候……")
    PyInstaller.__main__.run(opts)
    print("打包完成！生成的 exe 文件位于 dist 目录下。")

if __name__ == '__main__':
    main()
