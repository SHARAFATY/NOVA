import datetime
from collections import defaultdict, Counter, deque
from rapidfuzz import fuzz
from dateutil.parser import parse as parse_dt

class Brain:
    def __init__(self, memory=None):
        # Track command usage and habits
        self.habits = defaultdict(list)  # command -> [timestamps]
        self.counter = Counter()
        self.recent_commands = deque(maxlen=20)
        self.conversation_history = deque(maxlen=50)
        self.user_preferences = {}
        self.skills = []
        self.memory = memory
        if memory and hasattr(memory, 'data'):
            self._load_from_memory(memory.data)

    def _load_from_memory(self, data):
        self.habits.update({
            k: [parse_dt(t) if isinstance(t, str) else t for t in v]
            for k, v in data.get('habits', {}).items()
        })
        self.counter.update(data.get('counter', {}))
        self.recent_commands.extend([
            (cmd, parse_dt(t) if isinstance(t, str) else t)
            for cmd, t in data.get('recent_commands', [])
        ])
        self.conversation_history.extend([
            (parse_dt(t) if isinstance(t, str) else t, cmd, res)
            for t, cmd, res in data.get('conversation_history', [])
        ])
        self.user_preferences.update(data.get('user_preferences', {}))
        self.skills = data.get('skills', [])

    def update(self, command: str, result: str = None):
        now = datetime.datetime.now()
        self.habits[command].append(now)
        self.counter[command] += 1
        self.recent_commands.append((command, now))
        if result:
            self.conversation_history.append((now, command, result))
        if self.memory:
            self.save_to_memory()

    def save_to_memory(self):
        if not self.memory:
            return
        self.memory.data['habits'] = {k: [t.isoformat() for t in v] for k, v in self.habits.items()}
        self.memory.data['counter'] = dict(self.counter)
        self.memory.data['recent_commands'] = [
            (cmd, t.isoformat() if isinstance(t, datetime.datetime) else t)
            for cmd, t in self.recent_commands
        ]
        self.memory.data['conversation_history'] = [
            (t.isoformat() if isinstance(t, datetime.datetime) else t, cmd, res)
            for t, cmd, res in self.conversation_history
        ]
        self.memory.data['user_preferences'] = self.user_preferences
        self.memory.data['skills'] = self.skills
        self.memory.save()

    def learn_skill(self, example_input, example_action):
        self.skills.append({'input': example_input, 'action': example_action})
        if self.memory:
            self.memory.data['skills'] = self.skills
            self.memory.save()

    def match_skill(self, user_input, threshold=80):
        best = None
        best_score = 0
        for skill in self.skills:
            score = fuzz.partial_ratio(user_input.lower(), skill['input'].lower())
            if score > best_score:
                best = skill
                best_score = score
        if best and best_score >= threshold:
            return best['action']
        return None

    def suggest(self, top_n=3):
        # Suggest most frequent and most recent commands
        suggestions = [cmd for cmd, _ in self.counter.most_common(top_n)]
        recent = [cmd for cmd, _ in self.recent_commands if cmd not in suggestions]
        return suggestions + recent[:max(0, top_n - len(suggestions))]

    def get_habits(self):
        # Return commands used at similar times of day
        now = datetime.datetime.now()
        hour = now.hour
        habits = []
        for cmd, times in self.habits.items():
            if any(abs(t.hour - hour) <= 1 for t in times if isinstance(t, datetime.datetime)):
                habits.append(cmd)
        return habits

    def get_context(self):
        # Return last few conversation turns for context-aware responses
        return list(self.conversation_history)[-5:]

    def set_preference(self, key, value):
        self.user_preferences[key] = value
        if self.memory:
            self.save_to_memory()

    def get_preference(self, key, default=None):
        return self.user_preferences.get(key, default) 