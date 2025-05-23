AI_TOKEN = "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"
mood_list = ['positive', 'negative', 'all']
language_list = ['russian', 'english']

app_id = ""
current_language = language_list[0]
current_mood = mood_list[0]
day_range=30

class CurrentApp:
    def __init__(self, app_id, language='english', mood='all', days_period=999999999):
        self.app_id = app_id
        self.language = language
        self.mood = mood
        self.days_period = days_period
        pass