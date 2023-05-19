// 모바일
const hamburger = document.querySelector(".hamburger");
const mNav = document.querySelector(".m_nav");

hamburger.addEventListener('click', e => {
    e.preventDefault();
    hamburger.classList.toggle("on");
    mNav.classList.toggle("on");
});
