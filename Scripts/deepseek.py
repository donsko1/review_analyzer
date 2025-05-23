from openai import OpenAI
from typing import List, Dict
from Configs import AI_TOKEN
import json
from pathlib import Path
from Configs import CurrentApp
import re

class TopicAnalyzer:
    def __init__(self, game: CurrentApp, api_key: str = AI_TOKEN, model: str = "deepseek/deepseek-chat"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.language = game.language
        # self.review_type из game.mood будет 'all', но мы будем использовать 'positive'/'negative'
        # для создания имен файлов внутри методов.
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
        self.data_dir = Path("data") # Определяем базовую директорию для данных

    @staticmethod
    def get_keywords_from_json(json_path: Path, mode='grouped') -> Dict[str, List[str]]:
        """
        Загружает ключевые слова из JSON файла.
        :param json_path: Путь к JSON файлу.
        :param mode: 'grouped' для получения тем с ключевыми словами.
        :return: Словарь с темами и ключевыми словами.
        """
        if not json_path.exists():
            print(f"Warning: JSON file not found at {json_path}. Returning empty keywords.")
            return {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if mode == 'grouped':
                # Убедимся, что ключи в data являются строками, представляющими числа,
                # или что они уже в правильном формате.
                # Если ключи - это числа (индексы тем), преобразуем их в строки.
                return {str(topic): info['keywords'] for topic, info in data.items() if 'keywords' in info}
            
            # Режим 'all' или другие режимы, если они будут использоваться,
            # здесь не так актуальны, т.к. LLM нужен сгруппированный список.
            return {} # Возвращаем пустой dict для неактуальных режимов
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_path}: {e}. Returning empty keywords.")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while reading {json_path}: {e}. Returning empty keywords.")
            return {}

    def format_response(self, response_content: str, output_json_path: Path) -> Dict[str, List[str]]:
        """
        Форматирует текстовый ответ LLM в структурированные данные и сохраняет их в JSON.
        :param response_content: Текстовый ответ от LLM.
        :param output_json_path: Путь, куда сохранить форматированный JSON.
        :return: Словарь структурированных данных.
        """
        result = {}
        current_category = None
        
        for line in response_content.split('\n'):
            line = line.strip()
            
            # Определяем категории вида "1. **Название**" или "**Название**"
            if "**" in line:
                # Извлекаем текст между двойными звездочками
                category_match = re.search(r'\*\*(.*?)\*\*', line)
                if category_match:
                    category = category_match.group(1).strip()
                    result[category] = []
                    current_category = category
                else:
                    # Если формат не соответствует ожидаемому, пытаемся извлечь просто текст
                    # после возможной нумерации и до первого знака пунктуации, или всю строку
                    category = line.split('.', 1)[-1].strip() # Удаляем "1."
                    category = category.replace('**', '').strip() # Удаляем **
                    if category:
                        result[category] = []
                        current_category = category
            
            # Определяем подкатегории
            elif line.startswith('-') and current_category:
                # Удаляем "-" и берем текст до двоеточия, если оно есть
                parts = line.lstrip('- ').split(':', 1)
                subcategory = parts[0].strip()
                if subcategory:
                    result[current_category].append(subcategory)
        
        # Сохраняем результат
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True) # Убедимся, что папка data существует
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"Formatted JSON saved to: {output_json_path}")
        except Exception as e:
            print(f"Error saving formatted JSON to {output_json_path}: {e}")
        
        return result

    def analyze_topics(self) -> Dict[str, str]:
        """
        Анализирует ключевые слова для позитивных и негативных отзывов и возвращает 
        структурированный отчеты, сохраняя их в отдельные файлы.
        :return: Словарь с последними полученными ответами LLM по каждому настроению.
        """
        sentiments = ['positive', 'negative']
        all_responses = {}

        for sentiment in sentiments:
            input_json_path = self.data_dir / f"{self.app_id}_{self.language}_{sentiment}_topics.json"
            output_txt_path = self.data_dir / f"{self.app_id}_{self.language}_{sentiment}_topics.txt"
            output_result_json_path = self.data_dir / f"{self.app_id}_{self.language}_{sentiment}_result.json"
            
            print(f"\n--- Analyzing topics for {sentiment} reviews ---")

            keywords_for_llm = self.get_keywords_from_json(input_json_path, mode='grouped')
            
            if not keywords_for_llm:
                print(f"No keywords found for {sentiment} reviews from {input_json_path}. Skipping LLM analysis for this sentiment.")
                # Создаем пустые файлы, чтобы избежать ошибок на следующих этапах
                with open(output_txt_path, "w", encoding="utf-8") as f:
                    f.write(f"No topics found for {sentiment} reviews.")
                with open(output_result_json_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                all_responses[sentiment] = f"No topics found for {sentiment} reviews."
                continue

            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Список слов: {keywords_for_llm}"}
                    ]
                )
                llm_response_content = completion.choices[0].message.content
                
                # Форматируем и сохраняем ответ LLM в JSON
                self.format_response(llm_response_content, output_result_json_path)
                
                # Сохраняем необработанный ответ LLM в TXT файл
                with open(output_txt_path, "w", encoding="utf-8") as f:
                    f.write(llm_response_content)
                
                print(f"LLM analysis completed and saved for {sentiment} reviews.")
                all_responses[sentiment] = llm_response_content

            except Exception as e:
                error_message = f"Error analyzing {sentiment} topics: {str(e)}"
                print(error_message)
                # Сохраняем сообщение об ошибке в TXT и пустой JSON
                with open(output_txt_path, "w", encoding="utf-8") as f:
                    f.write(error_message)
                with open(output_result_json_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                all_responses[sentiment] = error_message
        
        # Возвращаем словарь с результатами по каждому настроению
        return all_responses