const N = 6; // Количество сегментов
const circle = document.getElementById('circle');
const radius = 265; // Радиус окружности
const pages = document.querySelectorAll('.page');
const labels = ["Технологии", "Кино", "Литература", "Театр", "Спорт", "Наука"];
const centerText = document.getElementById('centerText');

// Инициализация счетчиков страниц
document.querySelectorAll('.page-counter').forEach((counter, index) => {
    counter.textContent = `${index + 1}/${N}`;
});

document.querySelectorAll('.mobile-page-counter').forEach((counter, index) => {
    counter.textContent = `${index + 1}/${N}`;
});

// Данные карточек для каждого слайда
const cardsData = [
    // Слайд 1
    [
        { title: "1980", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1982", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1984", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1986", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ],
    // Слайд 2
    [
        { title: "1987", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1988", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1987", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1990", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1991", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ],
    // Слайд 3
    [
        { title: "1992", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1994", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1995", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "1997", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ],
    // Слайд 4
    [
        { title: "1999", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2000", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2002", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2003", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2004", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ],
    // Слайд 5
    [
        { title: "2006", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2008", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2010", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2012", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2014", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ],
    // Слайд 6
    [
        { title: "2015", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2016", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2017", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2018", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2019", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2020", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2021", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
        { title: "2022", subtitle: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." }
    ]
];

let currentPage = 0;
let segments = [];
let currentRotation = 0;

// Инициализация кнопок скролла
function initScrollButtons() {
    document.querySelectorAll('.cards-container').forEach(container => {
        const scrollLeftBtn = container.parentElement.querySelector('.scroll-button.left');
        const scrollRightBtn = container.parentElement.querySelector('.scroll-button.right');
        
        container.addEventListener('scroll', () => {
            updateScrollButtonsVisibility(container, scrollLeftBtn, scrollRightBtn);
        });
        
        updateScrollButtonsVisibility(container, scrollLeftBtn, scrollRightBtn);
    });
}

// Обновление видимости кнопок скролла
function updateScrollButtonsVisibility(container, leftBtn, rightBtn) {
    const scrollLeft = container.scrollLeft;
    const maxScroll = container.scrollWidth - container.clientWidth;
    
    leftBtn.style.display = scrollLeft > 0 ? 'block' : 'none';
    rightBtn.style.display = scrollLeft < maxScroll - 1 ? 'block' : 'none';
}

// Скролл карточек
function scrollCards(direction) {
    const container = document.querySelector(`#cardsContainer${currentPage + 1}`);
    const cardWidth = 320 + 80; // Ширина карточки + отступ
    const scrollAmount = direction * cardWidth;
    
    container.scrollBy({
        left: scrollAmount,
        behavior: 'smooth'
    });
}

// Создаем сегменты со смещением на 30 градусов вправо
for (let i = 0; i < N; i++) {
    const segment = document.createElement('div');
    segment.className = 'segment' + (i === 0 ? ' active' : '');
    segment.dataset.index = i;
    
    const content = document.createElement('div');
    content.className = 'segment-content';
    
    const number = document.createElement('div');
    number.className = 'segment-number';
    number.textContent = i + 1;
    content.appendChild(number);
    
    const label = document.createElement('div');
    label.className = 'segment-label';
    label.textContent = labels[i];
    content.appendChild(label);
    
    segment.appendChild(content);
    
    // Начальный угол -90 градусов (слева) + 30 градусов смещения вправо
    const angle = (360 / N) * i - 90 + 30;
    const x = radius * Math.cos(angle * Math.PI / 180);
    const y = radius * Math.sin(angle * Math.PI / 180);
    segment.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
    
    segment.addEventListener('click', function() {
        const targetIndex = parseInt(this.dataset.index);
        if (targetIndex === currentPage) return;
        
        rotateCircle(targetIndex);
        switchPage(targetIndex);
    });
    
    circle.appendChild(segment);
    segments.push(segment);
}

function rotateCircle(targetIndex) {
    const diff = targetIndex - currentPage;
    let rotationAngle = 0;
    
    if (Math.abs(diff) > N / 2) {
        rotationAngle = (N - Math.abs(diff)) * (360 / N);
        rotationAngle *= diff > 0 ? 1 : -1;
    } else {
        rotationAngle = diff * (360 / N) * -1;
    }
    
    currentRotation += rotationAngle;
    circle.style.transform = `rotate(${currentRotation}deg)`;
    
    segments.forEach(segment => {
        const content = segment.querySelector('.segment-content');
        content.style.transform = `rotate(${-currentRotation}deg)`;
    });
}

async function switchPage(targetIndex) {
    // Анимация центрального текста
    animateCenterText(currentPage, targetIndex);
    
    // Скрываем мобильные элементы текущей страницы
    const currentMobilePage = pages[currentPage].querySelector('.main-mobile');
    if (currentMobilePage) {
        const elementsToHide = [
            currentMobilePage.querySelector('.mobile-category'),
            currentMobilePage.querySelector('.mobile-divider'),
            currentMobilePage.querySelector('.mobile-card-wrapper')
        ];
        
        elementsToHide.forEach(el => el?.classList.add('hidden'));
    }
    
    // Ждем завершения анимации исчезновения
    await new Promise(resolve => setTimeout(resolve, 500));
    
    pages[currentPage].classList.remove('active');
    segments[currentPage].classList.remove('active');
    
    updateNavButtons(currentPage, false);
    updateMobileNavButtons(currentPage, false);
    
    currentPage = targetIndex;
    
    pages[currentPage].classList.add('active');
    segments[currentPage].classList.add('active');
    
    updateNavButtons(currentPage, true);
    updateMobileNavButtons(currentPage, true);
    updateMobileContent(targetIndex);
    
    // Показываем мобильные элементы новой страницы
    const newMobilePage = pages[currentPage].querySelector('.main-mobile');
    if (newMobilePage) {
        const elementsToShow = [
            newMobilePage.querySelector('.mobile-category'),
            newMobilePage.querySelector('.mobile-divider'),
            newMobilePage.querySelector('.mobile-card-wrapper')
        ];
        
        // Сначала устанавливаем opacity: 0, затем удаляем hidden
        elementsToShow.forEach(el => {
            if (el) {
                el.style.opacity = '0';
                el.classList.remove('hidden');
                // Запускаем анимацию появления
                setTimeout(() => {
                    el.style.opacity = '1';
                }, 10);
            }
        });
    }
    
    // Сброс скролла для нового слайда
    const container = document.querySelector(`#cardsContainer${currentPage + 1}`);
    if (container) {
        container.scrollLeft = 0;
        const scrollLeftBtn = container.parentElement.querySelector('.scroll-button.left');
        const scrollRightBtn = container.parentElement.querySelector('.scroll-button.right');
        updateScrollButtonsVisibility(container, scrollLeftBtn, scrollRightBtn);
    }
    
    // Сброс скролла для мобильной версии
    const mobileContainer = document.querySelector(`#page${targetIndex + 1} .mobile-card-wrapper`);
    if (mobileContainer) {
        mobileContainer.scrollLeft = 0;
    }
}

function animateCenterText(fromIndex, toIndex) {
    const fromCards = cardsData[fromIndex];
    const toCards = cardsData[toIndex];
    
    const fromFirst = fromCards[0].title;
    const fromLast = fromCards[fromCards.length - 1].title;
    const toFirst = toCards[0].title;
    const toLast = toCards[toCards.length - 1].title;
    
    // Собираем все заголовки карточек между текущим и целевым слайдом
    let leftTitles = [];
    let rightTitles = [];
    
    if (fromIndex < toIndex) {
        // Переход вперед
        for (let i = fromIndex; i <= toIndex; i++) {
            const cards = cardsData[i];
            if (i === fromIndex) {
                // Для первого слайда берем все карточки от текущей первой до первой следующего слайда
                const startIdx = cards.findIndex(c => c.title === fromFirst);
                for (let j = startIdx; j < cards.length; j++) {
                    leftTitles.push(cards[j].title);
                }
            } else if (i === toIndex) {
                // Для последнего слайда берем все карточки до целевой первой
                const endIdx = cards.findIndex(c => c.title === toFirst);
                for (let j = 0; j <= endIdx; j++) {
                    leftTitles.push(cards[j].title);
                }
            } else {
                // Для промежуточных слайдов берем все карточки
                cards.forEach(card => {
                    leftTitles.push(card.title);
                });
            }
        }
        
        // Для правой части
        for (let i = fromIndex; i <= toIndex; i++) {
            const cards = cardsData[i];
            if (i === fromIndex) {
                // Для первого слайда берем все карточки от текущей последней до последней следующего слайда
                const startIdx = cards.findIndex(c => c.title === fromLast);
                for (let j = startIdx; j < cards.length; j++) {
                    rightTitles.push(cards[j].title);
                }
            } else if (i === toIndex) {
                // Для последнего слайда берем все карточки до целевой последней
                const endIdx = cards.findIndex(c => c.title === toLast);
                for (let j = 0; j <= endIdx; j++) {
                    rightTitles.push(cards[j].title);
                }
            } else {
                // Для промежуточных слайдов берем все карточки
                cards.forEach(card => {
                    rightTitles.push(card.title);
                });
            }
        }
    } else if (fromIndex > toIndex) {
        // Переход назад
        for (let i = fromIndex; i >= toIndex; i--) {
            const cards = cardsData[i];
            if (i === fromIndex) {
                // Для первого слайда берем все карточки от текущей первой до первой предыдущего слайда
                const startIdx = cards.findIndex(c => c.title === fromFirst);
                for (let j = startIdx; j >= 0; j--) {
                    leftTitles.push(cards[j].title);
                }
            } else if (i === toIndex) {
                // Для последнего слайда берем все карточки от последней до целевой первой
                const endIdx = cards.findIndex(c => c.title === toFirst);
                for (let j = cards.length - 1; j >= endIdx; j--) {
                    leftTitles.push(cards[j].title);
                }
            } else {
                // Для промежуточных слайдов берем все карточки в обратном порядке
                for (let j = cards.length - 1; j >= 0; j--) {
                    leftTitles.push(cards[j].title);
                }
            }
        }
        
        // Для правой части
        for (let i = fromIndex; i >= toIndex; i--) {
            const cards = cardsData[i];
            if (i === fromIndex) {
                // Для первого слайда берем все карточки от текущей последней до последней предыдущего слайда
                const startIdx = cards.findIndex(c => c.title === fromLast);
                for (let j = startIdx; j >= 0; j--) {
                    rightTitles.push(cards[j].title);
                }
            } else if (i === toIndex) {
                // Для последнего слайда берем все карточки от первой до целевой последней
                const endIdx = cards.findIndex(c => c.title === toLast);
                for (let j = cards.length - 1; j >= endIdx; j--) {
                    rightTitles.push(cards[j].title);
                }
            } else {
                // Для промежуточных слайдов берем все карточки в обратном порядке
                for (let j = cards.length - 1; j >= 0; j--) {
                    rightTitles.push(cards[j].title);
                }
            }
        }
    }
    
    // Анимация
    const duration = 1000; // 1 секунда
    const interval = 50; // обновляем каждые 50мс
    const steps = duration / interval;
    let step = 0;
    
    const animation = setInterval(() => {
        step++;
        
        // Вычисляем текущие индексы для левой и правой частей
        const leftProgress = Math.min(step / steps, 1);
        const rightProgress = Math.min(step / steps, 1);
        
        const leftIndex = Math.floor(leftProgress * (leftTitles.length - 1));
        const rightIndex = Math.floor(rightProgress * (rightTitles.length - 1));
        
        // Обновляем текст
        const leftSpan = centerText.querySelector('.left');
        const rightSpan = centerText.querySelector('.right');
        
        leftSpan.textContent = leftTitles[leftIndex] || toFirst;
        rightSpan.textContent = rightTitles[rightIndex] || toLast;
        
        // Обновляем мобильную версию
        const mobileLeftSpan = document.querySelector(`#page${toIndex + 1} .mobile-center-text .left`);
        const mobileRightSpan = document.querySelector(`#page${toIndex + 1} .mobile-center-text .right`);
        if (mobileLeftSpan && mobileRightSpan) {
            mobileLeftSpan.textContent = leftTitles[leftIndex] || toFirst;
            mobileRightSpan.textContent = rightTitles[rightIndex] || toLast;
        }
        
        if (step >= steps) {
            clearInterval(animation);
            // Устанавливаем финальные значения
            leftSpan.textContent = toFirst;
            rightSpan.textContent = toLast;
            if (mobileLeftSpan && mobileRightSpan) {
                mobileLeftSpan.textContent = toFirst;
                mobileRightSpan.textContent = toLast;
            }
        }
    }, interval);
}

function navigate(direction) {
    let targetIndex = currentPage + direction;
    
    if (targetIndex < 0) {
        targetIndex = N - 1;
    } else if (targetIndex >= N) {
        targetIndex = 0;
    }
    
    rotateCircle(targetIndex);
    switchPage(targetIndex);
}

function updateNavButtons(pageIndex, isActive) {
    const page = pages[pageIndex];
    if (!page) return;
    
    const prevButton = page.querySelector('.prev-button');
    const nextButton = page.querySelector('.next-button');
    
    if (pageIndex === 0) {
        prevButton.classList.add('disabled');
        prevButton.removeAttribute('onclick');
        nextButton.classList.remove('disabled');
        nextButton.setAttribute('onclick', 'navigate(1)');
    } else if (pageIndex === N - 1) {
        prevButton.classList.remove('disabled');
        prevButton.setAttribute('onclick', 'navigate(-1)');
        nextButton.classList.add('disabled');
        nextButton.removeAttribute('onclick');
    } else {
        prevButton.classList.remove('disabled');
        prevButton.setAttribute('onclick', 'navigate(-1)');
        nextButton.classList.remove('disabled');
        nextButton.setAttribute('onclick', 'navigate(1)');
    }
}

// Мобильная навигация
function mobileNavigate(direction) {
    let targetIndex = currentPage + direction;
    
    if (targetIndex < 0) {
        targetIndex = N - 1;
    } else if (targetIndex >= N) {
        targetIndex = 0;
    }
    
    switchPage(targetIndex);
}

function mobileGoToPage(pageIndex) {
    if (pageIndex === currentPage) return;
    switchPage(pageIndex);
}

// function updateMobilePagination(pageIndex, isActive) {
//     const dots = document.querySelectorAll('.mobile-pagination-dot');
//     dots.forEach((dot, index) => {
//         if (index === pageIndex) {
//             dot.classList.add('active');
//         } else {
//             dot.classList.remove('active');
//         }
//     });
// }

function updateMobileNavButtons(pageIndex, isActive) {
    const prevButtons = document.querySelectorAll('.mobile-prev-button');
    const nextButtons = document.querySelectorAll('.mobile-next-button');
    
    prevButtons.forEach(button => {
        if (pageIndex === 0) {
            button.classList.add('disabled');
        } else {
            button.classList.remove('disabled');
        }
    });
    
    nextButtons.forEach(button => {
        if (pageIndex === N - 1) {
            button.classList.add('disabled');
        } else {
            button.classList.remove('disabled');
        }
    });
}

function updateMobileContent(pageIndex) {
    const page = pages[pageIndex];
    if (!page) return;
    
    const category = page.querySelector('.mobile-category');
    if (category) {
        category.textContent = labels[pageIndex];
    }
    
    const counter = page.querySelector('.mobile-page-counter');
    if (counter) {
        counter.textContent = `${pageIndex + 1}/${N}`;
    }
}

// Инициализация
updateNavButtons(0, true);
// updateMobilePagination(0, true);
updateMobileNavButtons(0, true);
initScrollButtons();