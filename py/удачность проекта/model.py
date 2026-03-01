import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import os
from datetime import datetime

class StartupPredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.allowed_categories = None
        self.allowed_main_categories = None
        self.allowed_countries = None
        self.allowed_currencies = None
        
    def load_saved_model(self):
        """Загрузка сохраненной модели и препроцессора"""
        try:
            # Проверяем наличие всех необходимых файлов
            required_files = [
                "my_kickstarter_model.keras",
                "preprocessor.pkl", 
                "allowed_values.pkl"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                print(f"⚠️ Отсутствуют файлы модели: {missing_files}")
                print("Запустите обучение в Colab и скопируйте файлы в папку проекта")
                return False
            
            # Загружаем модель
            print("🔄 Загружаем модель...")
            self.model = load_model("my_kickstarter_model.keras")
            
            # Загружаем препроцессор
            print("🔄 Загружаем препроцессор...")
            self.preprocessor = joblib.load("preprocessor.pkl")
            
            # Загружаем допустимые значения
            print("🔄 Загружаем допустимые значения...")
            allowed_values = joblib.load("allowed_values.pkl")
            
            self.allowed_categories = allowed_values['categories']
            self.allowed_main_categories = allowed_values['main_categories']
            self.allowed_countries = allowed_values['countries']
            self.allowed_currencies = allowed_values['currencies']
            
            print("✅ Модель успешно загружена!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            print("ℹ️ Переключаемся в демо-режим")
            return False
    
    def predict_success(self, input_data):
        """Предсказание успешности стартапа"""
        try:
            if self.model is None or self.preprocessor is None:
                print("⚠️ Модель не загружена, используем демо-режим")
                return self.demo_prediction(input_data)
            
            # Получаем параметры
            usd_goal = input_data.get('usd_goal', 10000)
            duration_days = input_data.get('duration_days', 30)
            name_length = input_data.get('name_length', 25)
            category = input_data.get('category', 'Technology')
            main_category = input_data.get('main_category', 'Technology')
            country = input_data.get('country', 'US')
            currency = input_data.get('currency', 'USD')
            launched_month = input_data.get('launched_month', datetime.now().month)
            launched_dayofweek = input_data.get('launched_dayofweek', datetime.now().weekday())
            launched_year = input_data.get('launched_year', datetime.now().year)
            
            # КОРРЕКЦИЯ: Ограничиваем длину названия (больше 25 - плохо)
            name_length_adj = min(name_length, 25)
            
            # Логарифм цели финансирования
            usd_goal_log = np.log1p(usd_goal)
            
            # Создаем DataFrame
            input_df = pd.DataFrame([{
                'usd_goal_real_log': usd_goal_log,
                'duration_days': duration_days,
                'name_length_adj': name_length_adj,  # Используем скорректированную длину
                'launched_month': launched_month,
                'launched_dayofweek': launched_dayofweek,
                'launched_year': launched_year,
                'category': category,
                'main_category': main_category,
                'country': country,
                'currency': currency
            }])
            
            # Преобразуем данные
            input_processed = self.preprocessor.transform(input_df)
            
            # Конвертируем если нужно
            if hasattr(input_processed, "toarray"):
                input_processed = input_processed.toarray()
            
            # Предсказание
            probability = self.model.predict(input_processed, verbose=0)[0][0]
            
            return {
                'success_probability': float(probability * 100),
                'risk_level': 'Высокий' if probability < 0.3 else 'Средний' if probability < 0.6 else 'Низкий',
                'recommended_stage': 'Seed Round' if probability > 0.55 else 'Pre-seed' if probability > 0.3 else 'Нужна доработка'
            }
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            return self.demo_prediction(input_data)
    
    def demo_prediction(self, input_data):
        """Демо-предсказание с учетом ограничений"""
        usd_goal = input_data.get('usd_goal', 10000)
        duration_days = input_data.get('duration_days', 30)
        name_length = input_data.get('name_length', 25)
        category = input_data.get('category', 'Technology')
        main_category = input_data.get('main_category', 'Technology')
        country = input_data.get('country', 'US')
        currency = input_data.get('currency', 'USD')
        
        # КОРРЕКЦИЯ: Ограничиваем длину названия (больше 25 - плохо)
        name_length_adj = min(name_length, 25)
        
        # Базовые коэффициенты
        country_coefficients = {
            'US': 1.00, 'GB': 0.85, 'CA': 0.80, 'AU': 0.75,
            'DE': 0.70, 'FR': 0.65, 'NL': 0.60, 'IT': 0.55,
            'ES': 0.50, 'RU': 0.30, 'PL': 0.40, 'CZ': 0.45,
            'JP': 0.65, 'KR': 0.60, 'IN': 0.35, 'BR': 0.40, 'MX': 0.45
        }
        
        category_coefficients = {
            'Technology': 1.2, 'Games': 1.1, 'Comics': 1.0,
            'Design': 0.9, 'Film & Video': 0.8, 'Music': 0.7,
            'Publishing': 0.7, 'Art': 0.6, 'Food': 0.6,
            'Fashion': 0.5, 'Crafts': 0.4, 'Other': 0.7
        }
        
        # Базовая вероятность
        country_coef = country_coefficients.get(country, 0.5)
        category_coef = category_coefficients.get(category, 0.7)
        base_prob = 35 * country_coef * category_coef
        
        # КОРРЕКЦИЯ: Больше дней = больше шансов (линейная зависимость до 90 дней)
        duration_factor = min(duration_days, 90) * 0.33  # ~30% за 90 дней
        
        # КОРРЕКЦИЯ: Длина названия (больше 25 - плохо)
        if name_length_adj <= 25:
            name_factor = (name_length_adj / 25) * 10  # до +10% за оптимальную длину
        else:
            name_factor = -10  # штраф за слишком длинное название
        
        # Корректировка на цель финансирования
        if usd_goal < 1000:
            goal_factor = 20
        elif usd_goal < 5000:
            goal_factor = 15
        elif usd_goal < 10000:
            goal_factor = 10
        elif usd_goal < 20000:
            goal_factor = 5
        elif usd_goal < 50000:
            goal_factor = 0
        elif usd_goal < 100000:
            goal_factor = -10
        else:
            goal_factor = -20
        
        # Итоговая вероятность
        final_prob = base_prob + goal_factor + duration_factor + name_factor
        final_prob = max(1, min(95, final_prob))
        
        return {
            'success_probability': final_prob,
            'risk_level': 'Высокий' if final_prob < 30 else 'Средний' if final_prob < 60 else 'Низкий',
            'recommended_stage': 'Seed Round' if final_prob > 55 else 'Pre-seed' if final_prob > 30 else 'Нужна доработка'
        }

# Глобальный экземпляр predictor
predictor = StartupPredictor()

def init_model():
    """Инициализация модели (загрузка сохраненной)"""
    try:
        # Просто загружаем сохраненную модель
        success = predictor.load_saved_model()
        
        if success:
            print("✅ Модель загружена из сохраненных файлов")
        else:
            print("⚠️ Модель не загружена, используется демо-режим")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка инициализации модели: {e}")
        return False

def get_allowed_values():
    """Возвращает допустимые значения для выпадающих списков"""
    if predictor.allowed_categories is not None:
        return {
            'categories': predictor.allowed_categories,
            'main_categories': predictor.allowed_main_categories,
            'countries': predictor.allowed_countries,
            'currencies': predictor.allowed_currencies
        }
    
    # Демо-значения если модель не загружена
    print("⚠️ Используем демо-значения категорий")
    return {
        'categories': {'Technology', 'Art', 'Film & Video', 'Music', 'Publishing', 
                      'Games', 'Food', 'Design', 'Fashion', 'Comics', 'Crafts', 'Other'},
        'main_categories': {'Technology', 'Art', 'Film & Video', 'Music', 'Publishing', 
                           'Games', 'Food', 'Design', 'Fashion', 'Crafts'},
        'countries': {'US', 'GB', 'CA', 'AU', 'DE', 'FR', 'NL', 'IT', 'ES', 'RU', 'PL', 'CZ', 'JP', 'KR', 'IN', 'BR', 'MX'},
        'currencies': {'USD', 'GBP', 'EUR', 'CAD', 'AUD', 'RUB', 'PLN', 'CZK', 'JPY', 'KRW', 'INR', 'BRL', 'MXN'}
    }

def predict_startup_success(input_params):
    """Основная функция для предсказания"""
    try:
        # Предсказание
        result = predictor.predict_success(input_params)
        return result
        
    except Exception as e:
        print(f"❌ Ошибка предсказания: {e}")
        # Возвращаем реалистичные демо-данные в случае ошибки
        return {
            'success_probability': 35.0,
            'risk_level': 'Средний',
            'recommended_stage': 'Pre-seed'
        }