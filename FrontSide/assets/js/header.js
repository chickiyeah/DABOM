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
    if (getSize("Height") < document.documentElement.scrollHeight) {
        if (e.deltaY > 0) {
            header.classList.add('active');

        } else {
            header.classList.remove('active');
        }
    }
});





var getSize = function (Name) {
	var size;
	var name = Name.toLowerCase();
	var document = window.document;
	var documentElement = document.documentElement;
	if (window["inner" + Name] === undefined) {
		// IE6 & IE7 don't have window.innerWidth or innerHeight
		size = documentElement["client" + Name];
	} else if (window["inner" + Name] != documentElement["client" + Name]) {
		// WebKit doesn't include scrollbars while calculating viewport size so we have to get fancy

		// Insert markup to test if a media query will match document.doumentElement["client" + Name]
		var bodyElement = document.createElement("body");
		bodyElement.id = "vpw-test-b";
		bodyElement.style.cssText = "overflow:scroll";
		var divElement = document.createElement("div");
		divElement.id = "vpw-test-d";
		divElement.style.cssText = "position:absolute;top:-1000px";
		// Getting specific on the CSS selector so it won't get overridden easily
		divElement.innerHTML = "";
		bodyElement.appendChild(divElement);
		documentElement.insertBefore(bodyElement, document.head);

		if (divElement["offset" + Name] == 7) {
			// Media query matches document.documentElement["client" + Name]
			size = documentElement["client" + Name];
		} else {
			// Media query didn't match, use window["inner" + Name]
			size = window["inner" + Name];
		}
		// Cleanup
		documentElement.removeChild(bodyElement);
	} else {
		// Default to use window["inner" + Name]
		size = window["inner" + Name];
	}
	return size;
};
/*window.addEventListener("resize", function() {
    result.innerText = resizeDom.getBoundingClientRect().height;
})*/
