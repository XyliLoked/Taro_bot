import openai
import json
import random
import os
from typing import List, Dict, Any, Optional, Tuple
from tarot_cards import TarotDeck  # Импортируем класс колоды

# Создаем экземпляр колоды
deck = TarotDeck()
CARDS = deck.cards  # Получаем список объектов TarotCard

class TarotSpread:
    """Класс для работы с раскладами Таро"""
    
    def __init__(self, gptunnel_api_key: str = None):
        """
        Инициализация с GPTunnel API ключом
        """
        if not gptunnel_api_key:
            gptunnel_api_key = os.getenv("GPTUNNEL_API_KEY")
        
        if not gptunnel_api_key:
            raise ValueError("GPTUNNEL_API_KEY не найден!")
        
        # Используем ключ GPTunnel и их base_url
        self.client = openai.OpenAI(
            api_key=gptunnel_api_key,  # Ключ от GPTunnel!
            base_url="https://gptunnel.ru/v1"
        )
    
    def _card_to_dict(self, card, position=None):
        """Преобразует объект TarotCard в словарь"""
        if position is None:
            position = random.choice(["прямое", "перевернутое"])
            
        card_dict = {
            "name": card.name,
            "position": position,
            "upright": card.meaning_up,
            "reversed": card.meaning_rev,
            "suit": card.suit,
            "number": card.number,
            "arcana": card.arcana
        }
        
        # Генерируем ключевые слова из значений
        if position == "прямое":
            keywords = card.meaning_up.lower().split()[:3]
        else:
            keywords = card.meaning_rev.lower().split()[:3]
        card_dict["keywords"] = keywords
        
        return card_dict
    
    def _get_cards_from_names(self, cards_with_positions: List[Tuple[str, str]]) -> List[Dict]:
        """
        Получить полные данные карт по их названиям с сохранением позиций
        cards_with_positions: список кортежей (имя_карты, позиция)
        """
        cards_data = []
        for name, position in cards_with_positions:
            for card in CARDS:
                if card.name == name:
                    # Передаем СОХРАНЕННУЮ позицию!
                    cards_data.append(self._card_to_dict(card, position))
                    break
        return cards_data
    
    def _get_random_cards(self, count: int) -> List[Dict]:
        """Вытянуть случайные карты из колоды"""
        selected = random.sample(CARDS, min(count, len(CARDS)))
        return [self._card_to_dict(card) for card in selected]
    
    async def generate_reading(self, 
                           spread_name: str, 
                           positions: List[str], 
                           cards_with_positions: List[Tuple[str, str]], 
                           question: str,
                           model: str = "gpt-4o-mini") -> str:
        """
        Генерация глубокой интерпретации расклада через GPTunnel
        cards_with_positions: список кортежей (имя_карты, позиция)
        """
        
        # Получаем полные данные карт с сохранением позиций
        cards_data = self._get_cards_from_names(cards_with_positions)
        
        combinations = self.analyze_combinations(cards_data)
        combinations_text = "\n".join(combinations) if combinations else "Нет особых сочетаний"
        
        # Формируем описание расклада с акцентом на взаимосвязи
        spread_description = f"📋 РАСКЛАД: {spread_name}\n\n"
        spread_description += f"❓ ВОПРОС КЛИЕНТА: {question}\n\n"
        spread_description += "🃏 КАРТЫ В РАСКЛАДЕ:\n"
        
        cards_list = []
        for i, (pos, card) in enumerate(zip(positions, cards_data)):
            card_info = f"{i+1}. ПОЗИЦИЯ «{pos}»\n"
            card_info += f"   КАРТА: {card['name']} ({card['position']})\n"
            if card['position'] == 'прямое':
                card_info += f"   ЗНАЧЕНИЕ: {card['upright']}\n"
            else:
                card_info += f"   ЗНАЧЕНИЕ: {card['reversed']}\n"
            cards_list.append(card_info)
        
        spread_description += "\n".join(cards_list)
        
        # СОЗДАЕМ УЛУЧШЕННЫЙ ПРОМПТ
        prompt = f"""ТЫ — МАСТЕР ТАРО И ПСИХОЛОГ
    Ты обладаешь глубокими знаниями символизма Таро, юнгианской психологии и практической мудростью. Твоя задача — дать клиенту не просто значения карт, а целостное, терапевтическое послание.

    {spread_description}

    ОСОБЫЕ СОЧЕТАНИЯ:
    {combinations_text}

    Учти эти сочетания в своей интерпретации - они очень важны!
    
    ИНСТРУКЦИЯ ПО ИНТЕРПРЕТАЦИИ:

    1. 🔮 ОБЩАЯ АТМОСФЕРА (2-3 предложения)
    - Какая энергия доминирует в раскладе?
    - Как карты связаны между собой?
    - Что это говорит о ситуации клиента?

    2. 📍 РАЗБОР КАЖДОЙ ПОЗИЦИИ
    Для каждой карты объясни:
    - Что эта карта говорит ИМЕННО в контексте вопроса клиента
    - Как ее значение связано с конкретной позицией
    - Какие эмоции/мысли/действия она описывает

    3. 🔗 КЛЮЧЕВЫЕ СОЧЕТАНИЯ
    - Какие карты усиливают друг друга?
    - Где есть напряжение или конфликт?
    - Что это означает для развития ситуации?

    4. 💡 ГЛАВНОЕ ПОСЛАНИЕ
    - Что клиент должен понять из этого расклада?
    - Какая мудрость здесь скрыта?

    5. 🌟 ПРАКТИЧЕСКИЙ СОВЕТ
    - Конкретные действия на основе карт
    - На что обратить внимание
    - Чего остерегаться

    СТИЛЬ:
    - Говори с уважением и эмпатией
    - Избегай общих фраз и воды
    - Будь конкретным, но мягким
    - Используй метафоры, если уместно
    - Заверши вдохновляющей нотой

    ПОМНИ: Ты говоришь с живым человеком, который доверил тебе свои сокровенные вопросы."""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты — мудрый таролог-психолог, сочетающий глубокое знание символов Таро с психологической чуткостью."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85,  # Чуть выше для креативности
                max_tokens=1500     # Больше токенов для детального ответа
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Ошибка при генерации интерпретации: {str(e)}"
    
    def analyze_combinations(self, cards_data: List[Dict]) -> List[str]:
        """Анализ особых сочетаний карт"""
        combinations = []
        names = [card["name"] for card in cards_data]
        positions = [card.get("position", "прямое") for card in cards_data]
        
        # Словарь особых сочетаний
        special_pairs = [
            (("Шут", "Смерть"), "🦋 Полная трансформация, начало новой главы"),
            (("Влюбленные", "Дьявол"), "❤️‍🔥 Страстная, но потенциально зависимая связь"),
            (("Маг", "Император"), "👑 Большая власть и влияние, лидерство"),
            (("Жрица", "Луна"), "🌙 Сильная интуиция, возможно скрытое знание"),
            (("Солнце", "Звезда"), "⭐ Очень позитивный период, надежды сбудутся"),
            (("Башня", "Суд"), "⚡ Неожиданное пробуждение, судьбоносные перемены"),
            (("Колесница", "Мир"), "🏆 Успех в путешествиях или международных делах"),
            (("Отшельник", "Луна"), "🕯️ Глубокий внутренний поиск, возможно одиночество"),
            (("Сила", "Дьявол"), "🦁 Борьба с искушениями или зависимостями"),
            (("Умеренность", "Звезда"), "⚖️ Исцеление, восстановление баланса"),
        ]
        
        # Проверяем пары
        for (card1, card2), meaning in special_pairs:
            if card1 in names and card2 in names:
                idx1 = names.index(card1)
                idx2 = names.index(card2)
                # Проверяем позиции (прямые/перевернутые)
                if positions[idx1] == "прямое" and positions[idx2] == "прямое":
                    combinations.append(f"✨ {meaning}")
                elif positions[idx1] == "перевернутое" or positions[idx2] == "перевернутое":
                    combinations.append(f"⚠️ {meaning} (но с осложнениями)")
        
        # Анализ большинства одной масти
        suits = [card.get("suit") for card in cards_data if card.get("suit")]
        if suits:
            from collections import Counter
            suit_counts = Counter(suits)
            dominant_suit, count = suit_counts.most_common(1)[0]
            if count >= 3:
                suit_meanings = {
                    "wands": "🔥 Много энергии Жезлов - действия, страсть, творчество",
                    "cups": "💧 Много Кубков - эмоции, отношения, чувства",
                    "swords": "⚔️ Много Мечей - мысли, конфликты, решения",
                    "pentacles": "💰 Много Пентаклей - деньги, работа, материальное"
                }
                combinations.append(f"📊 Доминирует масть: {suit_meanings.get(dominant_suit, '')}")
        
        # Анализ старших арканов
        major_count = sum(1 for card in cards_data if card.get("arcana") == "major")
        if major_count >= 4:
            combinations.append("🌟 Много Старших Арканов - судьбоносный период, важные уроки")
        
        return combinations

    async def three_card_spread(self, question: str) -> Dict[str, Any]:
        """Расклад 'Три карты' (Прошлое-Настоящее-Будущее)"""
        cards_dicts = self._get_random_cards(3)
        positions = ["Прошлое", "Настоящее", "Будущее"]
        
        # Создаем список кортежей (имя, позиция)
        cards_with_positions = [(card["name"], card["position"]) for card in cards_dicts]
        
        interpretation = await self.generate_reading(
            spread_name="Три карты",
            positions=positions,
            cards_with_positions=cards_with_positions,
            question=question
        )
        
        return {
            "spread": "three_cards",
            "name": "Три карты (Прошлое-Настоящее-Будущее)",
            "positions": positions,
            "cards": cards_dicts,  # Возвращаем полные данные карт
            "interpretation": interpretation
        }
    
    async def relationship_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на отношения (5 карт)"""
        cards_dicts = self._get_random_cards(5)
        positions = [
            "Вы в отношениях",
            "Партнер в отношениях", 
            "Что вас связывает",
            "Что мешает",
            "Перспектива"
        ]
        
        # Создаем список кортежей (имя, позиция)
        cards_with_positions = [(card["name"], card["position"]) for card in cards_dicts]
        
        interpretation = await self.generate_reading(
            spread_name="Отношения",
            positions=positions,
            cards_with_positions=cards_with_positions,
            question=question
        )
        
        return {
            "spread": "relationship",
            "name": "Расклад на отношения",
            "positions": positions,
            "cards": cards_dicts,
            "interpretation": interpretation
        }

    async def career_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на карьеру (4 карты)"""
        cards_dicts = self._get_random_cards(4)
        positions = [
            "Текущая ситуация",
            "Возможности", 
            "Препятствия",
            "Результат"
        ]
        
        # Создаем список кортежей (имя, позиция)
        cards_with_positions = [(card["name"], card["position"]) for card in cards_dicts]
        
        interpretation = await self.generate_reading(
            spread_name="Карьера",
            positions=positions,
            cards_with_positions=cards_with_positions,
            question=question
        )
        
        return {
            "spread": "career",
            "name": "Расклад на карьеру",
            "positions": positions,
            "cards": cards_dicts,
            "interpretation": interpretation
        }
        
    async def celtic_cross_spread(self, question: str) -> Dict[str, Any]:
        """Расклад 'Кельтский крест' (10 карт)"""
        cards_dicts = self._get_random_cards(10)
        positions = [
            "Ситуация (центр)",
            "Препятствие (пересекает)",
            "Основа (что внизу)",
            "Недавнее прошлое (что позади)",
            "Сознание (что вверху)",
            "Будущее (что впереди)",
            "Самооценка (позиция себя)",
            "Окружение (внешние факторы)",
            "Надежды и страхи",
            "Итог (результат)"
        ]
        
        # Создаем список кортежей (имя, позиция)
        cards_with_positions = [(card["name"], card["position"]) for card in cards_dicts]
        
        interpretation = await self.generate_reading(
            spread_name="Кельтский крест",
            positions=positions,
            cards_with_positions=cards_with_positions,
            question=question
        )
        
        return {
            "spread": "celtic_cross",
            "name": "Кельтский крест",
            "positions": positions,
            "cards": cards_dicts,
            "interpretation": interpretation
        }
    
    async def daily_spread(self) -> Dict[str, Any]:
        """Ежедневный расклад (1 карта дня)"""
        card = self._get_random_cards(1)[0]
        
        # Для одной карты делаем простой промпт
        prompt = f"""Карта дня: {card['name']} ({card['position']})
Ключевые слова: {', '.join(card['keywords'])}
Значение: {card['upright'] if card['position'] == 'прямое' else card['reversed']}

Дай совет на сегодня, связанный с этой картой. 2-3 предложения."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты мудрый советчик."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            interpretation = response.choices[0].message.content
            
        except Exception as e:
            interpretation = f"Карта дня: {card['name']}\n\nСовет: Доверьтесь интуиции сегодня."
        
        return {
            "spread": "daily",
            "name": "Карта дня",
            "positions": ["Совет на сегодня"],
            "cards": [card],
            "interpretation": interpretation
        }


# Функция-помощник для быстрого создания экземпляра
def create_spread_maker(api_key: str = None):
    """Создать объект для работы с раскладами"""
    return TarotSpread(gptunnel_api_key=api_key)