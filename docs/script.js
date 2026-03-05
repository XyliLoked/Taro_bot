// Получаем данные из Telegram WebApp
const tg = window.Telegram?.WebApp || { 
    ready: () => {}, 
    close: () => {},
    sendData: () => {},
    MainButton: { show: () => {}, hide: () => {}, setText: () => {}, onClick: () => {} }
};

// Уведомляем Telegram, что приложение готово
tg.ready();
tg.expand(); // Растягиваем на весь экран

async function startReading(spreadType) {
    const content = document.getElementById('content');
    content.innerHTML = '<p>🔮 Получаем расклад...</p>';
    
    try {
        // Здесь два варианта:
        
        // ВАРИАНТ А: Отправляем данные в бота (бот сам сгенерирует и пришлет ответ)
        tg.sendData(JSON.stringify({
            action: 'reading',
            spread: spreadType,
            question: 'Общий вопрос' // Можно добавить поле ввода вопроса
        }));
        
        // ВАРИАНТ Б: Прямой запрос к твоему API (если сделаешь)
        /*
        const response = await fetch('https://твой-сервер.com/api/reading', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ spread: spreadType, question: 'Мой вопрос' })
        });
        const data = await response.json();
        displayResult(data);
        */
        
    } catch (error) {
        content.innerHTML = `<p>Ошибка: ${error.message}</p>`;
    }
}

function displayResult(data) {
    let html = '<h2>🔮 Ваш расклад</h2>';
    
    data.cards.forEach(card => {
        const revSymbol = card.is_reversed ? '🔄' : '';
        html += `
            <div class="card">
                <h3>${card.position}</h3>
                <p><strong>${card.name} ${revSymbol}</strong></p>
                <p>${card.meaning}</p>
            </div>
        `;
    });
    
    html += `<div class="card"><h3>📜 Толкование</h3><p>${data.interpretation}</p></div>`;
    html += '<button onclick="window.location.reload()">Новый расклад</button>';
    
    document.getElementById('content').innerHTML = html;
}