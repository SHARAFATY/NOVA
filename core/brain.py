import datetime
from collections import defaultdict, Counter

class Brain:
    def __init__(self):
        # Track command usage and habits
        self.habits = defaultdict(list)  # command -> [timestamps]
        self.counter = Counter()

    def update(self, command: str):
        now = datetime.datetime.now()
        self.habits[command].append(now)
        self.counter[command] += 1

    def suggest(self, top_n=3):
        # Suggest most frequent commands
        if not self.counter:
            return []
        return [cmd for cmd, _ in self.counter.most_common(top_n)]

    def get_habits(self):
        # Return commands used at similar times of day
        now = datetime.datetime.now()
        hour = now.hour
        habits = []
        for cmd, times in self.habits.items():
            if any(abs(t.hour - hour) <= 1 for t in times):
                habits.append(cmd)
        return habits 