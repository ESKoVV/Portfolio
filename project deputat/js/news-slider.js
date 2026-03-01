/**
 * Слайдер новостей
 */
class NewsSlider {
  constructor() {
    this.slider = document.querySelector('.news__cards');
    this.cards = document.querySelectorAll('.news__card');
    this.prevBtn = document.querySelector('.news__prev');
    this.nextBtn = document.querySelector('.news__next');
    this.currentIndex = 0;

    this.init();
  }

  init() {
    this.prevBtn.addEventListener('click', () => this.slide(-1));
    this.nextBtn.addEventListener('click', () => this.slide(1));
  }

  slide(direction) {
    this.currentIndex += direction;
    if (this.currentIndex < 0) this.currentIndex = 0;
    if (this.currentIndex >= this.cards.length) this.currentIndex = this.cards.length - 1;
    
    this.slider.style.transform = `translateX(-${this.currentIndex * 400}px)`;
  }
}

new NewsSlider();