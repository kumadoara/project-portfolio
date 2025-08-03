import random

# 1から100までの数当てゲーム
def number_game():
    # 1から100までの乱数を作成
    target_number = random.randint(1, 100)
    attempts = 0

    print("-" * 40)
    print("数当てゲームへようこそ!")
    print("1から100までの数字を当ててください")
    print("ゲームを終了するには'q'を入力してください")
    print("-" * 40)

    while True:
        try:
            # ユーザの入力を受け取る
            user_input = input("\n数字を入力してください")

            # 'q'が入力された場合はゲーム終了
            if user_input.lower() == 'q':
                print("ゲームを終了します。またお会いしましょう!")
                break

            # 数字に変換
            guess = int(user_input)
            attempts += 1

            # 範囲外チェック
            if guess < 1 or guess > 100:
                print("1から100までの数字を入力してください")
                attempts -= 1  # 無効な入力の場合は試行回数をカウントしない
                continue

            # 正解判定
            if guess == target_number:
                print(f"\n🎉 正解です!  答えは{target_number}でした!")
                print(f"試行回数:  {attempts}回")
                print("おめでとうございます!")
                break
            elif guess < target_number:
                print("もっと大きい数字です")
            else:
                print("もっと小さい数字です")
        
        except ValueError:
            print("有効な数字を入力してください（または'q'で終了）")

# メイン関数
def main():
    while True:
        number_game()

        # もう一度プレイするか確認
        while True:
            play_again = input("\nもう一度プレイしますか? (y/n): ").strip().lower()
            if play_again in ['y', 'yes', 'はい']:
                break
            elif play_again in ['n', 'no', 'いいえ']:
                print("ゲームを終了します。ありがとうございました!")
                return
            else:
                print("'y' または 'n' で答えてください")

# プログラム実行
if __name__ == "__main__":
    main()

