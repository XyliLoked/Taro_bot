// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Расширяем на весь экран
tg.expand();

// Показываем, что приложение готово
tg.ready();

// Функция для отправки расклада в бота
function startReading(spreadType) {
    // Показываем загрузку
    showLoading();
    
    // Данные для отправки в бота
    const data = {
        action: 'spread',
        type: spreadType,
        question: 'Общий вопрос' // Здесь можно добавить поле для ввода вопроса позже
    };
    
    // Отправляем данные в бота
    tg.sendData(JSON.stringify(data));
    
    console.log('Отправляем данные:', data); // Для отладки
}

// Функция показа загрузки
function showLoading() {
    const content = document.getElementById('content');
    if (content) {
        content.innerHTML = `
            <div style="
                text-align: center;
                padding: 50px 20px;
                color: white;
            ">
                <h2 style="
                    font-size: 2rem;
                    margin-bottom: 20px;
                    text-shadow: 0 0 15px #8a6bff;
                ">🔮</h2>
                <p style="
                    font-size: 1.2rem;
                    opacity: 0.9;
                ">Получаем расклад...</p>
                <p style="
                    font-size: 0.9rem;
                    opacity: 0.6;
                    margin-top: 10px;
                ">Сосредоточьтесь на своем вопросе</p>
            </div>
        `;
    }
}

// Функция для отображения результата (если нужно показать в Mini App)
function showResult(data) {
    const content = document.getElementById('content');
    if (!content) return;
    
    let cardsHtml = '';
    data.cards.forEach(card => {
        const revSymbol = card.is_reversed ? '🔄' : '';
        cardsHtml += `
            <div class="result-card">
                <h3>${card.position}</h3>
                <p><strong>${card.name} ${revSymbol}</strong></p>
                <p class="meaning">${card.meaning}</p>
            </div>
        `;
    });
    
    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title">🔮 Ваш расклад</h2>
            <div class="cards-grid">
                ${cardsHtml}
            </div>
            <div class="interpretation">
                <h3>📜 Толкование</h3>
                <p>${data.interpretation}</p>
            </div>
            <button onclick="window.location.reload()" class="magic-button" style="margin-top: 20px;">
                <span class="button-text">Новый расклад</span>
            </button>
        </div>
    `;
}

// Слушаем события от Telegram
tg.onEvent('mainButtonClicked', function() {
    tg.close();
});

// Если бот присылает данные (для режима прямого ответа)
tg.onEvent('webAppData', function(data) {
    console.log('Получены данные:', data);
    // Здесь можно обработать данные, если бот пришлет их в Mini App
});

// Добавляем стили для результатов (временно, позже можно перенести в CSS)
const style = document.createElement('style');
style.textContent = `
    .result-container {
        padding: 20px;
        color: white;
    }
    .result-title {
        text-align: center;
        font-size: 2rem;
        margin-bottom: 30px;
        text-shadow: 0 0 15px #8a6bff;
    }
    .result-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
    }
    .result-card h3 {
        color: #b8a0ff;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    .meaning {
        opacity: 0.9;
        margin-top: 8px;
        font-style: italic;
    }
    .interpretation {
        background: rgba(106, 90, 205, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        border-left: 4px solid #8a6bff;
    }
    .interpretation h3 {
        color: #d4b0ff;
        margin-bottom: 10px;
    }
    .interpretation p {
        line-height: 1.6;
        opacity: 0.95;
    }
`;
document.head.appendChild(style);