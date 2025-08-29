"""記録管理ページ"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.models.user_profile import WorkoutRecord, NutritionRecord
from datetime import datetime, timedelta

st.set_page_config(page_title="記録管理", page_icon="📊", layout="wide")

# プロフィールチェック
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.warning("⚠️  プロフィールを設定してください")
    st.stop()

st.title("📊  トレーニング・栄養記録")

# タブの作成
tab1, tab2, tab3 = st.tabs(["📈 ダッシュボード", "💪 トレーニング記録", "🍎 栄養記録"])

with tab1:
    st.subheader("週間サマリー")

    # データの読み込み
    workouts = st.session_state.data_manager.load_workouts()
    nutrition_records = st.session_state.data_manager.load_nutrition()

    if workouts:
        # 週間データの集計
        df_workouts = pd.DataFrame([w.model_dump() for w in workouts])
        df_workouts['date'] = pd.to_datetime(df_workouts['date'])

        # 過去7日間のデータ
        last_week = datetime.now() - timedelta(days=7)
        df_week = df_workouts[df_workouts['date'] >= last_week]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_workouts = len(df_week)
            st.metric("トレーニング回数", f"{total_workouts}回", delta="週間")
        
        with col2:
            total_duration = df_week['duration'].sum() if not df_week.empty else 0  
            st.metric("総運動時間", f"{total_duration}分", delta=f"{total_duration//60}時間{total_duration%60}分")
        
        with col3:
            total_calories = df_week['calories'].sum() if not df_week.empty else 0  
            st.metric("消費カロリー", f"{total_calories:,.0f} kcal", delta="週間合計")
        
        with col4:
            avg_intensity = df_week['intensity'].mode()[0] if not df_week.empty else "なし"  
            st.metric("平均強度", avg_intensity, delta="最頻値")

        # グラフ表示
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            # 日別カロリー消費グラフ
            if not df_week.empty:
                daily_calories = df_week.groupby(df_week['date'].dt.date)['calories'].sum().reset_index()
                fig = px.bar(
                    daily_calories,
                    x='date',
                    y='calories',
                    title='日別消費カロリー',
                    labels={'calories': 'カロリー（kcal）', 'date': '日付'},
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("まだデータがありません")

    with col2:
        # 運動種目別の分布
        if not df_week.empty:
            exercise_dist = df_week['exercise'].value_counts().reset_index()
            exercise_dist.columns = ['exercise', 'count']
            fig = px.pie(
                exercise_dist,
                values='count',
                names='exercise',
                title='運動種目の分布',
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("まだデータがありません")

    # 週間トレンド
    st.markdown("### 📈  週間トレンド")
    if not df_workouts.empty:
        # 過去4週間のトレンド
        df_workouts['week'] = df_workouts['date'].dt.isocalendar().week
        weekly_stats = df_workouts.groupby('week').agg({
            'duration': 'sum',
            'calories': 'sum',
            'exercise': 'count'
        }).tail(4)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats['duration'],
            mode='lines+markers',
            name='運動時間（分）',
            yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats['calories'],
            mode='lines+markers',
            name='消費カロリー',
            yaxis='y2'
        ))

        fig.update_layout(
            title='週間トレーニングトレンド',
            xaxis_title='週',
            yaxis=dict(title='運動時間（分）', side='left'),
            yaxis2=dict(title='消費カロリー', overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 トレーニング記録を始めましょう！")

with tab2:
        st.subheader("💪 トレーニング履歴")

        workouts = st.session_state.data_manager.load_workouts()

        if workouts:
            # フィルター
            col1, col2, col3 = st.columns(3)
            with col1:
                date_filter = st.date_input(
                    "期間",
                    value=(datetime.now() - timedelta(days=30), datetime.now()),
                    format="YYYY-MM-DD"
                )
            with col2:
                exercise_list = list(set([w.exercise for w in workouts]))
                exercise_filter = st.multiselect("運動種目", exercise_list)
            with col3:
                intensity_filter = st.multiselect("強度", ["低", "中", "高"])
            
            # データフレームの作成とフィルタリング
            df = pd.DataFrame([w.model_dump() for w in workouts])
            df['date'] = pd.to_datetime(df['date'])

            # フィルター適用
            if len(date_filter) == 2:
                mask = (df['date'].dt.date >= date_filter[0]) & (df['date'].dt.date <= date_filter[1])
                df = df[mask]

            if exercise_filter:
                df = df[df['exercise'].isin(exercise_filter)]

            if intensity_filter:
                df = df[df['intensity'].isin(intensity_filter)]

            # 表示
            df_display = df.sort_values('date', ascending=False)
            df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d %H:%M')

            st.dataframe(
                df_display[['date', 'exercise', 'duration', 'calories','intensity', 'notes']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": "日時",
                    "exercise": "運動",
                    "duration": st.column_config.NumberColumn("時間（分）", format="%d 分"),
                    "calories": st.column_config.NumberColumn("カロリー", format="%d kcal"),
                    "intensity": "強度",
                    "notes": "メモ"
                }
            )

            # エクスポート機能
            csv = df_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"workout_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("まだトレーニング記録がありません。トレーニングチャットページから記録を追加してください。")

with tab3:
    st.subheader("🍎 栄養記録") 

    # 栄養記録の追加フォーム
    with st.expander("➕ 新しい食事記録を追加", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            meal_type = st.selectbox("食事タイプ", ["朝食", "昼食", "夕食", "間食"])
            meal_date = st.date_input("日付", value=datetime.now())
            meal_time = st.time_input("時間", value=datetime.now().time())
        
        with col2:
            st.markdown("###  食品を追加")
            food_name = st.text_input("食品名")
            calories = st.number_input("カロリー（kcal）",min_value=0, value=0)
            protein = st.number_input("タンパク質（g）",min_value=0.0, value=0.0)
            carbs = st.number_input("炭水化物（g）",min_value=0.0, value=0.0)
            fat = st.number_input("脂質（g）",min_value=0.0, value=0.0)
        
        notes = st.text_area("メモ（任意）")

        if st.button("記録を保存", use_container_width=True):
            if food_name and calories > 0:
                record = NutritionRecord(
                    date=datetime.combine(meal_date, meal_time),
                    meal_type=meal_type,
                    foods=[{
                        "name": food_name,
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat
                    }],
                    total_calories=calories,
                    notes=notes
                )

                if st.session_state.data_manager.save_nutrition(record):
                    st.success("✅  栄養記録を保存しました！")
                    st.rerun()
        else:
            st.error("食品名とカロリーを入力してください")
        
    # 栄養記録の表示
    nutrition_records = st.session_state.data_manager.load.nutrition()

    if nutrition_records:
        df_nutrition = pd.DataFrame([n.model_dump() for n in nutrition_records])
        df_nutrition['date'] = pd.to_datetime(df_nutrition['date'])

        # 今日の栄養摂取
        today = datetime.now().date()
        today_records = df_nutrition[df_nutrition['date'].dt.date == today]

        if not today_records.empty:
            st.markdown("### 📅 今日の栄養摂取")
            col1, col2, col3, col4 = st.columns(4)

            total_calories_today = today_records['total_calories'].sum()

            # 目標カロリーの計算
            from src.utils.helpers import calculate_bmr, calculate_tdee
            bmr = calculate_bmr(
                st.session_state.user_profile.height,
                st.session_state.user_profile.weight,
                st.session_state.user_profile.age,
                st.session_state.user_profile.gender
            )
            tdee = calculate_tdee(bmr, st.session_state.user_profile.activity_level)

            if st.session_state.user_profile.goal == "減量":
                target_calories = tdee - 500
            elif st.session_state.user_profile.goal == "増量":
                target_calories = tdee + 500
            else:
                target_calories = tdee
            
            with col1:
                st.metric("摂取カロリー", f"{total_calories_today:.0f} kcal")
            with col2:
                st.metric("目標カロリー", f"{target_calories:.0f} kcal")
            with col3:
                remaining = target_calories - total_calories_today
                st.metric("残りカロリー", f"{remaining:.0f} kcal",
                          delta=f"{remaining/target_calories*100:.1f}%")
            with col4:
                achievement = (total_calories_today / target_calories) * 100
                st.metric("達成率", f"{achievement:.1f}%")
            
            # 履歴表示
            st.markdown("### 📋 食事履歴")
            df_display = df_nutrition.sort_values('date', ascending=False)
            df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d %H:%M')

            # 食品情報を展開して表示
            for idx, row in df_display.iterrows():
                with st.expander(f"{row['date']} - {row['meal_type']} ({row['total_calories']:.0f} kcal)"):
                    for food in row['foods']:
                        st.write(f"**{food['name']}**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.write(f"カロリー: {food['calories']:.0f} kcal")
                        with col2:
                            st.write(f"タンパク質: {food.get('protein', 0):.1f}g")
                        with col3:
                            st.write(f"炭水化物: {food.get('carbs', 0):.1f}g")
                        with col4:
                            st.write(f"脂質: {food.get('fat', 0):.1f}g")
                    if row['notes']:
                        st.write(f"📝  メモ: {row['notes']}")
    else:
        st.info("まだ栄養記録がありません。上のフォームから記録を追加してください。")                    
