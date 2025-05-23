# import flet as ft
# from flet import RouteChangeEvent, CrossAxisAlignment, MainAxisAlignment, Text
# import threading
# from Key_words_modeling import LDAProcessor
# from download_reviews import SteamReviewsLoader, SteamGameInfo
# from preprocessing import TextCleaner
# from deepseek import TopicAnalyzer
# from Configs import CurrentApp
# import Configs
# from pathlib import Path
# import pandas as pd
# import json
# import matplotlib.pyplot as plt
# from flet.matplotlib_chart import MatplotlibChart
# import matplotlib
# import numpy as np

# matplotlib.use("svg")

# class AppController:
#     def __init__(self, page: ft.Page):
#         self.page = page
#         self.current_app = None
#         self.page.on_route_change = self.route_change
#         self.page.go(self.page.route)
    
#     def route_change(self, e: RouteChangeEvent):
#         route = self.page.route
#         match route:
#             case '/':
#                 self.page.views.clear()
#                 self.page.views.append(HomeScreen(self).build())
#             case '/download_review':
#                 self.page.views.clear()
#                 self.page.views.append(DownloadScreen(self).build())
#                 threading.Thread(target=self.download_reviews).start()
#             case '/analise':
#                 self.page.views.clear()
#                 self.page.views.append(AnalysisScreen(self).build())
#                 threading.Thread(target=self.analyze_data).start()
#             case '/result':
#                 self.page.views.clear()
#                 self.page.views.append(ResultScreen(self).build())
#             case '/game_info':
#                 self.page.views.clear()
#                 self.page.views.append(GameInfo(self).build())
#         self.page.update()
    
#     def load_game_info(self):
#         loader = SteamGameInfo(self.current_app)
#         info = loader.load()
#         self.page.go('/game_info')

#     def download_reviews(self):
#         loader = SteamReviewsLoader(self.current_app)
#         loader.load()
#         self.page.go('/analise')
    
#     def analyze_data(self):
#         cleaner = TextCleaner(self.current_app)
#         cleaner.process()
#         processor = LDAProcessor(self.current_app)
#         processor.process()
#         analyzer = TopicAnalyzer(self.current_app)
#         analyzer.analyze_topics()
#         self.page.go('/result')
    
#     def set_current_app(self, app_data):
#         self.current_app = app_data
#         self.page.client_storage.set("game_data", self.current_app.__dict__)

# class GameInfo:
#     def __init__(self, controller: AppController):
#         self.controller = controller
    
#     def build(self):
#         app = self.controller.current_app
#         info_path = Path("data") / f"{app.app_id}_{app.language}_info.csv".replace("/", "\\")
#         if not info_path.exists():
#             return ft.View(
#                 route='/game_info',
#                 controls=[ft.Text("Нет данных об игре. Сначала загрузите информацию.")],
#             )
        
#         df = pd.read_csv(info_path)

#         name = df.loc[0, 'name']
#         image_url = df.loc[0, 'header_image']


#         return ft.View(
#             route='/game_info',
#             controls=[
#                 ft.AppBar(title=ft.Text('Инфо об игре'), bgcolor='black'),
#                 ft.Text(value=name, size=30, weight="bold"),
#                 ft.Image(src=image_url, width=300),
#                 ft.ElevatedButton(text='Далее: скачать отзывы', on_click=lambda e: self.controller.page.go('/download_review'))
#             ],
#             vertical_alignment=MainAxisAlignment.CENTER,
#             horizontal_alignment=CrossAxisAlignment.CENTER,
#             spacing=26
#         )
    
    

# class HomeScreen:
#     def __init__(self, controller: AppController):
#         self.controller = controller
#         self.app_id = ft.TextField(label='Вставьте AppID', width=200)
#         self.language = ft.Dropdown(
#             label='Выберите язык',
#             width=200,
#             options=[ft.dropdown.Option(lang) for lang in Configs.language_list]
#         )
#         self.mood = Configs.mood_list[2]  # <- теперь это просто строка, например 'positive'
#         self.submit_button = ft.ElevatedButton(text='Старт', on_click=self.on_submit, disabled=True)

#     def validate(self, e: ft.ControlEvent):
#         self.submit_button.disabled = not all([self.app_id.value, self.language.value])
#         self.controller.page.update()

#     def on_submit(self, e: ft.ControlEvent):
#         game = CurrentApp(
#             self.app_id.value,
#             self.language.value,
#             self.mood,  # <- mood больше не UI-элемент
#             Configs.day_range
#         )
#         self.controller.set_current_app(game)
#         threading.Thread(target=self.controller.load_game_info).start()

#     def build(self):
#         self.app_id.on_change = self.validate
#         self.language.on_change = self.validate

#         return ft.View(
#             route='/',
#             controls=[
#                 ft.AppBar(title=ft.Text('Home'), bgcolor='black'),
#                 self.app_id,
#                 self.language,
#                 self.submit_button,
#             ],
#             vertical_alignment=ft.MainAxisAlignment.CENTER,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             spacing=26
#         )

    
# class DownloadScreen:
#     def __init__(self, controller: AppController):
#         self.controller = controller
    
#     def build(self):
#         return ft.View(
#             route='/download_review',
#             controls=[
#                 ft.AppBar(title=Text('Загрузка отзывов'), bgcolor='black'),
#                 Text(value='Данные загружаются. Подождите', size=30),
#                 ft.Image(
#                     src="https://media.tenor.com/6aWBg0rV1EYAAAAj/toothless-dancing.gif", 
#                     width=300,
#                     height=300,
#                     fit=ft.ImageFit.FILL 
#                 ),
#             ],
#             vertical_alignment=MainAxisAlignment.CENTER,
#             horizontal_alignment=CrossAxisAlignment.CENTER,
#             spacing=26
#         )

# class AnalysisScreen:
#     def __init__(self, controller: AppController):
#         self.controller = controller
    
#     def build(self):
#         return ft.View(
#             route='/analise',
#             controls=[
#                 ft.AppBar(title=ft.Text('Анализ'), bgcolor='black'),
#                 ft.Text(value='Анализ данных. Подождите', size=30),
#                 ft.Image(
#                     src="https://media1.tenor.com/m/q0Cj0U0_4-0AAAAC/genius-smart.gif", 
#                     width=498,
#                     height=213,
#                     fit=ft.ImageFit.FILL 
#                 ),
#             ],
#             vertical_alignment=MainAxisAlignment.CENTER,
#             horizontal_alignment=CrossAxisAlignment.CENTER,
#             spacing=26
#         )

# class ResultScreen:
#     def __init__(self, controller: AppController):
#         self.controller = controller
#         self.game_data = None
#         self.topics_data = None
#         self.comments_data = None
#         self.topics_json = None
#         self.result_json = None

#     def some_func(self):
#         pass

#     def load_data(self):
#         app = self.controller.current_app

#         # Загрузка инфо
#         info_path = Path("data") / f"{app.app_id}_{app.language}_info.csv"
#         self.game_data = pd.read_csv(info_path)

#         # Загрузка тем
#         topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_topics.txt"
#         self.topics_data = topics_path.read_text(encoding="utf-8")

#         # Загрузка тем id 
#         topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_topics.json"
#         with open(topics_path, "r", encoding="utf-8") as f:
#             self.topics_json = json.load(f)

#         # Загрузка комментариев по темам
#         comments_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_cleaned_reviews.csv"
#         if comments_path.exists():
#             self.comments_data = pd.read_csv(comments_path)

#         # Загрузка тем json
#         topics_path = Path("data") / f"{app.app_id}_{app.language}_{app.mood}_result.json"
#         with open(topics_path, "r", encoding="utf-8") as f:
#             self.result_json = json.load(f)

#     def build(self):
#         self.load_data()

#         return ft.View(
#             route='/result',
#             controls=[
#                 ft.AppBar(title=ft.Text('Результат'), bgcolor='black'),
#                 ft.Tabs(
#                     selected_index=0,
#                     animation_duration=300,
#                     tabs=[
#                         ft.Tab(
#                             text="Инфо об игре",
#                             content=self.build_game_info()
#                         ),
#                         ft.Tab(
#                             text="Темы и Топики",
#                             content=self.build_topics()
#                         ),
#                         ft.Tab(
#                             text="Графики",
#                             content=self.build_graphs()
#                         ),
#                     ],
#                     expand=1,
#                 ),
#                 ft.ElevatedButton(text='Home', on_click=lambda e: self.controller.page.go('/'))
#             ],
#             vertical_alignment=ft.MainAxisAlignment.CENTER,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             spacing=26
#         )
    
#     def build_game_info(self):
#         name = self.game_data.loc[0, 'name']
#         genres = self.game_data.loc[0, 'genres'].strip("[]").replace("'", "").split(", ")
#         description = self.game_data.loc[0, 'short_description']
#         image_url = self.game_data.loc[0, 'header_image']

#         genre_chips = [ft.Chip(label=ft.Text(genre)) for genre in genres]
#         return ft.Column(
#             controls=[
#                 ft.Text(value=name, size=30, weight="bold"),
#                 ft.Image(src=image_url, width=300),
#                 ft.Row(controls=genre_chips, wrap=True, spacing=8, run_spacing=8),
#                 ft.Text(value=description, size=20),
#             ],
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             spacing=20,
#             scroll="auto"
#         )

#     def build_tabs(self, result: dict):
#         comments = self.comments_data
#         return ft.Tabs(
#             selected_index=0,
#             expand=True,
#             tabs=[
#                 ft.Tab(
#                     text=topic,
#                     content=ft.Column([
#                         ft.Text(f"Комментарии по теме '{topic}':"),
#                         ft.ListView(
#                             controls=[
#                                 ft.Text(f"- {text}", size=12)
#                                 for cid in ids
#                                 if not comments[comments["recommendationid"] == int(cid)].empty
#                                 for text in comments[comments["recommendationid"] == int(cid)]["review"].tolist()
#                             ],
#                             spacing=10,
#                             height=600,  # Устанавливаем фиксированную высоту контейнера
#                             on_scroll=self.some_func()
#                         )
#                     ])
#                 )
#                 for topic, ids in result.items()
#             ]
#         )

#     def build_topics(self):
#         result_json = self.result_json
#         comment_ids = self.topics_json
#         topic_names = list(result_json.keys())
#         result = {}
#         for idx, topic_name in enumerate(topic_names):
#             topic_key = str(idx)
#             if topic_key in comment_ids:
#                 result[topic_name] = comment_ids[topic_key]["recommendationid"]
#             else:
#                 result[topic_name] = []
        
#         tabs = self.build_tabs(result)
#         return ft.Container(
#             content=ft.Row(
#                 controls=[
#                     # Левая колонка с текстом
#                     ft.Container(
#                         content=ft.Column([
#                             ft.Text("Темы по отзывам:"),
#                             ft.Text(self.topics_data or "Нет данных"),
#                         ],
#                         scroll="auto"
#                         ),
#                         width=400,
#                         padding=10,
#                     ),
#                     # Правая колонка с вкладками комментариев
#                     ft.Container(
#                         content=tabs,
#                         expand=True,
#                         padding=10,
#                         width=400
#                     )
#                 ],
#                 spacing=20,
#             ),
#             padding=20,
#         )

#     def build_graphs(self):
#         df = self.comments_data.copy()

#         # Преобразуем время
#         df["timestamp_created"] = pd.to_datetime(df["timestamp_created"], unit="s")
#         df["date"] = df["timestamp_created"].dt.floor("D")
#         df["playtime_diff"] = (df["playtime_forever"] - df["playtime_at_review"]) / 60
#         df["playtime_at_review"] = df["playtime_at_review"] / 60  # в часы

#         graphs = []
#         graphs.append(ft.Container(ft.Image(
#                     src=Path("wordclouds")/"full_corpus.png",
#                     width=800,
#                     height=400,
#                     #fit=ft.ImageFit.FILL
#                 ), width=900, height=500))

#         # 1. Круговая диаграмма (Pie)
#         fig1, ax1 = plt.subplots(figsize=(8, 5))
#         counts = df["voted_up"].value_counts()
#         labels = ["Позитивные", "Негативные"] if True in counts.index else ["Негативные", "Позитивные"]
#         ax1.pie(
#             counts, 
#             labels=labels,
#             autopct="%1.1f%%", 
#             startangle=90, 
#             colors=["blue", "red"]
#         )
#         ax1.set_title("Соотношение отзывов")
#         graphs.append(
#             ft.Row(
#                 controls=[
#                     ft.Container(MatplotlibChart(fig1, expand=False), width=900, height=500),
#                     ft.Container(ft.Text(f"Общее количество комментариев: {self.comments_data.shape[0]}"))
#                 ]
#             )
#         )

#         # 2. Временная ось (гистограмма по месяцам)
#         fig2, ax2 = plt.subplots(figsize=(8, 5))
#         fig2.autofmt_xdate(rotation=45)
#         grouped = df.groupby(["date", "voted_up"]).size().unstack(fill_value=0)
#         ax2.bar(grouped.index, grouped.get(True, 0), label="Позитивные", color="green")
#         ax2.bar(grouped.index, -grouped.get(False, 0), label="Негативные", color="red")  # вниз
#         ax2.axhline(y=0, color="black")
#         ax2.set_title("Отзывы по времени")
#         ax2.legend()
#         graphs.append(ft.Container(MatplotlibChart(fig2, expand=False), width=900, height=500))

#         # # 3. Распределение playtime_at_review
#         # fig3, ax3 = plt.subplots(figsize=(8, 5))
#         # ax3.hist(df[df["voted_up"] == True]["playtime_at_review"], bins=50, alpha=0.6, label="Позитивные", color="green")
#         # ax3.hist(df[df["voted_up"] == False]["playtime_at_review"], bins=50, alpha=0.6, label="Негативные", color="red")
#         # ax3.set_title("Время в игре на момент отзыва")
#         # ax3.set_xlabel("Часы")
#         # ax3.set_ylabel("Количество отзывов")
#         # ax3.legend()
#         # graphs.append(ft.Container(MatplotlibChart(fig3, expand=False), width=900, height=500))

#         # # 4. Распределение разницы playtime
#         # fig4, ax4 = plt.subplots(figsize=(8, 5))
#         # ax4.hist(df[df["voted_up"] == True]["playtime_diff"], bins=50, alpha=0.6, label="Позитивные", color="green")
#         # ax4.hist(df[df["voted_up"] == False]["playtime_diff"], bins=50, alpha=0.6, label="Негативные", color="red")
#         # ax4.set_title("Разница в игровом времени (часы)")
#         # ax4.set_xlabel("Разница (часы)")
#         # ax4.set_ylabel("Количество отзывов")
#         # ax4.legend()
#         # graphs.append(ft.Container(MatplotlibChart(fig4, expand=True), width=900, height=500))
#         # 3. Распределение playtime_at_review по сторонам
#         fig3, ax3 = plt.subplots(figsize=(8, 5))
#         bins = 50

#         # Позитивные
#         pos_data = df[df["voted_up"] == True]["playtime_at_review"]
#         pos_counts, pos_bins = np.histogram(pos_data, bins=bins)
#         ax3.bar(pos_bins[:-1], pos_counts, width=np.diff(pos_bins), align='edge', label="Позитивные", color="green")

#         # Негативные
#         neg_data = df[df["voted_up"] == False]["playtime_at_review"]
#         neg_counts, neg_bins = np.histogram(neg_data, bins=pos_bins)  # Совпадение по бинам
#         ax3.bar(neg_bins[:-1], -neg_counts, width=np.diff(neg_bins), align='edge', label="Негативные", color="red")

#         ax3.axhline(0, color='black')
#         ax3.set_title("Время в игре на момент отзыва")
#         ax3.set_xlabel("Часы")
#         ax3.set_ylabel("Количество отзывов")
#         ax3.legend()
#         graphs.append(ft.Container(MatplotlibChart(fig3, expand=False), width=900, height=500))

#         # 4. Распределение разницы playtime по сторонам
#         fig4, ax4 = plt.subplots(figsize=(8, 5))
#         bins = 50

#         # Позитивные
#         pos_data = df[df["voted_up"] == True]["playtime_diff"]
#         pos_counts, pos_bins = np.histogram(pos_data, bins=bins)
#         ax4.bar(pos_bins[:-1], pos_counts, width=np.diff(pos_bins), align='edge', label="Позитивные", color="green")

#         # Негативные
#         neg_data = df[df["voted_up"] == False]["playtime_diff"]
#         neg_counts, neg_bins = np.histogram(neg_data, bins=pos_bins)  # Совпадение по бинам
#         ax4.bar(neg_bins[:-1], -neg_counts, width=np.diff(neg_bins), align='edge', label="Негативные", color="red")

#         ax4.axhline(0, color='black')
#         ax4.set_title("Разница в игровом времени (часы)")
#         ax4.set_xlabel("Разница (часы)")
#         ax4.set_ylabel("Количество отзывов")
#         ax4.legend()
#         graphs.append(ft.Container(MatplotlibChart(fig4, expand=True), width=900, height=500))


#         return ft.Container(
#             content=ft.Column(
#                 graphs, 
#                 scroll=ft.ScrollMode.AUTO,
#                 alignment=ft.alignment.center
#             ),
#             padding=20,
#             expand=True
#         )

import flet as ft
from flet import RouteChangeEvent, CrossAxisAlignment, MainAxisAlignment, Text, SnackBar, colors
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

matplotlib.use("svg") # Используем SVG для лучшей совместимости с Flet

class AppController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_app = None
        self.page.on_route_change = self.route_change
        self.page.snack_bar = SnackBar(
            content=Text(""),
            open=False,
            bgcolor=colors.RED_600
        )
        self.page.add(self.page.snack_bar) # Добавляем SnackBar на страницу
        self.page.go(self.page.route)
    
    def _show_error_snackbar(self, message: str):
        """Показывает сообщение об ошибке через SnackBar."""
        self.page.snack_bar.content = Text(message)
        self.page.snack_bar.open = True
        self.page.update()
        
    def route_change(self, e: RouteChangeEvent):
        route = self.page.route
        self.page.views.clear() # Очищаем все views перед добавлением новой
        
        if route == '/':
            self.page.views.append(HomeScreen(self).build())
        elif route == '/download_review':
            self.page.views.append(DownloadScreen(self).build())
            threading.Thread(target=self.download_reviews).start()
        elif route == '/analise':
            self.page.views.append(AnalysisScreen(self).build())
            threading.Thread(target=self.analyze_data).start()
        elif route == '/result':
            self.page.views.append(ResultScreen(self).build())
        elif route == '/game_info':
            self.page.views.append(GameInfo(self).build())
            
        self.page.update()
    
    def load_game_info(self):
        try:
            loader = SteamGameInfo(self.current_app)
            info = loader.load()
            if info:
                self.page.go('/game_info')
            else:
                self._show_error_snackbar("Не удалось загрузить информацию об игре. Проверьте AppID.")
                self.page.go('/') # Вернуться на домашний экран
        except Exception as e:
            self._show_error_snackbar(f"Ошибка при загрузке информации об игре: {e}")
            self.page.go('/')

    def download_reviews(self):
        try:
            loader = SteamReviewsLoader(self.current_app)
            loader.load()
            self.page.go('/analise')
        except Exception as e:
            self._show_error_snackbar(f"Ошибка при загрузке отзывов: {e}")
            self.page.go('/')
    
    def analyze_data(self):
        try:
            cleaner = TextCleaner(self.current_app)
            cleaner.process()
            processor = LDAProcessor(self.current_app)
            processor.process()
            # Облака слов теперь генерируются внутри LDAProcessor.process(), 
            # который вызывает _generate_single_wordcloud для каждого типа настроения.
            analyzer = TopicAnalyzer(self.current_app)
            analyzer.analyze_topics()
            self.page.go('/result')
        except Exception as e:
            self._show_error_snackbar(f"Ошибка при анализе данных: {e}")
            self.page.go('/')
    
    def set_current_app(self, app_data: CurrentApp):
        self.current_app = app_data
        # Сохранение в client_storage может быть полезно для восстановления состояния
        # self.page.client_storage.set("game_data", self.current_app.__dict__)

class GameInfo:
    def __init__(self, controller: AppController):
        self.controller = controller
    
    def build(self):
        app = self.controller.current_app
        info_path = Path("data") / f"{app.app_id}_{app.language}_info.csv"
        
        if not info_path.exists():
            return ft.View(
                route='/game_info',
                controls=[
                    ft.AppBar(title=ft.Text('Инфо об игре'), bgcolor='black'),
                    ft.Text("Нет данных об игре. Сначала загрузите информацию.", size=20, color=colors.RED_400),
                    ft.ElevatedButton(text='На главную', on_click=lambda e: self.controller.page.go('/'))
                ],
                vertical_alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=26
            )
        
        try:
            df = pd.read_csv(info_path)
            name = df.loc[0, 'name']
            image_url = df.loc[0, 'header_image']
            genres = df.loc[0, 'genres'].strip("[]").replace("'", "").split(", ")
            description = df.loc[0, 'short_description']

            genre_chips = [ft.Chip(label=ft.Text(genre)) for genre in genres if genre.strip()]
            if not genre_chips:
                genre_chips = [ft.Text("Жанры не указаны")]

            return ft.View(
                route='/game_info',
                controls=[
                    ft.AppBar(title=ft.Text('Инфо об игре'), bgcolor='black'),
                    ft.Column(
                        [
                            ft.Text(value=name, size=30, weight="bold", text_align=ft.TextAlign.CENTER),
                            ft.Image(src=image_url, width=300, fit=ft.ImageFit.CONTAIN) if image_url else ft.Container(),
                            ft.Row(controls=genre_chips, wrap=True, spacing=8, run_spacing=8, alignment=MainAxisAlignment.CENTER),
                            ft.Text(value=description, size=16, selectable=True, text_align=ft.TextAlign.CENTER, max_lines=5, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.ElevatedButton(text='Далее: скачать отзывы', on_click=lambda e: self.controller.page.go('/download_review'))
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        spacing=26,
                        scroll=ft.ScrollMode.ADAPTIVE
                    )
                ],
                vertical_alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=26
            )
        except Exception as e:
            return ft.View(
                route='/game_info',
                controls=[
                    ft.AppBar(title=ft.Text('Инфо об игре'), bgcolor='black'),
                    ft.Text(f"Ошибка при чтении файла информации об игре: {e}", size=20, color=colors.RED_400),
                    ft.ElevatedButton(text='На главную', on_click=lambda e: self.controller.page.go('/'))
                ],
                vertical_alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=26
            )
    

class HomeScreen:
    def __init__(self, controller: AppController):
        self.controller = controller
        self.app_id = ft.TextField(label='Вставьте AppID', width=300)
        self.language = ft.Dropdown(
            label='Выберите язык',
            width=300,
            options=[ft.dropdown.Option(lang) for lang in Configs.language_list],
            value=Configs.language_list[0] # Устанавливаем значение по умолчанию
        )
        self.mood = Configs.mood_list[2] # 'all' - это всегда будет mood для загрузки.
        self.submit_button = ft.ElevatedButton(text='Старт', on_click=self.on_submit, disabled=True)

    def validate(self, e: ft.ControlEvent):
        self.submit_button.disabled = not all([self.app_id.value, self.language.value])
        self.controller.page.update()

    def on_submit(self, e: ft.ControlEvent):
        game = CurrentApp(
            self.app_id.value,
            self.language.value,
            self.mood, 
            Configs.day_range
        )
        self.controller.set_current_app(game)
        # load_game_info уже запускает отдельный поток
        threading.Thread(target=self.controller.load_game_info).start() 

    def build(self):
        self.app_id.on_change = self.validate
        self.language.on_change = self.validate

        return ft.View(
            route='/',
            controls=[
                ft.AppBar(title=ft.Text('Анализатор отзывов Steam'), bgcolor='black'),
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
                Text(value='Данные загружаются. Подождите...', size=30),
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
                ft.Text(value='Данные анализируются. Подождите...', size=30),
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
        self.app = self.controller.current_app
        self.data_dir = Path("data")

        # Инициализация всех переменных для данных
        self.game_info = None
        
        self.positive_comments_df = None
        self.negative_comments_df = None
        self.all_comments_df = None # Для общих графиков

        self.positive_lda_topics_json = None
        self.negative_lda_topics_json = None

        self.positive_ai_result_txt = None
        self.negative_ai_result_txt = None

        self.positive_ai_result_json = None
        self.negative_ai_result_json = None

        self.error_message = None # Для отображения общей ошибки загрузки данных
        
        self.load_data() # Загружаем все данные при инициализации

    def load_data(self):
        """Загружает все необходимые данные для ResultScreen."""
        try:
            # Загрузка информации об игре
            info_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_info.csv"
            if info_path.exists():
                self.game_info = pd.read_csv(info_path).iloc[0] # Берем первую строку
            else:
                self.error_message = "Ошибка: Файл информации об игре не найден."

            # Загрузка очищенных комментариев
            positive_cleaned_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_positive_cleaned_reviews.csv"
            negative_cleaned_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_negative_cleaned_reviews.csv"
            
            if positive_cleaned_path.exists():
                self.positive_comments_df = pd.read_csv(positive_cleaned_path, dtype={'recommendationid': str})
            if negative_cleaned_path.exists():
                self.negative_comments_df = pd.read_csv(negative_cleaned_path, dtype={'recommendationid': str})

            # Объединяем для общих графиков, если оба DataFrame существуют
            if self.positive_comments_df is not None and self.negative_comments_df is not None:
                self.all_comments_df = pd.concat([self.positive_comments_df, self.negative_comments_df], ignore_index=True)
            elif self.positive_comments_df is not None:
                self.all_comments_df = self.positive_comments_df.copy()
            elif self.negative_comments_df is not None:
                self.all_comments_df = self.negative_comments_df.copy()
            else:
                self.error_message = "Ошибка: Файлы очищенных отзывов (позитивных/негативных) не найдены."

            # Загрузка LDA тем
            positive_lda_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_positive_topics.json"
            negative_lda_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_negative_topics.json"

            if positive_lda_path.exists():
                with open(positive_lda_path, 'r', encoding='utf-8') as f:
                    self.positive_lda_topics_json = json.load(f)
            if negative_lda_path.exists():
                with open(negative_lda_path, 'r', encoding='utf-8') as f:
                    self.negative_lda_topics_json = json.load(f)

            # Загрузка AI результатов (TXT)
            positive_ai_txt_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_positive_topics.txt"
            negative_ai_txt_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_negative_topics.txt"
            
            if positive_ai_txt_path.exists():
                self.positive_ai_result_txt = positive_ai_txt_path.read_text(encoding="utf-8")
            if negative_ai_txt_path.exists():
                self.negative_ai_result_txt = negative_ai_txt_path.read_text(encoding="utf-8")
            
            # Загрузка AI результатов (JSON)
            positive_ai_json_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_positive_result.json"
            negative_ai_json_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_negative_result.json"

            if positive_ai_json_path.exists():
                with open(positive_ai_json_path, 'r', encoding='utf-8') as f:
                    self.positive_ai_result_json = json.load(f)
            if negative_ai_json_path.exists():
                with open(negative_ai_json_path, 'r', encoding='utf-8') as f:
                    self.negative_ai_result_json = json.load(f)

        except Exception as e:
            self.error_message = f"Ошибка при загрузке данных для отображения: {e}"
            print(f"DEBUG: Error loading data in ResultScreen: {e}") # Для отладки в консоли
    
    def build(self):
        """Строит основной View для экрана результатов."""
        tabs_list = [
            ft.Tab(
                text="Инфо об игре",
                content=self._build_game_info_section()
            ),
            ft.Tab(
                text="Позитивные отзывы",
                content=self._build_sentiment_section('positive')
            ),
            ft.Tab(
                text="Негативные отзывы",
                content=self._build_sentiment_section('negative')
            ),
            ft.Tab(
                text="Общая статистика",
                content=self._build_overall_statistics_section()
            ),
        ]

        return ft.View(
            route='/result',
            controls=[
                ft.AppBar(title=ft.Text('Результаты анализа'), bgcolor='black'),
                ft.Text(f"AppID: {self.app.app_id} | Язык: {self.app.language}", size=16, weight="bold"),
                ft.Text(self.error_message, color=colors.RED_500) if self.error_message else ft.Container(),
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=tabs_list,
                    expand=1,
                    # Можно добавить scrollable=True для вкладок, если их много
                ),
                ft.ElevatedButton(text='На главную', on_click=lambda e: self.controller.page.go('/'))
            ],
            vertical_alignment=ft.MainAxisAlignment.START, # Чтобы контент начинался сверху
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    
    def _build_game_info_section(self):
        """Создает секцию с информацией об игре."""
        if self.game_info is None:
            return ft.Column([ft.Text("Информация об игре не найдена.", color=colors.ORANGE_400)])
        
        name = self.game_info.get('name', 'Неизвестно')
        genres = self.game_info.get('genres', '[]').strip("[]").replace("'", "").split(", ")
        description = self.game_info.get('short_description', 'Описание недоступно')
        image_url = self.game_info.get('header_image', '')

        genre_chips = [ft.Chip(label=ft.Text(genre)) for genre in genres if genre.strip()]
        if not genre_chips:
            genre_chips = [ft.Text("Жанры не указаны")]

        return ft.Column(
            controls=[
                ft.Text(value=name, size=30, weight="bold", text_align=ft.TextAlign.CENTER),
                ft.Image(src=image_url, width=300, fit=ft.ImageFit.CONTAIN) if image_url else ft.Container(),
                ft.Row(controls=genre_chips, wrap=True, spacing=8, run_spacing=8, alignment=MainAxisAlignment.CENTER),
                ft.Text(value=description, size=16, selectable=True, text_align=ft.TextAlign.CENTER, max_lines=10, overflow=ft.TextOverflow.ELLIPSIS),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll="auto",
            expand=True
        )

    def _build_sentiment_section(self, sentiment: str):
        """
        Создает общую секцию для конкретного настроения (позитивные/негативные),
        включающую темы/топики и графики.
        """
        is_positive = (sentiment == 'positive')
        comments_df = self.positive_comments_df if is_positive else self.negative_comments_df
        lda_topics_json = self.positive_lda_topics_json if is_positive else self.negative_lda_topics_json
        ai_result_txt = self.positive_ai_result_txt if is_positive else self.negative_ai_result_txt
        ai_result_json = self.positive_ai_result_json if is_positive else self.negative_ai_result_json
        wordcloud_path = self.data_dir / f"{self.app.app_id}_{self.app.language}_{sentiment}_wordcloud.png"

        if comments_df is None or comments_df.empty or lda_topics_json is None or ai_result_json is None:
            return ft.Column([
                ft.Text(f"Нет данных для {sentiment} отзывов или произошла ошибка при загрузке.", color=colors.ORANGE_400),
                ft.Text("Убедитесь, что были скачаны и обработаны отзывы этого типа.", color=colors.ORANGE_400)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        # Комментарии по темам (вкладки внутри вкладки)
        comment_tabs = []
        if ai_result_json and lda_topics_json:
            for ai_topic_name, lda_subcategories in ai_result_json.items():
                # Находим соответствующий ключ в lda_topics_json по ключевым словам или по порядку
                # Это упрощенный поиск. В реальном проекте понадобится более надежное сопоставление
                # (например, по общим ключевым словам или через специальный ID, если LLM его возвращает).
                # Пока что берем самый большой набор ключевых слов, который может соответствовать.
                lda_topic_id = None
                max_common_keywords = -1
                
                # Извлекаем все слова из подкатегорий AI-темы для сравнения
                ai_keywords_from_subcategories = []
                for sub in lda_subcategories:
                    ai_keywords_from_subcategories.extend([w.strip() for w in sub.split(',') if w.strip()])

                for lda_idx, lda_info in lda_topics_json.items():
                    lda_keywords_set = set(lda_info.get('keywords', []))
                    common_count = len(lda_keywords_set.intersection(set(ai_keywords_from_subcategories)))
                    
                    if common_count > max_common_keywords:
                        max_common_keywords = common_count
                        lda_topic_id = lda_idx
                
                # Если LDA topic ID найден, берем связанные с ним recommendationid
                topic_comment_ids = lda_topics_json.get(lda_topic_id, {}).get("recommendationid", [])
                
                # Фильтруем комментарии по recommendationid и проверяем, есть ли они в comments_df
                filtered_comments = comments_df[comments_df["recommendationid"].isin(topic_comment_ids)]

                comments_controls = []
                if not filtered_comments.empty:
                    # Ограничиваем количество отображаемых комментариев для производительности UI
                    for index, row in filtered_comments.head(20).iterrows(): # Показываем до 20 комментариев
                        comments_controls.append(ft.Text(f"- {row['review']}", size=12, selectable=True))
                else:
                    comments_controls.append(ft.Text("Нет комментариев, соответствующих этой теме.", size=12, color=colors.GREY_500))

                comment_tabs.append(
                    ft.Tab(
                        text=ai_topic_name,
                        content=ft.ListView(
                            controls=comments_controls,
                            spacing=10,
                            height=300, # Фиксированная высота для списка комментариев
                            auto_scroll=True
                        )
                    )
                )
        
        # Облако слов
        wordcloud_image = ft.Container()
        if wordcloud_path.exists():
            wordcloud_image = ft.Image(
                src=str(wordcloud_path),
                width=800,
                height=400,
                fit=ft.ImageFit.CONTAIN
            )
        else:
            wordcloud_image = ft.Text(f"Облако слов для {sentiment} отзывов не найдено.", color=colors.ORANGE_400)


        return ft.Column(
            controls=[
                ft.Text(f"Темы по {sentiment} отзывам:", size=18, weight="bold"),
                ft.Container(
                    content=ft.Column( # Оборачиваем Text в Column
                        [ft.Text(ai_result_txt or "Нет данных о темах.", selectable=True)],
                        scroll="auto", # Скролл теперь применяется к Column
                        expand=True, # Column должен растягиваться на всю высоту контейнера
                    ),
                    border=ft.border.all(1, colors.GREY_300),
                    border_radius=5,
                    padding=10,
                    height=300, # Фиксированная высота контейнера
                    expand=True # Контейнер тоже может расширяться, если ему это позволит родитель
                ),
                ft.Text("Комментарии по темам:", size=18, weight="bold"),
                ft.Container(
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        tabs=comment_tabs if comment_tabs else [ft.Tab(text="Нет тем", content=ft.Text("Не удалось сгруппировать комментарии по темам."))],
                        expand=1,
                        scrollable=True # Скролл для вкладок, если их много
                    ),
                    height=350, # Фиксированная высота для контейнера с вкладками комментариев
                    expand=True,
                    border=ft.border.all(1, colors.GREY_300),
                    border_radius=5,
                ),
                ft.Text(f"Облако слов для {sentiment} отзывов:", size=18, weight="bold"),
                wordcloud_image,
                ft.Divider(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    def _build_overall_statistics_section(self):
        """Создает секцию с общими статистическими графиками."""
        if self.all_comments_df is None or self.all_comments_df.empty:
            return ft.Column([ft.Text("Нет объединенных данных отзывов для построения общей статистики.", color=colors.ORANGE_400)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        df = self.all_comments_df.copy()

        # Преобразуем время
        df["timestamp_created"] = pd.to_datetime(df["timestamp_created"], unit="s")
        df["date"] = df["timestamp_created"].dt.floor("D")
        df["playtime_diff"] = (df["playtime_forever"] - df["playtime_at_review"]) / 60
        df["playtime_at_review"] = df["playtime_at_review"] / 60  # в часы

        graphs = []

        # 1. Круговая диаграмма (Pie)
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        counts = df["voted_up"].value_counts(normalize=True) # Нормализованные значения для процентов
        # Убедимся, что True и False всегда присутствуют для labels
        labels = []
        sizes = []
        colors_map = {True: "green", False: "red"}
        
        # Заполняем labels и sizes в правильном порядке
        if True in counts.index:
            labels.append("Позитивные")
            sizes.append(counts[True])
        if False in counts.index:
            labels.append("Негативные")
            sizes.append(counts[False])

        # Определяем цвета в соответствии с order of labels
        plot_colors = [colors_map[True] if l == "Позитивные" else colors_map[False] for l in labels]

        ax1.pie(
            sizes, 
            labels=labels,
            autopct="%1.1f%%", 
            startangle=90, 
            colors=plot_colors # Используем plot_colors
        )
        ax1.set_title("Соотношение отзывов")
        graphs.append(
            ft.Column(
                controls=[
                    ft.Text(f"Общее количество комментариев: {self.all_comments_df.shape[0]}", size=16),
                    MatplotlibChart(fig1, expand=True) # expand=True позволяет FletChart занимать доступное пространство
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
        )
        plt.close(fig1) # Обязательно закрываем фигуру, чтобы освободить память

        # 2. Временная ось (гистограмма по месяцам)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        fig2.autofmt_xdate(rotation=45)
        
        # Группируем по дате и voted_up
        grouped = df.groupby(["date", "voted_up"]).size().unstack(fill_value=0)
        
        # Обеспечиваем наличие колонок True и False, если они отсутствуют
        positive_counts = grouped.get(True, pd.Series(0, index=grouped.index))
        negative_counts = grouped.get(False, pd.Series(0, index=grouped.index))
        
        ax2.bar(grouped.index, positive_counts, label="Позитивные", color="green")
        ax2.bar(grouped.index, -negative_counts, label="Негативные", color="red")  # вниз
        ax2.axhline(y=0, color="black")
        ax2.set_title("Отзывы по времени")
        ax2.legend()
        graphs.append(ft.Container(MatplotlibChart(fig2, expand=True), width=900, height=500))
        plt.close(fig2)

        # 3. Распределение playtime_at_review по сторонам
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        bins = 50

        pos_data = df[df["voted_up"] == True]["playtime_at_review"]
        neg_data = df[df["voted_up"] == False]["playtime_at_review"]
        
        # Объединяем данные для определения общих бинов
        all_playtime_data = pd.concat([pos_data, neg_data]).dropna()
        if not all_playtime_data.empty:
            _, bins_edges = np.histogram(all_playtime_data, bins=bins)
        else: # Fallback if no playtime data
            bins_edges = np.linspace(0, 100, bins + 1) # Default bins

        # Позитивные
        pos_counts, _ = np.histogram(pos_data.dropna(), bins=bins_edges)
        ax3.bar(bins_edges[:-1], pos_counts, width=np.diff(bins_edges), align='edge', label="Позитивные", color="green", alpha=0.7)

        # Негативные
        neg_counts, _ = np.histogram(neg_data.dropna(), bins=bins_edges)
        ax3.bar(bins_edges[:-1], -neg_counts, width=np.diff(bins_edges), align='edge', label="Негативные", color="red", alpha=0.7)

        ax3.axhline(0, color='black')
        ax3.set_title("Время в игре на момент отзыва")
        ax3.set_xlabel("Часы")
        ax3.set_ylabel("Количество отзывов")
        ax3.legend()
        graphs.append(ft.Container(MatplotlibChart(fig3, expand=True), width=900, height=500))
        plt.close(fig3)

        # 4. Распределение разницы playtime по сторонам
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        
        pos_data_diff = df[df["voted_up"] == True]["playtime_diff"]
        neg_data_diff = df[df["voted_up"] == False]["playtime_diff"]

        all_playtime_diff_data = pd.concat([pos_data_diff, neg_data_diff]).dropna()
        if not all_playtime_diff_data.empty:
            _, bins_edges_diff = np.histogram(all_playtime_diff_data, bins=bins)
        else: # Fallback if no playtime diff data
            bins_edges_diff = np.linspace(-50, 50, bins + 1) # Default bins

        pos_counts_diff, _ = np.histogram(pos_data_diff.dropna(), bins=bins_edges_diff)
        ax4.bar(bins_edges_diff[:-1], pos_counts_diff, width=np.diff(bins_edges_diff), align='edge', label="Позитивные", color="green", alpha=0.7)

        neg_counts_diff, _ = np.histogram(neg_data_diff.dropna(), bins=bins_edges_diff)
        ax4.bar(bins_edges_diff[:-1], -neg_counts_diff, width=np.diff(bins_edges_diff), align='edge', label="Негативные", color="red", alpha=0.7)

        ax4.axhline(0, color='black')
        ax4.set_title("Разница в игровом времени (часы)")
        ax4.set_xlabel("Разница (часы)")
        ax4.set_ylabel("Количество отзывов")
        ax4.legend()
        graphs.append(ft.Container(MatplotlibChart(fig4, expand=True), width=900, height=500))
        plt.close(fig4)

        return ft.Column(
            controls=graphs, 
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            expand=True
        )