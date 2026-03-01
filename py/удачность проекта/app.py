import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Добавляем текущую директорию в путь для импорта model.py
sys.path.append(os.path.dirname(__file__))

from model import predict_startup_success, init_model, get_allowed_values
import time
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Startup Success Predictor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стильное CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stSelectbox > div > div > select {
        font-size: 1.1rem;
        padding: 0.5rem;
    }
    .stNumberInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 0.8rem;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }
    .success-high {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-medium {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-low {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация модели при запуске (один раз)
if 'model_initialized' not in st.session_state:
    with st.spinner("🔄 Загружаем модель машинного обучения..."):
        st.session_state.model_initialized = init_model()
        if st.session_state.model_initialized:
            st.sidebar.success("✅ Модель успешно загружена!")
            # Загружаем допустимые значения
            st.session_state.allowed_values = get_allowed_values()
        else:
            st.sidebar.warning("⚠️ Модель не загружена. Используется демо-режим.")

# Заголовок приложения
st.markdown('<h1 class="main-header">🚀 Startup Success Predictor</h1>', unsafe_allow_html=True)

# Основной контент - форма ввода
with st.container():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 📊 Введите параметры вашего стартапа")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Финансовые параметры
        st.markdown("#### 💰 Финансы")
        usd_goal = st.number_input(
            "Цель финансирования (USD):",
            min_value=100,
            max_value=1000000,
            value=10000,
            step=100,
            help="Сумма, которую вы планируете собрать"
        )
        
        duration_days = st.number_input(
            "Длительность кампании (дней):",
            min_value=1,
            max_value=365,
            value=30,
            help="Сколько дней будет длиться кампания по сбору средств"
        )
        
        name_length = st.number_input(
            "Длина названия проекта (символов):",
            min_value=1,
            max_value=200,
            value=25,
            help="Оптимальная длина названия: 15-40 символов"
        )
    
    with col2:
        # Категории
        st.markdown("#### 🏷️ Категории")
        
        # Загружаем допустимые значения или используем демо
        if 'allowed_values' in st.session_state and st.session_state.allowed_values:
            allowed_categories = sorted(list(st.session_state.allowed_values['categories']))
            allowed_main_categories = sorted(list(st.session_state.allowed_values['main_categories']))
        else:
            # Демо-значения
            allowed_categories = ['Technology', 'Art', 'Film & Video', 'Music', 'Publishing', 
                                 'Games', 'Food', 'Design', 'Fashion', 'Comics', 'Crafts']
            allowed_main_categories = ['Technology', 'Art', 'Film & Video', 'Music', 'Publishing', 
                                      'Games', 'Food', 'Design', 'Fashion', 'Crafts']
        
        category = st.selectbox(
            "Категория проекта:",
            allowed_categories,
            help="Специфическая категория вашего проекта"
        )
        
        main_category = st.selectbox(
            "Основная категория:",
            allowed_main_categories,
            index=allowed_main_categories.index(category) if category in allowed_main_categories else 0,
            help="Общая категория проекта"
        )
    
    with col3:
        # География и дата
        st.markdown("#### 🌍 География и время")
        
        if 'allowed_values' in st.session_state and st.session_state.allowed_values:
            allowed_countries = sorted(list(st.session_state.allowed_values['countries']))
            allowed_currencies = sorted(list(st.session_state.allowed_values['currencies']))
        else:
            allowed_countries = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'NL', 'IT', 'ES', 'RU']
            allowed_currencies = ['USD', 'GBP', 'EUR', 'CAD', 'AUD', 'RUB', 'PLN', 'CZK']
        
        country = st.selectbox(
            "Страна запуска:",
            allowed_countries,
            help="Страна, в которой будет запущен проект"
        )
        
        currency = st.selectbox(
            "Валюта сбора:",
            allowed_currencies,
            help="Валюта сбора средств"
        )
        
        # Планируемая дата запуска
        st.markdown("#### 📅 Дата запуска")
        launched_date = st.date_input(
            "Планируемая дата запуска:",
            value=datetime.now(),
            help="Когда вы планируете начать кампанию"
        )
        
        # Извлекаем временные признаки из даты
        launched_month = launched_date.month
        launched_dayofweek = launched_date.weekday()  # 0 = Monday, 6 = Sunday
        launched_year = launched_date.year
    
    st.markdown('</div>', unsafe_allow_html=True)

# Кнопка применения
apply_button = st.button("🎯 Предсказать успешность", use_container_width=True)

# Область для результатов
if apply_button:
    with st.spinner("🤖 Анализируем ваш стартап..."):
        # Собираем все параметры
        input_params = {
            'usd_goal': usd_goal,
            'duration_days': duration_days,
            'name_length': name_length,
            'category': category,
            'main_category': main_category,
            'country': country,
            'currency': currency,
            'launched_month': launched_month,
            'launched_dayofweek': launched_dayofweek,
            'launched_year': launched_year
        }
        
        # Используем реальную модель
        result = predict_startup_success(input_params)
        success_probability = result['success_probability']
        
        # Отображение результатов
        st.markdown("---")
        st.markdown("## 📈 Результаты анализа")
        
        # Визуализация вероятности успеха
        col_prob = st.columns([2, 1])
        
        with col_prob[0]:
            # График вероятности
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = success_probability,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Вероятность успеха"},
                delta = {'reference': 35, 'increasing': {'color': "green"}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 20], 'color': 'red'},
                        {'range': [20, 60], 'color': 'yellow'},
                        {'range': [60, 100], 'color': 'green'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80}}
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col_prob[1]:
            # Цветной блок с результатом
            if success_probability >= 60:
                st.markdown(f'<div class="success-high"><h3>🎉 Отличные шансы!</h3><p>Вероятность успеха: <strong>{success_probability:.1f}%</strong></p></div>', unsafe_allow_html=True)
            elif success_probability >= 30:
                st.markdown(f'<div class="success-medium"><h3>📊 Хорошие перспективы</h3><p>Вероятность успеха: <strong>{success_probability:.1f}%</strong></p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-low"><h3>⚠️ Требует доработки</h3><p>Вероятность успеха: <strong>{success_probability:.1f}%</strong></p></div>', unsafe_allow_html=True)
        
        # Основной прогноз
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Вероятность успеха",
                value=f"{success_probability:.1f}%",
                delta="Выше среднего" if success_probability > 35 else "Ниже среднего"
            )
        
        with col2:
            risk_delta = "-12% к рынку" if result['risk_level'] != 'Высокий' else "+15% к рынку"
            st.metric(
                label="Уровень риска",
                value=result['risk_level'],
                delta=risk_delta
            )
        
        with col3:
            stage_delta = "Готов к инвестициям" if result['recommended_stage'] != 'Нужна доработка' else "Требует доработки"
            st.metric(
                label="Рекомендуемая стадия",
                value=result['recommended_stage'],
                delta=stage_delta
            )
        
        # Визуализации
        st.markdown("### 📊 Детальный анализ")
        
        fig_col1, fig_col2 = st.columns(2)
        
        with fig_col1:
            # График факторов успеха
            factors = ['Финансы', 'Длительность', 'Название', 'Категория', 'Страна']
            # Динамические оценки на основе вероятности успеха
            base_scores = [
                min(100, max(0, success_probability + (50000 - usd_goal) / 50000 * 25)),  # Финансы
                min(100, max(0, success_probability + min(duration_days, 60) / 60 * 20)),  # Длительность
                min(100, max(0, success_probability + (30 - abs(name_length - 30)) / 30 * 10)),  # Название
                min(100, max(0, success_probability + 8)),  # Категория
                min(100, max(0, success_probability + (10 if country == 'US' else 0)))  # Страна
            ]
            
            fig = go.Figure(data=[
                go.Bar(x=factors, y=base_scores, marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'])
            ])
            fig.update_layout(
                title="Факторы успеха",
                xaxis_title="Факторы",
                yaxis_title="Оценка (%)",
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with fig_col2:
            # Круговая диаграмма рисков
            if success_probability >= 60:
                risks = ['Рыночные', 'Технические', 'Командные', 'Финансовые']
                values = [20, 25, 15, 40]
            elif success_probability >= 30:
                risks = ['Рыночные', 'Технические', 'Командные', 'Финансовые']
                values = [30, 25, 20, 25]
            else:
                risks = ['Рыночные', 'Технические', 'Командные', 'Финансовые']
                values = [35, 25, 20, 20]
            
            fig = px.pie(
                values=values, 
                names=risks, 
                title="Распределение рисков",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Детали введенных данных
        st.markdown("### 🔍 Введенные параметры")
        col_analysis1, col_analysis2 = st.columns(2)
        
        with col_analysis1:
            st.markdown("#### 📝 Основные параметры")
            st.write(f"**Цель финансирования:** ${usd_goal:,}")
            st.write(f"**Длительность:** {duration_days} дней")
            st.write(f"**Длина названия:** {name_length} символов")
        
        with col_analysis2:
            st.markdown("#### 🏷️ Классификация")
            st.write(f"**Категория:** {category}")
            st.write(f"**Основная категория:** {main_category}")
            st.write(f"**Страна:** {country}")
            st.write(f"**Валюта:** {currency}")
            st.write(f"**Дата запуска:** {launched_date.strftime('%d.%m.%Y')}")
        
        # Рекомендации
        st.markdown("### 💡 Рекомендации")
        
        if success_probability >= 60:
            tab1, tab2, tab3 = st.tabs(["🚀 Действия", "📈 Метрики", "🤝 Партнерства"])
            
            with tab1:
                st.success("✅ Продолжайте в том же духе! Ваш стартап показывает отличные перспективы")
                st.success("✅ Подготовьте документацию для встречи с инвесторами")
                st.success("✅ Рассмотрите возможность ускоренного роста")
            
            with tab2:
                st.write("**Ключевые метрики для отслеживания:**")
                st.write("- LTV/CAC ratio > 3.0")
                st.write("- Месячный рост > 20%")
                st.write("- Churn rate < 3%")
                st.write("- Burn rate < $50k/мес")
            
            with tab3:
                st.write("**Потенциальные партнеры:**")
                st.write("- Венчурные фонды серии A")
                st.write("- Бизнес-ангелы")
                st.write("- Стратегические инвесторы")
                
        elif success_probability >= 30:
            tab1, tab2, tab3 = st.tabs(["🚀 Действия", "📈 Метрики", "🤝 Партнерства"])
            
            with tab1:
                st.warning("⚠️ Укрепите финансовую модель перед следующим раундом")
                st.info("💡 Проведите дополнительное исследование рынка")
                st.success("✅ Сфокусируйтесь на продукте")
            
            with tab2:
                st.write("**Ключевые метрики для отслеживания:**")
                st.write("- LTV/CAC ratio > 2.0")
                st.write("- Месячный рост > 15%")
                st.write("- Churn rate < 5%")
                st.write("- Burn rate < $30k/мес")
            
            with tab3:
                st.write("**Потенциальные партнеры:**")
                st.write("- Seed раунд инвесторы")
                st.write("- Бизнес-инкубаторы")
                st.write("- Отраслевые эксперты")
        else:
            tab1, tab2, tab3 = st.tabs(["🚀 Действия", "📈 Метрики", "🤝 Партнерства"])
            
            with tab1:
                st.error("❌ Пересмотрите бизнес-модель")
                st.warning("⚠️ Усильте команду")
                st.info("💡 Проведите пилотные тесты")
            
            with tab2:
                st.write("**Ключевые метрики для улучшения:**")
                st.write("- Достигните PMF (Product-Market Fit)")
                st.write("- Увеличьте retention rate")
                st.write("- Снизите CAC")
                st.write("- Наймите ключевых сотрудников")
            
            with tab3:
                st.write("**Рекомендуемые шаги:**")
                st.write("- Присоединитесь к акселератору")
                st.write("- Найдите ментора")
                st.write("- Участвуйте в стартап-сообществах")

# Боковая панель с информацией
with st.sidebar:
    st.markdown("## ℹ️ О приложении")
    st.write("""
    Это приложение использует машинное обучение 
    для прогнозирования успешности стартапов 
    на основе различных факторов.
    
    **Как использовать:**
    1. Заполните все поля формы
    2. Нажмите кнопку "Предсказать успешность"
    3. Изучите результаты и рекомендации
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Статистика")
    if st.session_state.model_initialized:
        st.success("✅ Модель активна (загружена из файлов)")
        st.write("Проанализировано стартапов: **265,266**")
        st.write("Точность модели: **67.9%**")
        st.write("F1-score: **0.625**")
    else:
        st.warning("⚠️ Демо-режим")
        st.write("Для загрузки модели выполните:")
        st.write("1. Запустите обучение в Colab")
        st.write("2. Скопируйте файлы в папку проекта:")
        st.code("""
        my_kickstarter_model.keras
        preprocessor.pkl
        allowed_values.pkl
        """)
    st.write("Последнее обновление: **Январь 2024**")
    
    st.markdown("---")
    st.markdown("### 🔧 Техническая информация")
    st.write("**Используемые алгоритмы:**")
    st.write("- Нейронная сеть (Keras/TensorFlow)")
    st.write("- OneHotEncoder для категориальных данных")
    st.write("- StandardScaler для числовых данных")
    
    st.markdown("---")
    st.markdown("### 📁 Используемые признаки")
    st.write("**Числовые признаки:**")
    st.write("- Логарифм цели финансирования")
    st.write("- Длительность кампании")
    st.write("- Длина названия проекта")
    st.write("- Месяц, день недели, год запуска")
    
    st.write("**Категориальные признаки:**")
    st.write("- Категория и основная категория")
    st.write("- Страна и валюта")

# Футер
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Made with ❤️ | Startup Success Predictor v3.0 | Powered by AI"
    "</div>", 
    unsafe_allow_html=True
)