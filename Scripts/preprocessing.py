import re
import pandas as pd
from pathlib import Path
import nltk
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer
from Configs import CurrentApp # Предполагается, что CurrentApp имеет app_id, language, mood

class TextCleaner:
    def __init__(self, game: CurrentApp, min_words=4, use_lemmatization=True):
        input_dir='data'
        output_dir='data'
        self.app_id = game.app_id
        self.language = game.language
        # self.mood теперь не используется для определения имени ВЫХОДНОГО файла,
        # так как всегда будем пытаться обработать и positive, и negative.
        # Однако, оно может быть использовано для фильтрации данных для LDA, если это потребуется позже.
        self.mood = game.mood 
        self.min_words = min_words
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.use_lemmatization = use_lemmatization
        self.lemmatizer = None
        
        # Проверка и загрузка необходимых ресурсов NLTK
        try:
            if self.language == 'russian':
                pass # PyMorphy2 не требует загрузки ресурсов NLTK
            elif self.language == 'english':
                try:
                    nltk.data.find('corpora/wordnet')
                except LookupError:
                    print("Downloading NLTK 'wordnet' corpus...")
                    nltk.download('wordnet')
                try:
                    nltk.data.find('corpora/omw-1.4') # Open Multilingual Wordnet, often needed with wordnet
                except LookupError:
                    print("Downloading NLTK 'omw-1.4' corpus...")
                    nltk.download('omw-1.4')
            else:
                print(f"Лемматизация не поддерживается для языка: {self.language}")
        except Exception as e:
            print(f"Ошибка при загрузке NLTK ресурсов: {e}")

        if self.use_lemmatization:
            if self.language == 'russian':
                self.lemmatizer = MorphAnalyzer()
            elif self.language == 'english':
                self.lemmatizer = WordNetLemmatizer()
            # Если язык не русский и не английский, lemmatizer останется None

    def _lemmatize_text(self, text):
        """Лемматизация текста с учетом языка"""
        if not self.lemmatizer or not isinstance(text, str):
            return text
            
        tokens = text.split()
        lemmatized = []
        
        for token in tokens:
            if self.language == 'russian':
                # PyMorphy2: parse возвращает список морфологических анализов, берем первый (наиболее вероятный)
                lemma = self.lemmatizer.parse(token)[0].normal_form
            elif self.language == 'english':
                # WordNetLemmatizer: по умолчанию лемматизирует как существительное.
                # Для лучшей лемматизации можно добавить POS-теггинг (например, 'n', 'v', 'a', 'r').
                lemma = self.lemmatizer.lemmatize(token) 
            else:
                lemma = token # Если язык не поддерживается, токен возвращается без изменений
                
            lemmatized.append(lemma)
            
        return ' '.join(lemmatized)

    @staticmethod
    def _remove_bbcodes(text):
        """Удаляет BB-коды вида [h1], [/?tag] и подобные"""
        if not isinstance(text, str):
            return text
            
        pattern = r'\[/?[^\]]+\]'
        return re.sub(pattern, '', text, flags=re.IGNORECASE)

    @staticmethod
    def _remove_special_chars(text):
        """Очищает специальные символы и форматирование"""
        if not isinstance(text, str):
            return text
            
        replacements = [
            (r'\n+', '. '),    # Замена переносов строк на точку с пробелом
            (r'\t+', ' '),     # Удаление табов
            (r'\.(?! )', '. '),# Добавление пробелов после точек, если его нет
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
        
        # Лемматизация применяется после основной очистки
        text = self._lemmatize_text(text)
        
        return text

    def process(self):
        """
        Основной метод обработки файла.
        Теперь обрабатывает позитивные и негативные отзывы отдельно и сохраняет их в отдельные файлы.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Вспомогательная функция для подсчета слов
        def count_words(text):
            if not isinstance(text, str):
                return 0
            return len([word for word in text.split() if word.strip()])

        # --- Обработка позитивных отзывов ---
        positive_input_path = self.input_dir / f"{self.app_id}_{self.language}_positive_reviews.csv"
        positive_output_path = self.output_dir / f"{self.app_id}_{self.language}_positive_cleaned_reviews.csv"

        if positive_input_path.exists():
            print(f"Processing positive reviews from: {positive_input_path}")
            positive_df = pd.read_csv(positive_input_path, dtype={'recommendationid': str})
            
            # Очистка текста
            positive_df['review'] = positive_df['review'].apply(self._clean_text)
            
            # Фильтрация коротких комментариев
            initial_count = len(positive_df)
            positive_df['word_count'] = positive_df['review'].apply(count_words)
            positive_df = positive_df[positive_df['word_count'] >= self.min_words].drop(columns=['word_count'])
            removed_count = initial_count - len(positive_df)
            print(f"Removed {removed_count} short positive reviews (less than {self.min_words} words).")
            
            # Сохранение очищенных позитивных отзывов
            positive_df.to_csv(positive_output_path, index=False, encoding='utf-8')
            print(f"Cleaned positive reviews saved to: {positive_output_path}")
        else:
            print(f"Warning: Positive reviews file not found at {positive_input_path}. Skipping positive review cleaning.")
            
        # --- Обработка негативных отзывов ---
        negative_input_path = self.input_dir / f"{self.app_id}_{self.language}_negative_reviews.csv"
        negative_output_path = self.output_dir / f"{self.app_id}_{self.language}_negative_cleaned_reviews.csv"

        if negative_input_path.exists():
            print(f"Processing negative reviews from: {negative_input_path}")
            negative_df = pd.read_csv(negative_input_path, dtype={'recommendationid': str})

            # Очистка текста
            negative_df['review'] = negative_df['review'].apply(self._clean_text)
            
            # Фильтрация коротких комментариев
            initial_count = len(negative_df)
            negative_df['word_count'] = negative_df['review'].apply(count_words)
            negative_df = negative_df[negative_df['word_count'] >= self.min_words].drop(columns=['word_count'])
            removed_count = initial_count - len(negative_df)
            print(f"Removed {removed_count} short negative reviews (less than {self.min_words} words).")
            
            # Сохранение очищенных негативных отзывов
            negative_df.to_csv(negative_output_path, index=False, encoding='utf-8')
            print(f"Cleaned negative reviews saved to: {negative_output_path}")
        else:
            print(f"Warning: Negative reviews file not found at {negative_input_path}. Skipping negative review cleaning.")