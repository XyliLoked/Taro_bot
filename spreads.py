import openai
import json
import random
import os
from typing import List, Dict, Any, Optional
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
    
    def _get_cards_from_names(self, card_names: List[str]) -> List[Dict]:
        """Получить полные данные карт по их названиям"""
        cards_data = []
        for name in card_names:
            for card in CARDS:
                if card.name == name:
                    cards_data.append(self._card_to_dict(card))
                    break
        return cards_data
    
    def _get_random_cards(self, count: int) -> List[Dict]:
        """Вытянуть случайные карты из колоды"""
        selected = random.sample(CARDS, min(count, len(CARDS)))
        return [self._card_to_dict(card) for card in selected]
    
    async def generate_reading(self, 
                               spread_name: str, 
                               positions: List[str], 
                               cards: List[str], 
                               question: str,
                               model: str = "gpt-4o-mini") -> str:
        """
        Генерация интерпретации расклада через OpenAI API
        """
        
        # Получаем полные данные карт
        cards_data = self._get_cards_from_names(cards)
        
        # Формируем описание расклада
        spread_description = f"Расклад: {spread_name}\n\n"
        for i, (pos, card) in enumerate(zip(positions, cards_data)):
            spread_description += f"Позиция {i+1} ({pos}): {card['name']} ({card['position']})\n"
            spread_description += f"Ключевые слова: {', '.join(card['keywords'])}\n"
            if card['position'] == 'прямое':
                spread_description += f"Значение: {card['upright']}\n"
            else:
                spread_description += f"Значение: {card['reversed']}\n"
            spread_description += "\n"
        
        # Создаем промпт для ИИ
        prompt = f"""Ты — опытный таролог с 20-летним стажем. 
        
Вопрос клиента: "{question}"

{spread_description}

Сделай глубокую, персонализированную интерпретацию этого расклада. 
Свяжи значения карт с вопросом клиента. 
Избегай общих фраз — дай конкретный, полезный совет.
Используй спокойный, мудрый, поддерживающий тон.

Формат ответа:
1. Краткое вступление (2-3 предложения)
2. Разбор каждой позиции (связывая с вопросом)
3. Общий вывод и совет
"""
        
        try:
            # Вызов OpenAI API через клиента
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты опытный таролог-психолог."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Ошибка при генерации интерпретации: {str(e)}"
    
    async def three_card_spread(self, question: str) -> Dict[str, Any]:
        """Расклад 'Три карты' (Прошлое-Настоящее-Будущее)"""
        cards = self._get_random_cards(3)
        positions = ["Прошлое", "Настоящее", "Будущее"]
        
        interpretation = await self.generate_reading(
            spread_name="Три карты",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "three_cards",
            "name": "Три карты (Прошлое-Настоящее-Будущее)",
            "positions": positions,
            "cards": cards,
            "interpretation": interpretation
        }
    
    async def relationship_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на отношения (5 карт)"""
        cards = self._get_random_cards(5)
        positions = [
            "Вы в отношениях",
            "Партнер в отношениях", 
            "Что вас связывает",
            "Что мешает",
            "Перспектива"
        ]
        
        interpretation = await self.generate_reading(
            spread_name="Отношения",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "relationship",
            "name": "Расклад на отношения",
            "positions": positions,
            "cards": cards,
            "interpretation": interpretation
        }

    async def career_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на карьеру (4 карты)"""
        cards = self._get_random_cards(4)
        positions = [
            "Текущая ситуация",
            "Возможности", 
            "Препятствия",
            "Результат"
        ]
        
        interpretation = await self.generate_reading(
            spread_name="Карьера",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "career",
            "name": "Расклад на карьеру",
            "positions": positions,
            "cards": cards,
            "interpretation": interpretation
        }
        
    async def celtic_cross_spread(self, question: str) -> Dict[str, Any]:
        """Расклад 'Кельтский крест' (10 карт)"""
        cards = self._get_random_cards(10)
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
        
        interpretation = await self.generate_reading(
            spread_name="Кельтский крест",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "celtic_cross",
            "name": "Кельтский крест",
            "positions": positions,
            "cards": cards,
            "interpretation": interpretation
        }
    
    async def relationship_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на отношения (5 карт)"""
        cards = self._get_random_cards(5)
        positions = [
            "Вы в отношениях",
            "Партнер в отношениях",
            "Что вас связывает",
            "Что мешает",
            "Перспектива"
        ]
        
        interpretation = await self.generate_reading(
            spread_name="Отношения",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "relationship",
            "name": "Расклад на отношения",
            "positions": positions,
            "cards": cards,
            "interpretation": interpretation
        }
    
    async def career_spread(self, question: str) -> Dict[str, Any]:
        """Расклад на карьеру (4 карты)"""
        cards = self._get_random_cards(4)
        positions = [
            "Текущая ситуация",
            "Возможности",
            "Препятствия",
            "Результат"
        ]
        
        interpretation = await self.generate_reading(
            spread_name="Карьера",
            positions=positions,
            cards=[card["name"] for card in cards],
            question=question
        )
        
        return {
            "spread": "career",
            "name": "Расклад на карьеру",
            "positions": positions,
            "cards": cards,
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
    return TarotSpread(openai_api_key=api_key)