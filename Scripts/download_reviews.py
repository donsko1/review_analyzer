import requests
import pandas as pd
from pathlib import Path
import time
import random
from Configs import CurrentApp

class SteamReviewsLoader:
    def __init__(self, game: CurrentApp):
        self.app_id = game.app_id
        self.language = game.language
        self.review_type = game.mood
        self.base_url = f"https://store.steampowered.com/appreviews/{game.app_id}"
        self.params = {
            'json': 1,
            'filter': 'all',
            'language': self.language,
            'review_type': self.review_type,
            'purchase_type': 'all',
            'num_per_page': 100,
            'day_range': game.days_period
        }
        self.reviews = []
        self.cursor = "*"
        self.explored_cursors = set()
        self.data_dir = Path(__file__).parent.parent / "data"

    def _make_request(self):
        try:
            time.sleep(random.uniform(2, 5))
            response = requests.get(self.base_url, params=self.params)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            print(f"Request failed: {e}")
            return None

    @staticmethod
    def _process_reviews(response_data):
        processed = []
        for review in response_data.get('reviews', []):
            author_data = review.pop('author', {})
            review.update(author_data)
            processed.append(review)
        return processed

    def _save_data(self):
        df = pd.DataFrame(self.reviews)
        df = df.drop_duplicates()
        
        selected_columns = df[[
            'recommendationid', 
            'language', 
            'review', 
            'timestamp_created', 
            'voted_up', 
            'playtime_forever', 
            'playtime_at_review'
        ]]
        
        self.data_dir.mkdir(exist_ok=True)
        filename = f"{self.app_id}_{self.language}_{self.review_type}_reviews.csv"
        selected_columns.to_csv(self.data_dir / filename, index=False, encoding='utf-8')
        return len(selected_columns)

    def load(self, max_pages=1000):
        same_cursor_count = 0
        total_loaded = 0

        for _ in range(max_pages):
            if self.cursor in self.explored_cursors:
                print("Cursor loop detected, stopping.")
                break
                
            self.explored_cursors.add(self.cursor)
            self.params['cursor'] = self.cursor

            response = self._make_request()
            if not response:
                break

            new_reviews = self._process_reviews(response)
            if not new_reviews:
                print("No more reviews.")
                break

            self.reviews.extend(new_reviews)
            total_loaded += len(new_reviews)

            new_cursor = response.get('cursor')
            if new_cursor == self.cursor:
                same_cursor_count += 1
                if same_cursor_count >= 3:
                    print("Cursor stuck, resetting.")
                    self.cursor = "*"
                    same_cursor_count = 0
            else:
                self.cursor = new_cursor
                same_cursor_count = 0

            print(f"Loaded {total_loaded} reviews...")

        saved_count = self._save_data()
        print(f"Total saved reviews: {saved_count}")
        return self.reviews

class SteamGameInfo:
    def __init__(self, game: CurrentApp):
        self.app_id = game.app_id
        self.language = game.language
        self.base_url = "https://store.steampowered.com/api/appdetails"
        self.params = {
            'appids': self.app_id,
            'l': self.language
        }
        self.data_dir = Path(__file__).parent.parent / "data"
        self.info = {}
    
    def _make_requests(self):
        try:
            response = requests.get(self.base_url, params=self.params)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            print(f"Request failed: {e}")
            return None
    
    def _save_data(self):
        df = pd.DataFrame([self.info])
        self.data_dir.mkdir(exist_ok=True)

        filename = f"{self.app_id}_{self.language}_info.csv"
        df.to_csv(self.data_dir / filename, index=False, encoding='utf-8')
        print(f"Game info saved to {self.data_dir / filename}")
    
    def load(self):
        response = self._make_requests()
        if not response:
            print("No response from Steam API")
            return None
        
        app_data = response.get(str(self.app_id), {}).get("data", {})
        if not app_data:
            print("No data found for app_id")
            return None
    
        self.info = {
            'name': app_data.get('name'),
            'genres': [g['description'] for g in app_data.get('genres', [])],
            'release_date': app_data.get('release_date', {}).get('date'),
            'developers': app_data.get('developers', []),
            'publishers': app_data.get('publishers', []),
            'short_description': app_data.get('short_description'),
            'header_image': app_data.get('header_image'),
        }

        self._save_data()
        return self.info