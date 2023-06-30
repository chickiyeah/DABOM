
const recordSlide = new Swiper(".record_slide", {
    direction: "horizontal",
    slidesPerGroup : 1,
    slidesPerView: "3",
    spaceBetween: 20,
    loop: false,
    pagination: {
        el: ".swiper-pagination",
        type: "fraction",
    },
    lazy : {
        loadPrevNext : true
    },
});