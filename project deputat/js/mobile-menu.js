/**
 * Мобильное меню
 */
document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const menu = document.querySelector('.mobile-menu');

  menuBtn.addEventListener('click', () => {
    menu.classList.toggle('active');
  });
});