const menuToggle = document.getElementById('menuToggle');
const sideMenu = document.getElementById('sideMenu');
const closeMenu = document.getElementById('closeMenu');
const overlay = document.getElementById('overlay');
const mainContent = document.getElementById('mainContent');
const menuItems = document.querySelectorAll('.menu-item');

// Функция открытия меню
function openMenu() {
    sideMenu.classList.add('active');
    overlay.classList.add('active');
    mainContent.classList.add('shifted');
    document.body.style.overflow = 'hidden'; // Блокируем скролл
}

// Функция закрытия меню
function closeMenuFunc() {
    sideMenu.classList.remove('active');
    overlay.classList.remove('active');
    mainContent.classList.remove('shifted');
    document.body.style.overflow = 'auto'; // Разблокируем скролл
}

// Обработчики событий
menuToggle.addEventListener('click', openMenu);
closeMenu.addEventListener('click', closeMenuFunc);
overlay.addEventListener('click', closeMenuFunc);

// Закрытие меню при клике на пункт меню
menuItems.forEach(item => {
    item.addEventListener('click', function(e) {
        // Удаляем активный класс у всех пунктов
        menuItems.forEach(i => i.classList.remove('active'));
        // Добавляем активный класс текущему пункту
        this.classList.add('active');

        // Закрываем меню на мобильных устройствах
        if (window.innerWidth <= 768) {
            setTimeout(closeMenuFunc, 300);
        }
    });
});

// Закрытие меню при нажатии Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeMenuFunc();
    }
});

// Адаптивное поведение
window.addEventListener('resize', function() {
    if (window.innerWidth > 768 && sideMenu.classList.contains('active')) {
        // На десктопе не блокируем скролл
        document.body.style.overflow = 'auto';
    } else if (window.innerWidth <= 768 && sideMenu.classList.contains('active')) {
        // На мобильных блокируем скролл при открытом меню
        document.body.style.overflow = 'hidden';
    }
});

// Инициализация - первый пункт меню активный по умолчанию
if (menuItems.length > 0) {
    menuItems[0].classList.add('active');
}

// Плавная прокрутка для якорных ссылок (если будут)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId !== '#') {
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                closeMenuFunc();
            }
        }
    });
});

// Анимация появления меню при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Небольшая задержка для плавного появления
    setTimeout(() => {
        menuToggle.style.opacity = '1';
        menuToggle.style.transform = 'translateY(0)';
    }, 300);

    // Инициализация кнопки
    menuToggle.style.opacity = '0';
    menuToggle.style.transform = 'translateY(-20px)';
    menuToggle.style.transition = 'opacity 0.5s, transform 0.5s';
});