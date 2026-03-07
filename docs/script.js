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
            initData: window.Telegram.WebApp.initData
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ответ от сервера:', data);
        displayResult(data);
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса:', error);
        showError('Не удалось связаться с сервером. Попробуйте позже.');
    });
}

// Функция показа загрузки
function showLoading() {
    const content = document.getElementById('content');
    if (!content) return;
    // ... (твой существующий код showLoading, он правильный, его можно оставить)
    // Чтобы не загромождать ответ, я его пропускаю, но ты его сохрани.
    console.log("Показываю загрузку...");
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
        const positionMatches = positionsText.split(/\n(?=🎴|📍|🔹|🔸|\d+\.)/).filter(p => p.trim());

        positionMatches.forEach((posText, idx) => {
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
        deck.scrollBy({ left: delta, behavior: 'smooth' });
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
        deck.scrollTo({ left: activeIndex * cardWidth, behavior: 'smooth' });
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
            deck.scrollTo({ left: pos * cardWidth, behavior: 'smooth' });
            updateActiveDot(pos);
        });
    });

    function updateActiveDot(index) {
        document.querySelectorAll('.position-dot').forEach((dot, i) => {
            if (i === index) dot.classList.add('active');
            else dot.classList.remove('active');
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
                    <div class="card-content">${message}</div>
                </div>
            </div>
            <button class="magic-button" onclick="window.location.reload()" style="margin-top: 30px;">
                <span class="button-text">ПОПРОБОВАТЬ СНОВА</span>
            </button>
        </div>
    `;
}

// Слушаем события от Telegram
tg.onEvent('mainButtonClicked', () => tg.close());
tg.onEvent('webAppData', (data) => console.log('Получены данные:', data));