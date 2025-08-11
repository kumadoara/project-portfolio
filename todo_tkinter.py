import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = "apptasks.json"

# タスクデータの読み込み
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open (DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# タスクデータの保存
def save_tasks():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# GUIセットアップ
root = tk.Tk()
root.title("ToDoアプリ")
root.geometry("400x400")
root.configure(bg="#f5f5f5")

# グローバル変数 tasks を初期化
tasks = load_tasks()

def refresh_list():
    listbox.delete(0, tk.END)
    for t in tasks:
        listbox.insert(tk.END, t)

# タスク追加
def add_task():
    task = entry.get().strip()
    if task:
        tasks.append(task)
        entry.delete(0, tk.END)
        refresh_list()
        save_tasks()

# タスク削除
def delete_task():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        tasks.pop(index)
        refresh_list()
        save_tasks()

# タスク編集
def edit_task():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        new_task = simpledialog.askstring("タスク編集", "新しいタスク名を入力してください。", initialvalue=tasks[index])
        if new_task:
            tasks[index] = new_task.strip()
            refresh_list()
            save_tasks()

# フォント
FONT_TITLE = ("Helvetica", 16, "bold")
FONT_NORMAL = ("Helvetica", 12)

# 入力欄
frame_input = tk.Frame(root, bg="#f5f5f5")
frame_input.pack(pady=5)

entry = tk.Entry(frame_input, font=FONT_NORMAL, width=25, bd=2, relief="groove")
entry.pack(side=tk.LEFT, padx=5)

btn_add = tk.Button(frame_input, text="追加", font=FONT_NORMAL, bg="#4CAF50", fg="white", command=add_task)
btn_add.pack(side=tk.LEFT)

# タイトル
title_label = tk.Label(root, text="🌿 ToDoリスト", font=FONT_TITLE, bg="#f5f5f5", fg="#4CAF50")
title_label.pack(pady=10)

# リストボックス
listbox = tk.Listbox(root, font=FONT_NORMAL, width=35, height=10, bd=2, relief="groove", selectbackground="#A5D6A7")
listbox.pack(pady=10)

# ボタン群
frame_buttons = tk.Frame(root, bg="#f5f5f5")
frame_buttons.pack()

btn_edit = tk.Button(frame_buttons, text="編集", font=FONT_NORMAL, bg="#FFC107", fg="black", command=edit_task)
btn_edit.pack(side=tk.LEFT, padx=5)

btn_delete = tk.Button(frame_buttons, text="削除", font=FONT_NORMAL, bg="#F44336", fg="white", command=delete_task)
btn_delete.pack(side=tk.LEFT, padx=5)

refresh_list()

# メイン処理
root.mainloop()
