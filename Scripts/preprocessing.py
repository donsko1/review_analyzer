import re
import pandas as pd
from pathlib import Path
import nltk
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer
from Configs import CurrentApp

class TextCleaner:
    def __init__(self, game: CurrentApp, min_words=4, use_lemmatization=True):
        input_dir='data'
        output_dir='data'
        self.app_id = game.app_id
        self.language = game.language
        self.mood = game.mood
        self.min_words = min_words  # Новый параметр
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.use_lemmatization = use_lemmatization
        self.lemmatizer = None
        if self.use_lemmatization:
            if self.language == 'russian':
                self.lemmatizer = MorphAnalyzer()
            elif self.language == 'english':
                self.lemmatizer = WordNetLemmatizer()
            else:
                print(f"Лемматизация не поддерживается для языка: {self.language}")
        self.input_file = self.input_dir / f"{game.app_id}_{game.language}_{game.mood}_reviews.csv"
        self.output_file = self.output_dir / f"{game.app_id}_{game.language}_{game.mood}_cleaned_reviews.csv"

    def _lemmatize_text(self, text):
        """Лемматизация текста с учетом языка"""
        if not self.lemmatizer or not isinstance(text, str):
            return text
            
        tokens = text.split()
        lemmatized = []
        
        for token in tokens:
            # Для русского языка
            if self.language == 'russian':
                lemma = self.lemmatizer.parse(token)[0].normal_form
            # Для английского языка
            elif self.language == 'english':
                lemma = self.lemmatizer.lemmatize(token)
            else:
                lemma = token
                
            lemmatized.append(lemma)
            
        return ' '.join(lemmatized)

    @staticmethod
    def _remove_bbcodes(text):
        """Удаляет BB-коды вида [h1], [/?tag] и подобные"""
        if not isinstance(text, str):
            return text
            
        # Исправленное регулярное выражение
        pattern = r'\[/?[^\]]+\]'
        return re.sub(pattern, '', text, flags=re.IGNORECASE)

    @staticmethod
    def _remove_special_chars(text):
        """Очищает специальные символы и форматирование"""
        if not isinstance(text, str):
            return text
            
        replacements = [
            (r'\n+', '. '),    # Замена переносов строк
            (r'\t+', ' '),     # Удаление табов
            (r'\.(?! )', '. '),# Добавление пробелов после точек
            (r'\s+\.', '.'),   # Удаление пробелов перед точками
            (r'\s+', ' '),     # Удаление множественных пробелов
            (r'\s*\.\s*', '. ')# Нормализация пробелов вокруг точек
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
            
        return text.strip()

    @staticmethod
    def _replace_hearts(text):
        """Заменяет сердечки на PAD"""
        return re.sub(r"[♥]+", ' **** ', text) if isinstance(text, str) else text

    def _clean_text(self, text):
        """Основной пайплайн очистки текста"""
        cleaners = [
            self._remove_bbcodes,
            self._replace_hearts,
            self._remove_special_chars
        ]
        
        for cleaner in cleaners:
            text = cleaner(text)
            
        return text

    def process(self):
        """Основной метод обработки файла"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Загрузка данных
        reviews = pd.read_csv(self.input_file)
        
        # Очистка текста
        reviews['review'] = reviews['review'].apply(self._clean_text)
        
        # НОВЫЙ БЛОК: Фильтрация коротких комментариев
        def count_words(text):
            if not isinstance(text, str):
                return 0
            return len([word for word in text.split() if word.strip()])
            
        reviews['word_count'] = reviews['review'].apply(count_words)
        initial_count = len(reviews)
        reviews = reviews[reviews['word_count'] >= self.min_words].drop(columns=['word_count'])
        removed_count = initial_count - len(reviews)
        
        # Сохранение
        reviews.to_csv(self.output_file, index=False, encoding='utf-8')
