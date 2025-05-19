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