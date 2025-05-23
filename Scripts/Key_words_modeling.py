import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import json
from nltk.corpus import stopwords
import nltk
from pathlib import Path
from Configs import CurrentApp
from wordcloud import WordCloud

class LDAProcessor:
    def __init__(self, game: CurrentApp, n_topics=5, threshold=0.1, max_features=1000):
        self.n_topics = n_topics
        self.threshold = threshold
        self.app_id = game.app_id
        self.language = game.language
        self.data_dir = Path("data") # Указываем прямо на папку data
        
        # Проверка и загрузка NLTK стоп-слов
        try:
            nltk.data.find(f'corpora/stopwords')
        except LookupError:
            print(f"Downloading NLTK 'stopwords' corpus for {self.language}...")
            nltk.download('stopwords')
        
        try:
            self.stop_words = stopwords.words(self.language)
        except OSError: # Если язык не поддерживается стоп-словами NLTK
            print(f"No stopwords found for language '{self.language}'. Proceeding without stopwords.")
            self.stop_words = [] # Пустой список, если стоп-слов нет

        self.vectorizer = CountVectorizer(
            max_df=0.95,        # Игнорировать слова, которые появляются более чем в 95% документов
            min_df=2,           # Игнорировать слова, которые появляются менее чем в 2 документах
            stop_words=self.stop_words,
            max_features=max_features # Ограничить количество фичей
        )
        # LDA модель будет инициализирована внутри process() для каждого набора данных отдельно

    def _generate_single_wordcloud(self, text_data: str, sentiment_label: str):
        """
        Генерирует облако слов для данного текста и сохраняет его.
        :param text_data: Строка, содержащая весь текст для облака слов.
        :param sentiment_label: 'positive' или 'negative', для имени файла.
        """
        if not text_data.strip():
            print(f"No text data provided for {sentiment_label} wordcloud. Skipping.")
            return

        wc = WordCloud(
            width=1600, height=1200,
            background_color='white',
            stopwords=set(self.stop_words) # Используем set для быстрого поиска стоп-слов
        ).generate(text_data)

        # Сохраняем в папку data, как указано
        output_path = self.data_dir / f"{self.app_id}_{self.language}_{sentiment_label}_wordcloud.png"
        output_path.parent.mkdir(parents=True, exist_ok=True) # Гарантируем, что папка data существует
        wc.to_file(str(output_path))
        print(f"Wordcloud saved to: {output_path}")

    def _get_topic_keywords(self, lda_model, topic_idx: int, feature_names: list, n_words=10) -> list:
        """
        Извлекает топ ключевых слов для заданной темы.
        :param lda_model: Обученная LDA модель.
        :param topic_idx: Индекс темы.
        :param feature_names: Список всех фичей (слов) из векторизатора.
        :param n_words: Количество топ-слов для извлечения.
        :return: Список ключевых слов.
        """
        return [feature_names[i] 
                for i in lda_model.components_[topic_idx].argsort()[-n_words:]]

    def _assign_to_topics(self, topic_dict: dict, review_id: str, prob_vector: list):
        """
        Присваивает ID отзыва теме, если вероятность принадлежности выше порога.
        :param topic_dict: Словарь тем, куда добавляются ID отзывов.
        :param review_id: ID отзыва.
        :param prob_vector: Вектор вероятностей принадлежности отзыва к каждой теме.
        """
        for topic_idx, prob in enumerate(prob_vector):
            if prob >= self.threshold:
                if topic_idx in topic_dict: # Убедимся, что тема существует
                    topic_dict[topic_idx]["recommendationid"].append(str(review_id))

    def process(self):
        """
        Основной метод обработки. Теперь обрабатывает позитивные и негативные отзывы отдельно.
        """
        self.data_dir.mkdir(parents=True, exist_ok=True) # Убедимся, что папка data существует

        sentiments = ['positive', 'negative']

        for sentiment in sentiments:
            input_file = self.data_dir / f'{self.app_id}_{self.language}_{sentiment}_cleaned_reviews.csv'
            output_json_file = self.data_dir / f'{self.app_id}_{self.language}_{sentiment}_topics.json'

            print(f"\n--- Processing {sentiment} reviews ---")

            if not input_file.exists():
                print(f"Warning: Cleaned reviews file not found for {sentiment} reviews: {input_file}. Skipping LDA for this sentiment.")
                # Создаем пустой JSON файл тем, если данных нет, чтобы избежать ошибок на следующих этапах
                with open(output_json_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                continue

            df = pd.read_csv(input_file, dtype={'recommendationid': str})

            if df.empty or df['review'].isnull().all() or not df['review'].str.strip().any():
                print(f"No valid reviews to process for {sentiment} sentiment after cleaning. Skipping LDA and wordcloud.")
                # Создаем пустой JSON файл тем
                with open(output_json_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                continue

            # Убедимся, что столбец 'review' содержит строки и заполняем NaN пустой строкой
            df['review'] = df['review'].astype(str).fillna('')
            
            # Генерация облака слов для текущего настроения
            full_text_corpus = " ".join(df['review'])
            self._generate_single_wordcloud(full_text_corpus, sentiment)

            # Выполняем векторизацию
            try:
                doc_term_matrix = self.vectorizer.fit_transform(df['review'])
                feature_names = self.vectorizer.get_feature_names_out()
            except ValueError as e:
                print(f"Error during vectorization for {sentiment} reviews: {e}. This might happen if all reviews are too short or consist only of stopwords. Skipping LDA topic modeling.")
                with open(output_json_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                continue

            # Проверяем, есть ли какие-либо признаки для LDA
            if doc_term_matrix.shape[1] == 0:
                print(f"No features extracted for {sentiment} reviews after vectorization. This might mean all reviews are too short or consist only of stopwords. Skipping LDA topic modeling.")
                with open(output_json_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                continue

            # Инициализируем и обучаем LDA модель для текущего настроения
            lda_model = LatentDirichletAllocation(n_components=self.n_topics, random_state=42)
            topic_probabilities = lda_model.fit_transform(doc_term_matrix)

            # Создаем словарь тем для текущего настроения
            current_topic_dict = {}
            for topic_idx in range(self.n_topics):
                top_keywords = self._get_topic_keywords(lda_model, topic_idx, feature_names)
                current_topic_dict[topic_idx] = {
                    "keywords": top_keywords,
                    "recommendationid": []
                }
            
            # Присваиваем отзывы темам
            for doc_idx, prob_vector in enumerate(topic_probabilities):
                review_id = df.iloc[doc_idx]['recommendationid']
                self._assign_to_topics(current_topic_dict, review_id, prob_vector)

            # Сохраняем словарь тем
            with open(output_json_file, 'w', encoding='utf-8') as f:
                json.dump(current_topic_dict, f, ensure_ascii=False, indent=4)
            print(f"Topics JSON saved to: {output_json_file}")