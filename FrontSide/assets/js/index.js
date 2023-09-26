document.addEventListener("DOMContentLoaded", (e) => {
    get_post()
    get_pola()


    document.querySelector(".search_i").addEventListener("keydown", (e) => {
        if (e.code === "Enter") {
            let input = document.querySelector(".search_i")
            if (input.value.trim() === "") {
                alert("공백은 검색할 수 없습니다.")
            } else {
                window.open(`diary_kcal?keyword=${input.value}`)
            }
        }

    })
})



function get_post() {
    fetch("/api/diary/all", {
        method: "POST",
        body: JSON.stringify({
            "page": 1
        })
    }).then((response) => {
        if (response.status === 200) {
            response.json().then((data) => {
                console.log(data);
                if (data.posts.length > 0) {
                    let swiper = document.querySelector(".swiper-wrapper")
                    swiper.innerHTML = ""
                    let to_html = ""
                    data.posts.forEach((post) => {
                        console.log(post);
                        let images = JSON.parse(post.images.replace(/'/g, '"'))
                        if (images.length > 0) {
                            let html = `<div class="swiper-slide">
                                            <a onclick="window.open('record_my?id=${post.no}')" href="javascript:">
                                                <div class="img_box">
                                                    <img alt="식단이미지" src="${images[0]}">
                                                </div>
                                                <div class="buttom_box">
                                                    <div class="pattern">
                                                        <object aria-label="지그재그 이미지" data="/assets/images/zigzag-05.svg"
                                                                type="image/svg+xml"></object>
                                                    </div>
                                                    <div class="txt">more</div>
                                                </div>
                                            </a>
                                        </div>`

                            to_html = to_html + html
                        }
                    })

                    swiper.insertAdjacentHTML("beforeend", to_html)
                }
            })
        }

        if (response.status === 422) {
            //로그인 안된상황
        }
    })
}

function get_pola() {
    fetch("/api/diary/pola", {
        method: "GET"
    }).then((response) => {
        if (response.status === 200) {
            response.json().then((data) => {
                let post = data.post[0]
                let images = JSON.parse(post.images.replace(/'/g, '"'))
                let html = `<a class="diary_box" onclick="window.open('record_my?id=${post.no}')" href="javascript:">
                                <div class="img_box">
                                    <img src="${images[0]}" alt="식단이미지">
                                </div>
                                <p class="txt">${post.desc}</p>
                            </a>`

                let h_pola = document.getElementById("pola")
                h_pola.innerHTML = ""
                h_pola.insertAdjacentHTML('beforeend', html)
            })
        }
    })
}