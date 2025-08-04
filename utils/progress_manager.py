import json
from pathlib import Path

# --- 路径定义 ---
# 获取项目根目录 (utils -> nvshu-app)
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PROGRESS_DIR = DATA_DIR / "progress"

# --- 章节和类型定义 ---
CHAPTERS = ["basics", "history", "geography", "phonology", "heritage"]
Q_TYPES = ["single", "multi"]

def initialize_all_progress_files():
    """
    遍历所有章节和题型，检查并创建缺失的进度文件。
    如果进度文件不存在，则根据对应的题库文件生成一个全新的进度文件。
    """
    print("开始检查并初始化所有进度文件...")
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    
    count_created = 0
    for chapter in CHAPTERS:
        for q_type in Q_TYPES:
            quiz_path = DATA_DIR / f"quiz_{chapter}_{q_type}.json"
            progress_path = PROGRESS_DIR / f"learned_{chapter}_{q_type}.json"

            # 只有在题库存在而进度文件不存在时才创建
            if quiz_path.exists() and not progress_path.exists():
                try:
                    with open(quiz_path, "r", encoding="utf-8") as f:
                        quiz_data = json.load(f)
                    
                    # 创建一个所有题目 streak 均为 0 的进度字典
                    # 确保题库是列表，并且列表中的项是字典
                    if isinstance(quiz_data, list) and all(isinstance(item, dict) for item in quiz_data):
                        # 使用 item.get('id', i) 作为备用，以防万一 'id' 键不存在
                        progress_data = {str(item.get('id', i)): 0 for i, item in enumerate(quiz_data)}
                    else:
                        print(f"  - [警告] {quiz_path.name} 的格式不正确，应为JSON数组。跳过。")
                        continue
                    
                    with open(progress_path, "w", encoding="utf-8") as f:
                        json.dump(progress_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"  - 已创建进度文件: {progress_path.name}")
                    count_created += 1
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"  - [错误] 处理 {quiz_path.name} 时出错: {e}")
                except Exception as e:
                    print(f"  - [未知错误] 创建 {progress_path.name} 时失败: {e}")

    if count_created == 0:
        print("所有进度文件均已存在，无需创建。")
    else:
        print(f"初始化完成，共创建了 {count_created} 个新的进度文件。")
    print("-" * 20)


def reset_chapter_progress(chapter_key: str):
    """
    重置指定章节的单选和多选题库进度。
    这会直接覆盖或创建新的进度文件，并将所有题目的 streak 设为 0。
    """
    if chapter_key not in CHAPTERS:
        print(f"[错误] 章节 '{chapter_key}' 不存在。")
        return

    print(f"正在重置章节 '{chapter_key}' 的学习进度...")
    for q_type in Q_TYPES:
        quiz_path = DATA_DIR / f"quiz_{chapter_key}_{q_type}.json"
        progress_path = PROGRESS_DIR / f"learned_{chapter_key}_{q_type}.json"

        if quiz_path.exists():
            try:
                with open(quiz_path, "r", encoding="utf-8") as f:
                    quiz_data = json.load(f)

                if isinstance(quiz_data, list) and all(isinstance(item, dict) for item in quiz_data):
                    progress_data = {str(item.get('id', i)): 0 for i, item in enumerate(quiz_data)}
                else:
                     print(f"  - [警告] {quiz_path.name} 的格式不正确，应为JSON数组。跳过。")
                     continue

                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(progress_data, f, indent=2, ensure_ascii=False)
                
                print(f"  - 已重置进度文件: {progress_path.name}")
            except Exception as e:
                print(f"  - [错误] 重置 {progress_path.name} 时失败: {e}")
        else:
            print(f"  - [跳过] 未找到题库文件: {quiz_path.name}，无法重置进度。")
    print(f"章节 '{chapter_key}' 重置完成。")


# ====================================================================
# 如果直接运行此脚本，则执行一次完整的初始化检查
# ====================================================================
if __name__ == '__main__':
    # 你可以直接在终端中运行 `python utils/progress_manager.py`
    # 来为所有章节生成初始的进度.json文件。
    initialize_all_progress_files()
