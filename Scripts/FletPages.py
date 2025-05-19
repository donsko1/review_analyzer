import flet as ft
from flet import RouteChangeEvent, CrossAxisAlignment, MainAxisAlignment, Text
import threading
from Key_words_modeling import LDAProcessor
from download_reviews import SteamReviewsLoader, SteamGameInfo
from preprocessing import TextCleaner
from deepseek import TopicAnalyzer
from Configs import CurrentApp
import Configs
from pathlib import Path
import pandas as pd
import json
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart
import matplotlib
import numpy as np

matplotlib.use("svg")

class AppController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_app = None
        self.page.on_route_change = self.route_change
        self.page.go(self.page.route)
    
    def route_change(self, e: RouteChangeEvent):
        route = self.page.route
        match route:
            case '/':
                self.page.views.clear()
                self.page.views.append(HomeScreen(self).build())
            case '/download_review':
                self.page.views.clear()
                self.page.views.append(DownloadScreen(self).build())
                threading.Thread(target=self.download_reviews).start()
            case '/analise':
                self.page.views.clear()
                self.page.views.append(AnalysisScreen(self).build())
                threading.Thread(target=self.analyze_data).start()
            case '/result':
                self.page.views.clear()
                self.page.views.append(ResultScreen(self).build())
            case '/game_info':
                self.page.views.clear()
                self.page.views.append(GameInfo(self).build())
        self.page.update()
    
    def load_game_info(self):
        loader = SteamGameInfo(self.current_app)
        info = loader.load()
        self.page.go('/game_info')

    def download_reviews(self):
        loader = SteamReviewsLoader(self.current_app)
        loader.load()
        self.page.go('/analise')
    
    def analyze_data(self):
        cleaner = TextCleaner(self.current_app)
        cleaner.process()
        processor = LDAProcessor(self.current_app)
        processor.process()
        processor.generate_wordclouds()
        analyzer = TopicAnalyzer(self.current_app)
        analyzer.analyze_topics()
        self.page.go('/result')
    
    def set_current_app(self, app_data):
        self.current_app = app_data
        self.page.client_storage.set("game_data", self.current_app.__dict__)

class GameInfo:
    def __init__(self, controller: AppController):
        self.controller = controller
    
    def build(self):
        app = self.controller.current_app
        info_path = Path("data") / f"{app.app_id}_{app.language}_info.csv".replace("/", "\\")
        if not info_path.exists():
            return ft.View(
                route='/game_info',
                controls=[ft.Text("Нет данных об игре. Сначала загрузите информацию.")],
            )
        
        df = pd.read_csv(info_path)

        name = df.loc[0, 'name']
        image_url = df.loc[0, 'header_image']


        return ft.View(
            route='/game_info',
            controls=[
                ft.AppBar(title=ft.Text('Инфо об игре'), bgcolor='black'),
                ft.Text(value=name, size=30, weight="bold"),
                ft.Image(src=image_url, width=300),
                ft.ElevatedButton(text='Далее: скачать отзывы', on_click=lambda e: self.controller.page.go('/download_review'))
            ],
            vertical_alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=26
        )
    
    

class HomeScreen:
    def __init__(self, controller: AppController):
        self.controller = controller
        self.app_id = ft.TextField(label='Вставьте AppID', width=200)
        self.language = ft.Dropdown(
            label='Выберите язык',
            width=200,
            options=[ft.dropdown.Option(lang) for lang in Configs.language_list]
        )
        self.mood = Configs.mood_list[2]  # <- теперь это просто строка, например 'positive'
        self.submit_button = ft.ElevatedButton(text='Старт', on_click=self.on_submit, disabled=True)

    def validate(self, e: ft.ControlEvent):
        self.submit_button.disabled = not all([self.app_id.value, self.language.value])
        self.controller.page.update()

    def on_submit(self, e: ft.ControlEvent):
        game = CurrentApp(
            self.app_id.value,
            self.language.value,
            self.mood,  # <- mood больше не UI-элемент
            Configs.day_range
        )
        self.controller.set_current_app(game)
        threading.Thread(target=self.controller.load_game_info).start()

    def build(self):
        self.app_id.on_change = self.validate
        self.language.on_change = self.validate

        return ft.View(
            route='/',
            controls=[
                ft.AppBar(title=ft.Text('Home'), bgcolor='black'),
                self.app_id,
                self.language,
                self.submit_button,
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=26
        )

    
class DownloadScreen:
    def __init__(self, controller: AppController):
        self.controller = controller
    
    def build(self):
        return ft.View(
            route='/download_review',
            controls=[
                ft.AppBar(title=Text('Загрузка отзывов'), bgcolor='black'),
                Text(value='Данные загружаются. Подождите', size=30),
                ft.Image(
                    src="https://media.tenor.com/6aWBg0rV1EYAAAAj/toothless-dancing.gif", 
                    width=300,
                    height=300,
                    fit=ft.ImageFit.FILL 
                ),
            ],
            vertical_alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=26
        )

class AnalysisScreen:
    def __init__(self, controller: AppController):
        self.controller = controller
    
    def build(self):
        return ft.View(
            route='/analise',
            controls=[
                ft.AppBar(title=ft.Text('Анализ'), bgcolor='black'),
                ft.Text(value='Анализ данных. Подождите', size=30),
                ft.Image(
                    src="https://media1.tenor.com/m/q0Cj0U0_4-0AAAAC/genius-smart.gif", 
                    width=498,
                    height=213,
                    fit=ft.ImageFit.FILL 
                ),
            ],
            vertical_alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=26
        )

class ResultScreen:
    def __init__(self, controller: AppController):
        self.controller = controller
        self.game_data = None
        self.topics_data = None
        self.comments_data = None
        self.topics_json = None
        self.result_json = None

    def some_func(self):
        pass

    def load_data(self):
        app = self.controller.current_app

        # Загрузка инфо
        info_path = Path("data") / f"{app.app_id}_{app.language}_info.csv"
        self.game_data = pd.read_csv(info_path)

        # Загрузка тем
        topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_topics.txt"
        self.topics_data = topics_path.read_text(encoding="utf-8")

        # Загрузка тем id 
        topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_topics.json"
        with open(topics_path, "r", encoding="utf-8") as f:
            self.topics_json = json.load(f)

        # Загрузка комментариев по темам
        comments_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_cleaned_reviews.csv"
        if comments_path.exists():
            self.comments_data = pd.read_csv(comments_path)

        # Загрузка тем json
        topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_result.json"
        with open(topics_path, "r", encoding="utf-8") as f:
            self.result_json = json.load(f)

    def build(self):
        self.load_data()

        return ft.View(
            route='/result',
            controls=[
                ft.AppBar(title=ft.Text('Результат'), bgcolor='black'),
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="Инфо об игре",
                            content=self.build_game_info()
                        ),
                        ft.Tab(
                            text="Темы и Топики",
                            content=self.build_topics()
                        ),
                        ft.Tab(
                            text="Графики",
                            content=self.build_graphs()
                        ),
                    ],
                    expand=1,
                ),
                ft.ElevatedButton(text='Home', on_click=lambda e: self.controller.page.go('/'))
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=26
        )
    
    def build_game_info(self):
        name = self.game_data.loc[0, 'name']
        genres = self.game_data.loc[0, 'genres'].strip("[]").replace("'", "").split(", ")
        description = self.game_data.loc[0, 'short_description']
        image_url = self.game_data.loc[0, 'header_image']

        genre_chips = [ft.Chip(label=ft.Text(genre)) for genre in genres]
        return ft.Column(
            controls=[
                ft.Text(value=name, size=30, weight="bold"),
                ft.Image(src=image_url, width=300),
                ft.Row(controls=genre_chips, wrap=True, spacing=8, run_spacing=8),
                ft.Text(value=description, size=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll="auto"
        )

    def build_tabs(self, result: dict):
        comments = self.comments_data
        return ft.Tabs(
            selected_index=0,
            expand=True,
            tabs=[
                ft.Tab(
                    text=topic,
                    content=ft.Column([
                        ft.Text(f"Комментарии по теме '{topic}':"),
                        ft.ListView(
                            controls=[
                                ft.Text(f"- {text}", size=12)
                                for cid in ids
                                if not comments[comments["recommendationid"] == int(cid)].empty
                                for text in comments[comments["recommendationid"] == int(cid)]["review"].tolist()
                            ],
                            spacing=10,
                            height=600,  # Устанавливаем фиксированную высоту контейнера
                            on_scroll=self.some_func()
                        )
                    ])
                )
                for topic, ids in result.items()
            ]
        )

    def build_topics(self):
        result_json = self.result_json
        comment_ids = self.topics_json
        topic_names = list(result_json.keys())
        result = {}
        for idx, topic_name in enumerate(topic_names):
            topic_key = str(idx)
            if topic_key in comment_ids:
                result[topic_name] = comment_ids[topic_key]["recommendationid"]
            else:
                result[topic_name] = []
        
        tabs = self.build_tabs(result)
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Левая колонка с текстом
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Темы по отзывам:"),
                            ft.Text(self.topics_data or "Нет данных"),
                        ],
                        scroll="auto"
                        ),
                        width=400,
                        padding=10,
                    ),
                    # Правая колонка с вкладками комментариев
                    ft.Container(
                        content=tabs,
                        expand=True,
                        padding=10,
                        width=400
                    )
                ],
                spacing=20,
            ),
            padding=20,
        )

    def build_graphs(self):
        df = self.comments_data.copy()

        # Преобразуем время
        df["timestamp_created"] = pd.to_datetime(df["timestamp_created"], unit="s")
        df["date"] = df["timestamp_created"].dt.floor("D")
        df["playtime_diff"] = (df["playtime_forever"] - df["playtime_at_review"]) / 60
        df["playtime_at_review"] = df["playtime_at_review"] / 60  # в часы

        graphs = []
        graphs.append(ft.Container(ft.Image(
                    src=Path("wordclouds")/"full_corpus.png",
                    width=800,
                    height=400,
                    #fit=ft.ImageFit.FILL
                ), width=900, height=500))

        # 1. Круговая диаграмма (Pie)
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        counts = df["voted_up"].value_counts()
        labels = ["Позитивные", "Негативные"] if True in counts.index else ["Негативные", "Позитивные"]
        ax1.pie(
            counts, 
            labels=labels,
            autopct="%1.1f%%", 
            startangle=90, 
            colors=["blue", "red"]
        )
        ax1.set_title("Соотношение отзывов")
        graphs.append(
            ft.Row(
                controls=[
                    ft.Container(MatplotlibChart(fig1, expand=False), width=900, height=500),
                    ft.Container(ft.Text(f"Общее количество комментариев: {self.comments_data.shape[0]}"))
                ]
            )
        )

        # 2. Временная ось (гистограмма по месяцам)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        fig2.autofmt_xdate(rotation=45)
        grouped = df.groupby(["date", "voted_up"]).size().unstack(fill_value=0)
        ax2.bar(grouped.index, grouped.get(True, 0), label="Позитивные", color="green")
        ax2.bar(grouped.index, -grouped.get(False, 0), label="Негативные", color="red")  # вниз
        ax2.axhline(y=0, color="black")
        ax2.set_title("Отзывы по времени")
        ax2.legend()
        graphs.append(ft.Container(MatplotlibChart(fig2, expand=False), width=900, height=500))

        # # 3. Распределение playtime_at_review
        # fig3, ax3 = plt.subplots(figsize=(8, 5))
        # ax3.hist(df[df["voted_up"] == True]["playtime_at_review"], bins=50, alpha=0.6, label="Позитивные", color="green")
        # ax3.hist(df[df["voted_up"] == False]["playtime_at_review"], bins=50, alpha=0.6, label="Негативные", color="red")
        # ax3.set_title("Время в игре на момент отзыва")
        # ax3.set_xlabel("Часы")
        # ax3.set_ylabel("Количество отзывов")
        # ax3.legend()
        # graphs.append(ft.Container(MatplotlibChart(fig3, expand=False), width=900, height=500))

        # # 4. Распределение разницы playtime
        # fig4, ax4 = plt.subplots(figsize=(8, 5))
        # ax4.hist(df[df["voted_up"] == True]["playtime_diff"], bins=50, alpha=0.6, label="Позитивные", color="green")
        # ax4.hist(df[df["voted_up"] == False]["playtime_diff"], bins=50, alpha=0.6, label="Негативные", color="red")
        # ax4.set_title("Разница в игровом времени (часы)")
        # ax4.set_xlabel("Разница (часы)")
        # ax4.set_ylabel("Количество отзывов")
        # ax4.legend()
        # graphs.append(ft.Container(MatplotlibChart(fig4, expand=True), width=900, height=500))
        # 3. Распределение playtime_at_review по сторонам
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        bins = 50

        # Позитивные
        pos_data = df[df["voted_up"] == True]["playtime_at_review"]
        pos_counts, pos_bins = np.histogram(pos_data, bins=bins)
        ax3.bar(pos_bins[:-1], pos_counts, width=np.diff(pos_bins), align='edge', label="Позитивные", color="green")

        # Негативные
        neg_data = df[df["voted_up"] == False]["playtime_at_review"]
        neg_counts, neg_bins = np.histogram(neg_data, bins=pos_bins)  # Совпадение по бинам
        ax3.bar(neg_bins[:-1], -neg_counts, width=np.diff(neg_bins), align='edge', label="Негативные", color="red")

        ax3.axhline(0, color='black')
        ax3.set_title("Время в игре на момент отзыва")
        ax3.set_xlabel("Часы")
        ax3.set_ylabel("Количество отзывов")
        ax3.legend()
        graphs.append(ft.Container(MatplotlibChart(fig3, expand=False), width=900, height=500))

        # 4. Распределение разницы playtime по сторонам
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        bins = 50

        # Позитивные
        pos_data = df[df["voted_up"] == True]["playtime_diff"]
        pos_counts, pos_bins = np.histogram(pos_data, bins=bins)
        ax4.bar(pos_bins[:-1], pos_counts, width=np.diff(pos_bins), align='edge', label="Позитивные", color="green")

        # Негативные
        neg_data = df[df["voted_up"] == False]["playtime_diff"]
        neg_counts, neg_bins = np.histogram(neg_data, bins=pos_bins)  # Совпадение по бинам
        ax4.bar(neg_bins[:-1], -neg_counts, width=np.diff(neg_bins), align='edge', label="Негативные", color="red")

        ax4.axhline(0, color='black')
        ax4.set_title("Разница в игровом времени (часы)")
        ax4.set_xlabel("Разница (часы)")
        ax4.set_ylabel("Количество отзывов")
        ax4.legend()
        graphs.append(ft.Container(MatplotlibChart(fig4, expand=True), width=900, height=500))


        return ft.Container(
            content=ft.Column(
                graphs, 
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.alignment.center
            ),
            padding=20,
            expand=True
        )
