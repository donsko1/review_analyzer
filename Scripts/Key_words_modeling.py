import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import json
from nltk.corpus import stopwords
import nltk
from pathlib import Path
from Configs import CurrentApp
import os
from wordcloud import WordCloud

class LDAProcessor:
    def __init__(self, game: CurrentApp, n_topics=5, threshold=0.1, max_features=1000):
        self.n_topics = n_topics
        self.threshold = threshold
        self.input_file = Path("data") / f'{game.app_id}_{game.language}_{game.mood}_cleaned_reviews.csv'.replace("/", "\\")
        self.output_file = Path("data") / f'{game.app_id}_{game.language}_{game.mood}_topics.json'.replace("/", "\\")
        try:
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                print("Не сработало")
                nltk.download('stopwords')
                
            self.stop_words = stopwords.words(game.language)
        except OSError:
            self.stop_words = []
        self.vectorizer = CountVectorizer(
            max_df=0.95, 
            min_df=2, 
            stop_words=self.stop_words,
            max_features=max_features
        )
        self.lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42
        )
        self.topic_dict = {}

    def generate_wordclouds(self, output_file="wordclouds/full_corpus.png"):
        df = pd.read_csv(self.input_file)
        text = " ".join(df['review'].astype(str))
        
        wc = WordCloud(
            width=1600, height=1200,
            background_color='white',
            stopwords=set(self.stop_words)
        ).generate(text)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wc.to_file(str(output_path))



    def process(self):
        self.df = pd.read_csv(
            self.input_file,
            dtype={'recommendationid': str}
        )
        doc_term_matrix = self.vectorizer.fit_transform(self.df['review'])
        self.topic_probabilities = self.lda.fit_transform(doc_term_matrix)
        self._create_topic_dict()
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.topic_dict, f, ensure_ascii=False, indent=4)
        return self

    def _create_topic_dict(self):
        feature_names = self.vectorizer.get_feature_names_out()
        
        for topic_idx in range(self.n_topics):
            top_keywords = self._get_topic_keywords(topic_idx, feature_names)
            self.topic_dict[topic_idx] = {
                "keywords": top_keywords,
                "recommendationid": []
            }

        for doc_idx, prob_vector in enumerate(self.topic_probabilities):
            review_id = self.df.iloc[doc_idx]['recommendationid']
            self._assign_to_topics(review_id, prob_vector)

    def _get_topic_keywords(self, topic_idx, feature_names, n_words=10):
        return [feature_names[i] 
                for i in self.lda.components_[topic_idx].argsort()[-n_words:]]

    def _assign_to_topics(self, review_id, prob_vector):
        for topic_idx, prob in enumerate(prob_vector):
            if prob >= self.threshold:
                self.topic_dict[topic_idx]["recommendationid"].append(str(review_id))
            