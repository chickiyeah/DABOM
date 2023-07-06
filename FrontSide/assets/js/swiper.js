if (location.href.includes("/record_my")) {
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
}

const storySlide = new Swiper(".story_slide", {
    slidesPerView: 'auto',
    rewind: true,
    loopAdditionalSlides: 1,
    speed: 500,
    navigation: {
        nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev",
    }, lazy: {
        loadPrevNext: true
    },
});