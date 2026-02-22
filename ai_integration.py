import openai
import json
from typing import List, Dict, Any
from config import config
import aiohttp
import asyncio

class AIIntegration:
    def __init__(self):
        self.openai_client = None
        if config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    async def generate_reading_interpretation(self, spread_name: str, cards: List[Dict], question: str = None) -> str:
        """
        Генерирует интерпретацию расклада с помощью ИИ
        """
        # Формируем описание карт
        cards_description = ""
        for i, card in enumerate(cards):
            position = card.get('position', f"Позиция {i+1}")
            orientation = "прямая" if card['is_upright'] else "перевернутая"
            meaning = card['card'].meaning_up if card['is_upright'] else card['card'].meaning_rev
            
            cards_description += f"{position}: {card['card'].name} ({orientation})\n"
            cards_description += f"Значение: {meaning}\n\n"
        
        # Промпт для ИИ
        prompt = f"""
        Ты опытный таролог с глубоким пониманием символики карт Таро.
        
        Расклад: {spread_name}
        Вопрос клиента: {question if question else "Общий расклад"}
        
        Карты в раскладе:
        {cards_description}
        
        Проанализируй этот расклад и предоставь:
        1. Общую интерпретацию расклада
        2. Значение каждой карты в её позиции
        3. Связи между картами
        4. Практические рекомендации
        5. Возможные предостережения (если есть)
        
        Будь глубоким, но понятным. Учитывай контекст вопроса.
        Ответ должен быть на русском языке, объёмом 300-500 слов.
        """
        
        # Пробуем разные API по очереди
        try:
            if self.openai_client:
                return await self._generate_with_openai(prompt)
        except Exception as e:
            print(f"OpenAI error: {e}")
        
        # Если OpenAI не сработал, пробуем другие варианты
        try:
            return await self._generate_with_google_ai(prompt)
        except:
            pass
        
        # Если все API недоступны, возвращаем базовую интерпретацию
        return self._generate_basic_interpretation(cards, spread_name, question)
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Генерация через OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model=config.AI_MODEL,
            messages=[
                {"role": "system", "content": "Ты опытный таролог, дающий мудрые и точные интерпретации раскладов Таро."},
                {"role": "user", "content": prompt}
            ],
            temperature=config.AI_TEMPERATURE,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    async def _generate_with_google_ai(self, prompt: str) -> str:
        """Генерация через Google AI API (альтернатива)"""
        import google.generativeai as genai
        
        genai.configure(api_key=config.GOOGLE_AI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(prompt)
        return response.text
    
    def _generate_basic_interpretation(self, cards: List[Dict], spread_name: str, question: str) -> str:
        """Базовая интерпретация без ИИ"""
        interpretation = f"📜 *Расклад: {spread_name}*\n\n"
        
        if question:
            interpretation += f"*Вопрос:* {question}\n\n"
        
        interpretation += "*Карты в раскладе:*\n"
        for i, card in enumerate(cards):
            position = card.get('position', f"Позиция {i+1}")
            orientation = "прямая" if card['is_upright'] else "перевернутая"
            meaning = card['card'].meaning_up if card['is_upright'] else card['card'].meaning_rev
            
            interpretation += f"\n{position}: *{card['card'].name}* ({orientation})\n"
            interpretation += f"Значение: {meaning}\n"
        
        interpretation += "\n\n*Общая интерпретация:*\n"
        interpretation += "Этот расклад показывает... (базовая интерпретация)\n\n"
        interpretation += "*Рекомендации:*\n"
        interpretation += "1. Обратите внимание на первую карту\n"
        interpretation += "2. Рассмотрите взаимосвязи между картами\n"
        interpretation += "3. Учтите перевернутые позиции\n"
        
        return interpretation
    
    async def generate_card_interpretation(self, card, is_upright: bool, context: str = "") -> str:
        """Генерация детальной интерпретации отдельной карты"""
        orientation = "прямой" if is_upright else "перевернутой"
        meaning = card.meaning_up if is_upright else card.meaning_rev
        
        prompt = f"""
        Карта Таро: {card.name}
        Позиция: {orientation}
        Основное значение: {meaning}
        
        Контекст запроса: {context if context else "Общая интерпретация"}
        
        Дай развернутую интерпретацию этой карты в указанной позиции.
        Рассмотри:
        1. Символику карты
        2. Практическое применение в жизни
        3. Советы по работе с энергией карты
        4. Предостережения (если есть)
        
        Ответ на русском языке, 150-250 слов.
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": "Ты таролог, специализирующийся на детальных интерпретациях карт."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.AI_TEMPERATURE,
                    max_tokens=500
                )
                return response.choices[0].message.content
        except:
            pass
        
        # Базовая интерпретация
        return f"*{card.name}* ({orientation})\n\nЗначение: {meaning}\n\nЭта карта указывает на..."

# Создаем глобальный экземпляр
ai_integration = AIIntegration()