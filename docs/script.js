// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Расширяем на весь экран
tg.expand();

// Показываем, что приложение готово
tg.ready();

// Функция для отправки расклада в бота
function startReading(spreadType) {
    // Получаем вопрос из текстового поля
    const questionInput = document.getElementById('userQuestion');
    let userQuestion = '';
    
    if (questionInput) {
        userQuestion = questionInput.value.trim();
    }
    
    // Если вопрос пустой, используем стандартный
    const finalQuestion = userQuestion || "Общий вопрос без уточнения";
    
    // Показываем загрузку
    showLoading();
    
    // Данные для отправки в бота
    const data = {
        action: 'spread',
        type: spreadType,
        question: finalQuestion
    };
    
    // Отправляем данные в бота
    tg.sendData(JSON.stringify(data));
    
    console.log('Отправляем данные:', data);
}

// Функция показа загрузки
// Эффектная загрузка с анимацией карт (версия 1)
function showLoading() {
    const content = document.getElementById('content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="loading-container">
            <div class="magic-circle">
                <div class="sparkles"></div>
                <div class="cards-stack">
                    <div class="card-animation card-1">🃏</div>
                    <div class="card-animation card-2">🎴</div>
                    <div class="card-animation card-3">🃏</div>
                    <div class="card-animation card-4">🎴</div>
                    <div class="card-animation card-5">🃏</div>
                </div>
                <div class="crystal-ball">
                    <div class="inner-light"></div>
                </div>
            </div>
            
            <h2 class="loading-title"> ТАСУЕМ 🔮 КОЛОДУ 🔮</h2>
            
            <div class="fortune-text">
                <p class="fortune-line">Сосредоточьтесь на своем вопросе...</p>
                <p class="fortune-line">Карты уже чувствуют вашу энергию</p>
            </div>
            
            <div class="magic-progress">
                <div class="progress-bar"></div>
            </div>
            
            <div class="prediction-bubbles">
                <span>✨</span>
                <span>⭐</span>
                <span>🌟</span>
                <span>💫</span>
                <span>⚡</span>
            </div>
        </div>
    `;
    
    // Добавляем стили для анимации
    const style = document.createElement('style');
    style.textContent = `
        .loading-container {
            text-align: center;
            padding: 20px;
            min-height: 60vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .magic-circle {
            width: 200px;
            height: 200px;
            margin: 20px auto;
            position: relative;
            animation: rotateGlow 3s infinite alternate;
        }
        
        @keyframes rotateGlow {
            0% { transform: scale(1) rotate(0deg); filter: hue-rotate(0deg); }
            100% { transform: scale(1.1) rotate(10deg); filter: hue-rotate(30deg); }
        }
        
        .cards-stack {
            position: relative;
            width: 100%;
            height: 100%;
        }
        
        .card-animation {
            position: absolute;
            font-size: 2.5rem;
            width: 60px;
            height: 90px;
            background: linear-gradient(145deg, #2a1b3d, #4a2b5e);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px rgba(138, 43, 226, 0.6);
            border: 2px solid rgba(255, 215, 0, 0.3);
            animation: shuffleCard 2s infinite;
            transform-origin: center;
            left: 50%;
            top: 50%;
            margin-left: -30px;
            margin-top: -45px;
        }
        
        .card-1 { animation-delay: 0s; transform: rotate(-10deg) translateY(-20px); }
        .card-2 { animation-delay: 0.2s; transform: rotate(-5deg) translateY(-10px); }
        .card-3 { animation-delay: 0.4s; transform: rotate(0deg); }
        .card-4 { animation-delay: 0.6s; transform: rotate(5deg) translateY(10px); }
        .card-5 { animation-delay: 0.8s; transform: rotate(10deg) translateY(20px); }
        
        @keyframes shuffleCard {
            0% { transform: rotate(0deg) translateY(0px) scale(1); opacity: 0.8; }
            25% { transform: rotate(15deg) translateY(-30px) scale(1.2); opacity: 1; }
            50% { transform: rotate(-15deg) translateY(30px) scale(1.1); opacity: 0.9; }
            75% { transform: rotate(5deg) translateY(-15px) scale(1.15); opacity: 1; }
            100% { transform: rotate(0deg) translateY(0px) scale(1); opacity: 0.8; }
        }
        
        .crystal-ball {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #ffffff, #c0b0ff, #8a6bff);
            opacity: 0.2;
            filter: blur(10px);
            animation: pulseCrystal 2s infinite;
            z-index: -1;
        }
        
        @keyframes pulseCrystal {
            0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.2; }
            50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
            100% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.2; }
        }
        
        .inner-light {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            box-shadow: inset 0 0 50px #ffd700;
            animation: innerPulse 3s infinite;
        }
        
        @keyframes innerPulse {
            0% { box-shadow: inset 0 0 30px #8a6bff; }
            50% { box-shadow: inset 0 0 80px #b8a0ff; }
            100% { box-shadow: inset 0 0 30px #8a6bff; }
        }
        
        .loading-title {
            font-size: 1.8rem;
            color: white;
            text-shadow: 0 0 20px #8a6bff;
            margin: 30px 0 20px;
            animation: titleFlicker 2s infinite;
        }
        
        @keyframes titleFlicker {
            0% { opacity: 0.9; text-shadow: 0 0 20px #8a6bff; }
            50% { opacity: 1; text-shadow: 0 0 40px #b8a0ff, 0 0 60px #9370db; }
            100% { opacity: 0.9; text-shadow: 0 0 20px #8a6bff; }
        }
        
        .fortune-text {
            margin: 20px 0;
        }
        
        .fortune-line {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            margin: 8px 0;
            opacity: 0;
            animation: fadeInLine 1s forwards;
        }
        
        .fortune-line:nth-child(1) { animation-delay: 0.5s; }
        .fortune-line:nth-child(2) { animation-delay: 1.5s; }
        
        @keyframes fadeInLine {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .magic-progress {
            width: 80%;
            max-width: 300px;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            margin: 30px auto;
            overflow: hidden;
            position: relative;
        }
        
        .progress-bar {
            width: 30%;
            height: 100%;
            background: linear-gradient(90deg, #8a6bff, #b8a0ff, #9370db);
            border-radius: 4px;
            animation: progressMove 2s infinite;
            position: absolute;
        }
        
        @keyframes progressMove {
            0% { left: -30%; }
            100% { left: 100%; }
        }
        
        .prediction-bubbles {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .prediction-bubbles span {
            font-size: 1.5rem;
            animation: bubbleFloat 2s infinite;
            opacity: 0.6;
        }
        
        .prediction-bubbles span:nth-child(1) { animation-delay: 0s; }
        .prediction-bubbles span:nth-child(2) { animation-delay: 0.3s; }
        .prediction-bubbles span:nth-child(3) { animation-delay: 0.6s; }
        .prediction-bubbles span:nth-child(4) { animation-delay: 0.9s; }
        .prediction-bubbles span:nth-child(5) { animation-delay: 1.2s; }
        
        @keyframes bubbleFloat {
            0% { transform: translateY(0) scale(1); opacity: 0.6; }
            50% { transform: translateY(-15px) scale(1.2); opacity: 1; }
            100% { transform: translateY(0) scale(1); opacity: 0.6; }
        }
        
        .sparkles {
            position: absolute;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 50% 50%, #ffffff, transparent 70%);
            animation: sparkleRotate 4s infinite linear;
            opacity: 0.3;
        }
        
        @keyframes sparkleRotate {
            from { transform: rotate(0deg) scale(1); }
            to { transform: rotate(360deg) scale(1.2); }
        }
    `;
    document.head.appendChild(style);
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