const carousel = document.querySelector('.carousel');
const slides = carousel.querySelector('.slides');
const slideWidth = carousel.offsetWidth;

let position = 0;

carousel.addEventListener('mousedown', dragStart);
carousel.addEventListener('touchstart', dragStart);

carousel.addEventListener('mouseup', dragEnd);
carousel.addEventListener('touchend', dragEnd);

carousel.addEventListener('mousemove', dragMove);
carousel.addEventListener('touchmove', dragMove);

function dragStart(event) {
  if (event.type === 'touchstart') {
    position = event.touches[0].clientX;
  } else {
    position = event.clientX;
    event.preventDefault();
  }
}

function dragMove(event) {
  const currentPosition = event.type === 'touchmove' ? event.touches[0].clientX : event.clientX;
  const diff = currentPosition - position;
  slides.style.transform = `translateX(${diff}px)`;
}

function dragEnd(event) {
  const currentPosition = event.type === 'touchend' ? event.changedTouches[0].clientX : event.clientX;
  const diff = currentPosition - position;

  if (diff > slideWidth / 4) {
    position += slideWidth;
  } else if (diff < -slideWidth / 4) {
    position -= slideWidth;
  }

  slides.style.transform = `translateX(${position}px)`;
}
