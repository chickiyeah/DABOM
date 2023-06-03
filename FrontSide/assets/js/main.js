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

/*window.addEventListener('scroll', (e) => { 
    console.log(window.scrollX, window.scrollY);
});*/

window.addEventListener('wheel', (e) => { 
    //console.log(e.deltaX, e.deltaY, "delta");
    if (e.deltaY > 0) {
        header.classList.add('active');
    } else {
        header.classList.remove('active');
    }
});

/*window.scroll(function(event){
    didScroll = true;
    console.log(window.pageYOffset)
});*/

function scrollEvent() {

    setInterval(function() {
        if (didScroll) {
            hasScrolled();
            didScroll = false;
        }
    }, 250); // 스크롤이 멈춘 후 동작이 실행되기 까지의 딜레이

    function hasScrolled() {
        let st = this.scrollTop(); // 현재 window의 scrollTop 값

        // delta로 설정한 값보다 많이 스크롤 되어야 실행된다.
        if(Math.abs(lastScrollTop - st) <= delta)
            return;

        if (st > lastScrollTop && st > navbarHeight){
            // 스크롤을 내렸을 때
            header.classList.add('active');
        } else {
            // 스크롤을 올렸을 때
            if(st + window.height() < document.height()) {
                header.classList.remove('active');
            }
        }

        lastScrollTop = st; // 현재 멈춘 위치를 기준점으로 재설정
    }
}

scrollEvent();