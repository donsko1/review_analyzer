from openai import OpenAI
from typing import List, Dict
from Configs import AI_TOKEN
import json
from pathlib import Path
from Configs import CurrentApp

class TopicAnalyzer:
    def __init__(self, game: CurrentApp, api_key: str = AI_TOKEN, model: str = "deepseek/deepseek-chat"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.language = game.language
        self.review_type = game.mood
        self.app_id = game.app_id
        self.system_prompt = """
            Ты анализируешь отзывы игроков на видеоигры. 
            Ты получил Сгруппированные по темам ключевые слова. Тебе нужно сформировать тематические категории для каждой темы на основе ключевых слов связанных с игровым опытом, для каждой темы. Учитывай контекст:
            - Исправь очевидные опечатки
            - Назови каждую тему 2-3 словами
            - Внутри тем выдели подкатегории через ":" и приведи примеры слов
            - Избегай общих формулировок вроде "Другое"

            **Пример структуры ответа:**
            1. **Название темы**  
            - Подкатегория: пример, пример  
            - Подкатегория: пример, пример

            **Правила:**  
            - Не добавляй слова, которых нет в списке  
            - Если слово повторяется - объедини его  
            - Пиши на русском, используй markdown
        """

    @staticmethod
    def get_keywords_from_json(json_path, mode='all'):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if mode == 'grouped':
            return {topic: info['keywords'] for topic, info in data.items()}
        
        all_keywords = []
        for topic_info in data.values():
            all_keywords.extend(topic_info['keywords'])
        
        if mode == 'all':
            return list(set(all_keywords))  # Уникальные ключи
        
        return all_keywords

    def analyze_topics(self) -> str:
        """Анализирует ключевые слова и возвращает структурированный отчет"""
        json_path = Path("data") / f"{self.app_id}_{self.language}_{self.review_type}_topics.json".replace("/", "\\")
        keywords = self.get_keywords_from_json(json_path, mode='grouped')
        txt_path = Path("data") / f"{self.app_id}_{self.language}_{self.review_type}_topics.txt".replace("/", "\\")
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Список слов: {keywords}"}
                ]
            )
            self.format_response(completion.choices[0].message.content)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(completion.choices[0].message.content)
            
            return completion.choices[0].message.content
        except Exception as e:
            return f"Ошибка анализа: {str(e)}"

    #@staticmethod
    def format_response(self, response: str) -> Dict[str, List[str]]:
        """Форматирует текстовый ответ в структурированные данные"""
        result = {}
        current_category = None
        json_path = Path("data") / f"{self.app_id}_{self.language}_{self.review_type}_result.json".replace("/", "\\")
        
        for line in response.split('\n'):
            line = line.strip()  # Удаляем пробелы по краям
            
            # Определяем категории вида "1. **Название**" или "**Название**"
            if "**" in line:
                # Удаляем всё до ** и после **, включая номерацию (например, "1. ")
                category = line.split("**")[1].strip()
                result[category] = []
                current_category = category
                
            # Определяем подкатегории
            elif line.startswith('-') and current_category:
                # Удаляем "-" и берем текст до двоеточия
                subcategory = line.split(':')[0].lstrip('- ').strip()
                result[current_category].append(subcategory)
        
        # Сохраняем результат
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        return result
    