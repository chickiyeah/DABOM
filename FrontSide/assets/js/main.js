// 메인페이지 모바일 햄버거 메뉴
const mHeader = document.querySelector(".mobile_header");
const hamburger = document.querySelector(".hamburger");

hamburger.addEventListener('click', e => {
    e.preventDefault();
    hamburger.classList.toggle("on");
    mHeader.classList.toggle("on");
});

// 브라우저 리사이즈 시
window.addEventListener("resize", e => {
    let wid = window.innerWidth;
    // console.log(wid);
    if(wid >= 800) mHeader.classList.remove("on");
    if(wid >= 800) hamburger.classList.remove("on");
});

// pc 해더 
const header = document.querySelector('header .pc_header');

let didScroll;
let lastScrollTop = 0;
let delta = 5; // 이벤트를 발생시킬 스크롤의 이동 범위
let navbarHeight = header.offsetHeight;

// pc 해더
window.addEventListener('wheel', (e) => { 
    //console.log(e.deltaX, e.deltaY, "delta");
    if (e.deltaY > 0) {
        header.classList.add('active');
        
    } else {
        header.classList.remove('active');
    }
});
