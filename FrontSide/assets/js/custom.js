const searchCall = document.querySelector('.search_call');
const searchBar = document.querySelector(".search_bar");
const headerBox = document.querySelector(".header_box");

const imgCall = document.querySelector(".img_call");
const imgMoreBox = document.querySelector(".img_more_box");
const goback1 = document.querySelector(".goback1")
const goback_image = document.querySelector(".goback_image")


searchCall.addEventListener('click', e => {
    e.preventDefault();
    headerBox.classList.toggle("on");
    searchBar.classList.toggle("on");
});

goback1.addEventListener('click', e => {
    e.preventDefault();
    headerBox.classList.toggle("on");
    searchBar.classList.toggle("on");
});


imgCall.addEventListener('click', e => {
    e.preventDefault();
    imgMoreBox.classList.toggle("on");
});

goback_image.addEventListener('click', e => {
    e.preventDefault();
    imgMoreBox.classList.toggle("on");
});    