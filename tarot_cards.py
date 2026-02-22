class TarotCard:
    def __init__(self, name, number, arcana, suit=None, meaning_up=None, meaning_rev=None, description=None):
        self.name = name
        self.number = number
        self.arcana = arcana  # 'major' или 'minor'
        self.suit = suit  # 'wands', 'cups', 'swords', 'pentacles' или None для старших арканов
        self.meaning_up = meaning_up
        self.meaning_rev = meaning_rev
        self.description = description

class TarotDeck:
    def __init__(self):
        self.cards = self._create_deck()
    
    def _create_deck(self):
        cards = []
        
        # Старшие арканы (22 карты)
        major_arcana = [
            TarotCard("Шут", 0, "major", 
                     meaning_up="Начало, невинность, спонтанность",
                     meaning_rev="Безрассудство, риск, незрелость"),
            TarotCard("Маг", 1, "major",
                     meaning_up="Воля, мастерство, концентрация",
                     meaning_rev="Манипуляция, слабая воля, обман"),
            TarotCard("Верховная Жрица", 2, "major",
                     meaning_up="Интуиция, тайна, подсознание",
                     meaning_rev="Скрытые мотивы, поверхностность"),
            TarotCard("Императрица", 3, "major",
                     meaning_up="Изобилие, природа, материнство",
                     meaning_rev="Зависимость, расточительство"),
            TarotCard("Император", 4, "major",
                     meaning_up="Авторитет, структура, контроль",
                     meaning_rev="Тирания, жесткость, негибкость"),
            # ... добавьте остальные старшие арканы
        ]
        
        # Младшие арканы - Жезлы (Wands)
        wands = [
            TarotCard("Туз Жезлов", 1, "minor", "wands",
                     meaning_up="Вдохновение, энергия, потенциал",
                     meaning_rev="Задержки, разочарование"),
            TarotCard("Двойка Жезлов", 2, "minor", "wands",
                     meaning_up="Планирование, решение, будущее",
                     meaning_rev="Страх, отсутствие планирования"),
            # ... добавьте остальные карты жезлов
        ]
        
        # Младшие арканы - Кубки (Cups)
        cups = [
            TarotCard("Туз Кубков", 1, "minor", "cups",
                     meaning_up="Любовь, эмоции, новые чувства",
                     meaning_rev="Эмоциональная пустота"),
            # ... добавьте остальные карты кубков
        ]
        
        # Младшие арканы - Мечи (Swords)
        swords = [
            TarotCard("Туз Мечей", 1, "minor", "swords",
                     meaning_up="Правда, прорыв, ясность",
                     meaning_rev="Конфликт, негативные мысли"),
            # ... добавьте остальные карты мечей
        ]
        
        # Младшие арканы - Пентакли (Pentacles)
        pentacles = [
            TarotCard("Туз Пентаклей", 1, "minor", "pentacles",
                     meaning_up="Процветание, новые возможности",
                     meaning_rev="Упущенные возможности"),
            # ... добавьте остальные карты пентаклей
        ]
        
        cards = major_arcana + wands + cups + swords + pentacles
        return cards
    
    def get_card_by_name(self, name):
        for card in self.cards:
            if card.name.lower() == name.lower():
                return card
        return None
    
    def get_random_card(self):
        import random
        return random.choice(self.cards)
    
    def shuffle(self):
        import random
        random.shuffle(self.cards)
        return self.cards