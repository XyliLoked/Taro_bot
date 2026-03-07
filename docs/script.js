// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Расширяем на весь экран
tg.expand();

// Показываем, что приложение готово
tg.ready();

// ЭТО ВАЖНО: проверяем, что WebApp действительно загружен
console.log("Telegram WebApp initialized:", tg);

// Функция для отправки расклада в бота
function startReading(spreadType) {
    // Получаем вопрос из текстового поля
    const questionInput = document.getElementById('userQuestion');
    let userQuestion = questionInput ? questionInput.value.trim() : '';
    const finalQuestion = userQuestion || "Общий вопрос без уточнения";
    
    // Показываем загрузку
    showLoading();
    
    // Получаем initData (там есть query_id)
    const initData = window.Telegram.WebApp.initData;
    console.log("initData:", initData);
    
    // Отправляем данные на свой сервер
    fetch('https://tarobot-production-99c8.up.railway.app/webapp-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'spread',
            type: spreadType,
            question: finalQuestion,
            initData: window.Telegram.WebApp.initData  // ← это важно для Menu-кнопки
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ответ от сервера:', data);
        displayResult(data);  // ← показываем результат в Mini App
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса:', error);
        // Вместо alert показываем ошибку прямо в Mini App
        if (typeof displayResult === 'function') {
            displayResult({ 
                status: 'error', 
                error: 'Не удалось связаться с сервером. Попробуйте позже.' 
            });
        }
    });
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
            flex-direction: column;
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
            text-align: center; /* Текст по центру */
            font-size: 2.2rem;
            color: white;
            text-shadow: 0 0 20px #8a6bff;
            margin: 30px 0 20px; /* Оставляем отступы как были */
            animation: titleFlicker 2s infinite;
            width: 100%; /* Чтобы занимал всю ширину */
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

// Функция для отображения результата в виде магических карт с каруселью
function displayResult(data) {
    const content = document.getElementById('content');
    if (!content) {
        console.error("Элемент #content не найден!");
        return;
    }

    if (!data || data.status !== 'success' || !data.interpretation) {
        showError(data?.error || 'Неизвестная ошибка');
        return;
    }

    const text = data.interpretation;
    
    // Сначала ищем общие секции (атмосфера, послание, совет, пожелание)
    const generalSections = [
        { emoji: '🔮', title: 'ОБЩАЯ АТМОСФЕРА', pattern: /🔮?\s*ОБЩАЯ\s*АТМОСФЕРА:?\s*([\s\S]*?)(?=📍|💡|🌟|✨|$)/i },
        { emoji: '💡', title: 'ГЛАВНОЕ ПОСЛАНИЕ', pattern: /💡?\s*ГЛАВНОЕ\s*ПОСЛАНИЕ:?\s*([\s\S]*?)(?=🌟|✨|$)/i },
        { emoji: '🌟', title: 'ПРАКТИЧЕСКИЙ СОВЕТ', pattern: /🌟?\s*ПРАКТИЧЕСКИЙ\s*СОВЕТ:?\s*([\s\S]*?)(?=✨|$)/i },
        { emoji: '✨', title: 'ПОЖЕЛАНИЕ', pattern: /✨?\s*ПОЖЕЛАНИЕ:?\s*([\s\S]*?)$/i }
    ];

    // Отдельно ищем блок с позициями
    const positionsBlock = text.match(/📍?\s*РАЗБОР\s*КАЖДОЙ\s*ПОЗИЦИИ:?\s*([\s\S]*?)(?=💡|🌟|✨|$)/i);
    
    let cardsHtml = '';
    let cardIndex = 0;

    // Функция создания карты
    function createCard(emoji, title, text, index) {
        const cleanText = text.replace(/\*\*/g, '<strong>')
                             .replace(/\*/g, '')
                             .replace(/\n/g, '<br>');
        
        return `
            <div class="magic-card" style="animation-delay: ${index * 0.1}s;" data-index="${index}">
                <div class="card-inner">
                    <div class="card-glow"></div>
                    <div class="card-header">
                        <span class="card-emoji">${emoji}</span>
                        <h3 class="card-title">${title}</h3>
                    </div>
                    <div class="card-content">
                        ${cleanText}
                    </div>
                    <div class="card-runes">ᛉ ᛟ ᚨ ᚷ ᚱ</div>
                </div>
            </div>
        `;
    }

    // Добавляем общие секции
    generalSections.forEach(section => {
        const match = text.match(section.pattern);
        if (match && match[1].trim()) {
            cardsHtml += createCard(section.emoji, section.title, match[1].trim(), cardIndex++);
        }
    });

    // Разбираем позиции на отдельные карты
    if (positionsBlock && positionsBlock[1]) {
        const positionsText = positionsBlock[1];
        // Разбиваем текст на отдельные позиции (по эмодзи или переносу строки)
        const positionMatches = positionsText.split(/\n(?=🎴|📍|🔹|🔸|\d+\.)/).filter(p => p.trim());
        
        positionMatches.forEach((posText, idx) => {
            // Пытаемся извлечь название позиции (то, что до двоеточия)
            const titleMatch = posText.match(/^[^:]+:/);
            const posTitle = titleMatch ? titleMatch[0].replace(':', '').trim() : `Позиция ${idx + 1}`;
            const cleanPosText = posText.replace(/^[^:]+:\s*/, '').trim();
            
            if (cleanPosText) {
                cardsHtml += createCard('📍', posTitle, cleanPosText, cardIndex++);
            }
        });
    }

    // Создаём индикаторы позиций
    let positionIndicators = '';
    for (let i = 0; i < cardIndex; i++) {
        positionIndicators += `<div class="position-dot ${i === 0 ? 'active' : ''}" data-pos="${i}"></div>`;
    }

    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title mystical-title">🔮 ВАШ МИСТИЧЕСКИЙ РАСКЛАД 🔮</h2>
            <div class="cards-deck mystical-deck">
                ${cardsHtml}
            </div>
            <div class="card-position-indicator">
                ${positionIndicators}
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 40px;">
                <span class="button-text">НОВОЕ ГАДАНИЕ</span>
                <span class="button-glow"></span>
            </button>
        </div>
    `;

    // Активируем карусель
    initCarousel();
    console.log("✅ Мистическая карусель создана");
}

// Функция для инициализации карусели
function initCarousel() {
    const deck = document.querySelector('.cards-deck');
    if (!deck) return;

    let startX, scrollLeft, isDown = false;

    deck.addEventListener('mousedown', (e) => {
        isDown = true;
        deck.classList.add('grabbing');
        startX = e.pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });

    deck.addEventListener('mouseleave', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });

    deck.addEventListener('mouseup', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });

    deck.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });

    deck.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 300 : -300;
        deck.scrollBy({
            left: delta,
            behavior: 'smooth'
        });
    }, { passive: false });

    deck.addEventListener('touchstart', (e) => {
        isDown = true;
        startX = e.touches[0].pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });

    deck.addEventListener('touchend', () => {
        isDown = false;
        const cardWidth = 340;
        const activeIndex = Math.round(deck.scrollLeft / cardWidth);
        deck.scrollTo({
            left: activeIndex * cardWidth,
            behavior: 'smooth'
        });
        updateActiveDot(activeIndex);
    });

    deck.addEventListener('touchmove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.touches[0].pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });

    deck.addEventListener('scroll', () => {
        const cardWidth = 340;
        const activeIndex = Math.round(deck.scrollLeft / cardWidth);
        updateActiveDot(activeIndex);
    });

    document.querySelectorAll('.position-dot').forEach(dot => {
        dot.addEventListener('click', () => {
            const pos = parseInt(dot.dataset.pos);
            const cardWidth = 340;
            deck.scrollTo({
                left: pos * cardWidth,
                behavior: 'smooth'
            });
            updateActiveDot(pos);
        });
    });

    function updateActiveDot(index) {
        document.querySelectorAll('.position-dot').forEach((dot, i) => {
            if (i === index) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
}

function showError(message) {
    const content = document.getElementById('content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title mystical-title">❌ ОШИБКА</h2>
            <div class="tarot-card error-card">
                <div class="card-inner">
                    <div class="card-content">
                        ${message}
                    </div>
                </div>
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 30px;">
                <span class="button-text">ПОПРОБОВАТЬ СНОВА</span>
            </button>
        </div>
    `;
}

// Слушаем события от Telegram
tg.onEvent('mainButtonClicked', function() {
    tg.close();
});

tg.onEvent('webAppData', function(data) {
    console.log('Получены данные:', data);
});

// Функция для инициализации карусели
function initCarousel() {
    const deck = document.querySelector('.cards-deck');
    if (!deck) return;

    // Данные для свайпов
    let startX, scrollLeft, isDown = false;

    // Обработчики для мыши (перетаскивание)
    deck.addEventListener('mousedown', (e) => {
        isDown = true;
        deck.classList.add('grabbing');
        startX = e.pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });

    deck.addEventListener('mouseleave', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });

    deck.addEventListener('mouseup', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });

    deck.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });

    // ⭐ НОВЫЙ ОБРАБОТЧИК: колесико мыши для ПК
    deck.addEventListener('wheel', (e) => {
        e.preventDefault(); // Отключаем вертикальную прокрутку страницы
        const delta = e.deltaY > 0 ? 300 : -300; // Скорость прокрутки
        deck.scrollBy({
            left: delta,
            behavior: 'smooth' // Плавная прокрутка
        });
    }, { passive: false }); // Важно! passive: false чтобы работал preventDefault

    // Обработчики для тач-устройств (мобильные)
    deck.addEventListener('touchstart', (e) => {
        isDown = true;
        startX = e.touches[0].pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });

    deck.addEventListener('touchend', () => {
        isDown = false;
        // Центрируем ближайшую карту после отпускания
        const cardWidth = 340;
        const activeIndex = Math.round(deck.scrollLeft / cardWidth);
        deck.scrollTo({
            left: activeIndex * cardWidth,
            behavior: 'smooth'
        });
        updateActiveDot(activeIndex);
    });

    deck.addEventListener('touchmove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.touches[0].pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });

    // Обновление активной точки при скролле
    deck.addEventListener('scroll', () => {
        const cardWidth = 340;
        const activeIndex = Math.round(deck.scrollLeft / cardWidth);
        updateActiveDot(activeIndex);
    });

    // Клик по точкам для перехода
    document.querySelectorAll('.position-dot').forEach(dot => {
        dot.addEventListener('click', () => {
            const pos = parseInt(dot.dataset.pos);
            const cardWidth = 340;
            deck.scrollTo({
                left: pos * cardWidth,
                behavior: 'smooth'
            });
            updateActiveDot(pos);
        });
    });

    // Функция обновления активной точки
    function updateActiveDot(index) {
        document.querySelectorAll('.position-dot').forEach((dot, i) => {
            if (i === index) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
}

// Функция для отображения результата в виде магических карт с каруселью
// Функция для отображения результата в виде магических карт с каруселью
function displayResult(data) {
    const content = document.getElementById('content');
    if (!content) {
        console.error("Элемент #content не найден!");
        return;
    }

    if (!data || data.status !== 'success' || !data.interpretation) {
        showError(data?.error || 'Неизвестная ошибка');
        return;
    }

    const text = data.interpretation;
    
    // Сначала ищем общие секции (атмосфера, послание, совет, пожелание)
    const generalSections = [
        { emoji: '🔮', title: 'ОБЩАЯ АТМОСФЕРА', pattern: /🔮?\s*ОБЩАЯ\s*АТМОСФЕРА:?\s*([\s\S]*?)(?=📍|💡|🌟|✨|$)/i },
        { emoji: '💡', title: 'ГЛАВНОЕ ПОСЛАНИЕ', pattern: /💡?\s*ГЛАВНОЕ\s*ПОСЛАНИЕ:?\s*([\s\S]*?)(?=🌟|✨|$)/i },
        { emoji: '🌟', title: 'ПРАКТИЧЕСКИЙ СОВЕТ', pattern: /🌟?\s*ПРАКТИЧЕСКИЙ\s*СОВЕТ:?\s*([\s\S]*?)(?=✨|$)/i },
        { emoji: '✨', title: 'ПОЖЕЛАНИЕ', pattern: /✨?\s*ПОЖЕЛАНИЕ:?\s*([\s\S]*?)$/i }
    ];

    // Отдельно ищем блок с позициями
    const positionsBlock = text.match(/📍?\s*РАЗБОР\s*КАЖДОЙ\s*ПОЗИЦИИ:?\s*([\s\S]*?)(?=💡|🌟|✨|$)/i);
    
    let cardsHtml = '';
    let cardIndex = 0;

    // Функция создания карты
    function createCard(emoji, title, text, index) {
        const cleanText = text.replace(/\*\*/g, '<strong>')
                             .replace(/\*/g, '')
                             .replace(/\n/g, '<br>');
        
        return `
            <div class="magic-card" style="animation-delay: ${index * 0.1}s;" data-index="${index}">
                <div class="card-inner">
                    <div class="card-glow"></div>
                    <div class="card-header">
                        <span class="card-emoji">${emoji}</span>
                        <h3 class="card-title">${title}</h3>
                    </div>
                    <div class="card-content">
                        ${cleanText}
                    </div>
                    <div class="card-runes">ᛉ ᛟ ᚨ ᚷ ᚱ</div>
                </div>
            </div>
        `;
    }

    // Добавляем общие секции
    generalSections.forEach(section => {
        const match = text.match(section.pattern);
        if (match && match[1].trim()) {
            cardsHtml += createCard(section.emoji, section.title, match[1].trim(), cardIndex++);
        }
    });

    // Разбираем позиции на отдельные карты
    if (positionsBlock && positionsBlock[1]) {
        const positionsText = positionsBlock[1];
        // Разбиваем текст на отдельные позиции (по эмодзи или переносу строки)
        const positionMatches = positionsText.split(/\n(?=🎴|📍|🔹|🔸|\d+\.)/).filter(p => p.trim());
        
        positionMatches.forEach((posText, idx) => {
            // Пытаемся извлечь название позиции (то, что до двоеточия)
            const titleMatch = posText.match(/^[^:]+:/);
            const posTitle = titleMatch ? titleMatch[0].replace(':', '').trim() : `Позиция ${idx + 1}`;
            const cleanPosText = posText.replace(/^[^:]+:\s*/, '').trim();
            
            if (cleanPosText) {
                cardsHtml += createCard('📍', posTitle, cleanPosText, cardIndex++);
            }
        });
    }

    // Создаём индикаторы позиций
    let positionIndicators = '';
    for (let i = 0; i < cardIndex; i++) {
        positionIndicators += `<div class="position-dot ${i === 0 ? 'active' : ''}" data-pos="${i}"></div>`;
    }

    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title mystical-title">🔮 ВАШ МИСТИЧЕСКИЙ РАСКЛАД 🔮</h2>
            <div class="cards-deck mystical-deck">
                ${cardsHtml}
            </div>
            <div class="card-position-indicator">
                ${positionIndicators}
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 40px;">
                <span class="button-text">НОВОЕ ГАДАНИЕ</span>
                <span class="button-glow"></span>
            </button>
        </div>
    `;

    // Активируем карусель
    initCarousel();
    console.log("✅ Мистическая карусель создана");
}

function showError(message) {
    const content = document.getElementById('content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title mystical-title">❌ ОШИБКА</h2>
            <div class="tarot-card error-card">
                <div class="card-inner">
                    <div class="card-content">
                        ${message}
                    </div>
                </div>
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 30px;">
                <span class="button-text">ПОПРОБОВАТЬ СНОВА</span>
            </button>
        </div>
    `;
}

// Добавляем поддержку свайпов для карт
function initSwipeNavigation() {
    const deck = document.querySelector('.cards-deck');
    if (!deck) return;
    
    let startX;
    let scrollLeft;
    let isDown = false;
    
    deck.addEventListener('mousedown', (e) => {
        isDown = true;
        deck.classList.add('grabbing');
        startX = e.pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });
    
    deck.addEventListener('mouseleave', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });
    
    deck.addEventListener('mouseup', () => {
        isDown = false;
        deck.classList.remove('grabbing');
    });
    
    deck.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });
    
    // Для мобильных
    deck.addEventListener('touchstart', (e) => {
        isDown = true;
        startX = e.touches[0].pageX - deck.offsetLeft;
        scrollLeft = deck.scrollLeft;
    });
    
    deck.addEventListener('touchend', () => {
        isDown = false;
    });
    
    deck.addEventListener('touchmove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.touches[0].pageX - deck.offsetLeft;
        const walk = (x - startX) * 2;
        deck.scrollLeft = scrollLeft - walk;
    });
}

// Вызываем после отображения карт
setTimeout(initSwipeNavigation, 500); // Ждём появления карт

function showError(message) {
    const content = document.getElementById('content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title">❌ ОШИБКА</h2>
            <div class="tarot-card error-card">
                <div class="card-content">
                    ${message}
                </div>
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 30px;">
                <span class="button-text">ПОПРОБОВАТЬ СНОВА</span>
            </button>
        </div>
    `;
    console.log("❌ Ошибка отображена в Mini App:", message);
}

function showError(message) {
    const content = document.getElementById('content');
    if (!content) return;
    
    content.innerHTML = `
        <div class="result-container">
            <h2 class="result-title">❌ ОШИБКА</h2>
            <div class="tarot-card error-card">
                <div class="card-content">
                    ${message}
                </div>
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 30px;">
                <span class="button-text">ПОПРОБОВАТЬ СНОВА</span>
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