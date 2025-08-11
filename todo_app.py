import json
import os

DATA_FILE = "tasks.json"

def save_tasks(tasks):
    """タスクをJSONファイルに保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def load_tasks():
    """JSONファイルからタスクを読み込む"""
    if not os.path.exists(DATA_FILE):
        return []
        
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("警告: tasks.json の読み込みに失敗しました（JSONが壊れている可能性）。新規作成します。")
        return []
    
    # ケース1: {"tasks": [...]}のようなラップされた形式
    if isinstance(data, dict) and "tasks" in data and isinstance(data["tasks"], list):
        data = data["tasks"]
    
    # 最低限、List型に正規化する
    if not isinstance(data, list):
        print("警告: 保存形式が想定と異なります。新規作成します。")
        return []
    
    normalized = []
    changed = False

    for item in data:
        # 文字列だけのリスト（古い形式） -> dictに変換
        if isinstance(item, str):
            normalized.append({"task": item, "done": False})
            changed = True
        # 期待どおりのdictならキーを補完して使う
        elif isinstance(item, dict):
            task_text = item.get("task") or item.get("title") or ""
            done_flag = bool(item.get("done", False))
            # もし'task'が欠けている・別キーの場合は変換したと判断
            if "task" not in item or "done" not in item:
                changed = True
            normalized.append({"task": task_text, "done": done_flag})
        else:
            # 不明な型はスキップ（保存データが混ざっていた場合の安全策）
            changed = True
            continue
    # 正規化で変更が発生したら、上書き保存して次回以降はクリーンな形式にする
    if changed:
        print("注意: タスクデータを新しい形式に自動変換して保存します。")
        save_tasks(normalized)
    return normalized

def show_menu():
    """メニュー表示"""
    print("\n=== ToDo アプリ ===")
    print("1. タスクを追加")
    print("2. タスクを表示")
    print("3. タスクを完了")
    print("4. 完了済みタスクを削除")
    print("5. タスクを編集")
    print("6. アプリの終了")

def add_task(tasks):
    """タスクを追加"""
    task = input("追加するタスクを入力してください: ").strip()
    if task:
        tasks.append({"task": task, "done": False})
        save_tasks(tasks)
        print(f"タスク『{task}』を追加しました。")
    else:
        print("タスク名が空です。追加できません。")

def show_tasks(tasks):
    """タスクを表示"""
    if not tasks:
        print("タスクはありません。")
        return
    
    print("\n--- タスク一覧 ---")
    for i, t in enumerate(tasks, start=1):
        text = t.get("task") if isinstance(t, dict) else str(t)
        done = t.get("done", False) if isinstance(t, dict) else False
        status = "✅ 完了" if done else "⏳ 未完了"
        print(f"{i}. {text} - {status}")
    print("------------------")

def complete_task(tasks):
    """タスクを完了"""
    if not tasks:
        print("タスクはありません。")
        return
    try:
        num = int(input("完了するタスク番号を入力してください: ").strip())
        if 1 <= num <= len(tasks):
            tasks[num - 1]["done"] = True
            save_tasks(tasks)
            print(f"タスク『{tasks[num - 1]['task']}』を完了しました。")
        else:
            print("タスク番号が範囲外です。1 〜", len(tasks), "の番号を入力してください。")
    except ValueError:
        print("無効な入力です。数字を入力してください。")

def delete_completed_tasks(tasks):
    """完了したタスクを削除"""
    completed = [t for t in tasks if t.get("done")]
    if not completed:
        print("完了済みのタスクはありません。")
        return
    confirm = input("完了済みタスクをすべて削除しますか？(y/n): ").strip().lower()
    if confirm == "y":
        tasks[:] = [t for t in tasks if not t.get("done")]
        save_tasks(tasks)
        print("完了済みタスクを削除しました。")
    else:
        print("削除をキャンセルしました。")

def edit_task(tasks):
    """タスクの編集"""
    if not tasks:
        print("タスクはありません。")
        return
    try:
        num = int(input("編集するタスク番号を入力してください: ").strip())
        if 1 <= num <= len(tasks):
            current = tasks[num - 1].get("task", "")
            new_task = input(f"新しいタスク内容（現在: {current}）: ").strip()
            if new_task:
                tasks[num - 1]["task"] = new_task
                save_tasks(tasks)
                print("タスクを更新しました。")
            else:
                print("タスク内容が空のため、更新をキャンセルしました。")
        else:
            print("タスク番号が範囲外です。")
    except ValueError:
        print("無効な入力です。数字を入力してください。")

def main():
    """メイン関数"""
    tasks = load_tasks()
    while True:
        show_menu()
        choice = input("番号を選択してください: ").strip()
        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_completed_tasks(tasks)
        elif choice == "5":
            edit_task(tasks)
        elif choice == "6":
            print("アプリを終了します。")
            break
        else:
            print("無効な選択肢です。1〜6の番号を入力してください。")

if __name__ == "__main__":
    main()
