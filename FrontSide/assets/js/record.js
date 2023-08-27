document.addEventListener("DOMContentLoaded", (e) => {
    const monthdiv  = document.querySelector('.month_item');
    const sel_year = document.querySelector("body > main > div > div > div.year_box > input")

    var date = new Date();
    var year = date.getFullYear();
    var month = (1 + date.getMonth());
    monthdiv.querySelector(`#m_${lastselmonth}`).classList.remove('on');
    monthdiv.querySelector(`#m_${month}`).classList.add('on');
    lastselmonth = month

    //get_alone_posts(year, month, 1);
    Array.prototype.forEach.call(monthdiv.children, (child) => {
        child.addEventListener("click", (e) => {e.preventDefault();sel_month(monthdiv,child.id)});
    })

    const tab_menu = document.querySelector(".tab_menu").children
    const my_post = tab_menu[0];
    const our_post = tab_menu[1];
    const alone_ul = document.querySelector(".my_record");
    const our_ul = document.querySelector(".our_record");

    our_ul.style.display="none"

    my_post.addEventListener("click", (e) => {
        my_post.classList.add('on');
        our_post.classList.remove('on');
        alone_ul.style.display=""
        our_ul.style.display="none"
        alone_ul.innerHTML = "";
        get_alone_posts(last_year, lastselmonth, 1);
    })

    our_post.addEventListener("click", (e) => {
        our_post.classList.add('on');
        my_post.classList.remove('on');
        our_ul.style.display=""
        alone_ul.style.display="none"
        our_ul.innerHTML = "";
        get_with_posts(last_year, lastselmonth, 1);
    })
})

function sel_year(year) {
    last_year = year;
    const alone_ul = document.querySelector(".my_record");

    if (alone_ul.style.display == "none") {
        get_with_posts(year, lastselmonth, 1);
    } else {
        get_alone_posts(year, lastselmonth, 1);
    }
}

/** 월을 선택하는 함수
 * (월div, 월id( m_월 ))
 */
function sel_month(monthdiv, id) {
    let id_s = parseInt(id.replace("m_",""))

    monthdiv.querySelector(`#m_${lastselmonth}`).classList.remove('on');
    monthdiv.querySelector(`#m_${id_s}`).classList.add('on');
    lastselmonth = id_s

    const alone_ul = document.querySelector(".my_record");

    if (alone_ul.style.display == "none") {
        get_with_posts(last_year, id_s, 1);
    } else {
        get_alone_posts(last_year, id_s, 1);
    }
}

/** 내 기록의 게시글을 불러오는 함수
 * (년:int, 월:int, 페이지:int)
 */
function get_alone_posts(year, month, page) {
    if (page <= 0) {
        page = 1;
    }

    fetch("/api/diary/alone", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
            year: year,
            month: month,
            page: page
        })
    }).then((e) => {
        e.json().then((json) => {
            var to_html = "";
            let posts = json.posts
            let amount = json.total
                let pagediv = document.querySelector("#page_div")
                let to_page = amount / 7
                var maxpage
                if (Number.isInteger(to_page)) {
                    maxpage = to_page
                } else {
                    maxpage = Math.floor(to_page) + 1
                }

                console.log(page)
                console.log(maxpage)
                var startpage
                var endpage
                if (page / 10 > 1) {
                    startpage = Math.floor((page/10))*10
                    endpage = Math.floor((page/10))*10 + 1 + 10
                }else{
                    startpage = 1
                    endpage = 11
                }
                if (page - 1 >= 1) {
                    document.querySelector(".prev").addEventListener("click", (e) => {e.preventDefault;get_write(g_id,parseInt(page)-1);})
                }
                
                if ( page + 1 <= maxpage ) {
                    document.querySelector(".next").addEventListener("click", (e) => {e.preventDefault;get_write(g_id,parseInt(page)+1);})
                }

                pagediv.innerHTML = "";
                if (amount === 0) {
                    pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:">1</a>`)
                }else{
                    if (page > maxpage) {
                        //비정상 접근 시도 새로고침
                        location.reload();
                    }else if (page < 1) {
                        //비정상 접근 시도 새로고침
                        location.reload();
                    } else {  
                        let pg_html = ""                   
                        for (let i = startpage; i < maxpage+1; i++) {
                            if (i == page) {
                                pg_html = pg_html + `<a class="selected" id=${i} href="javascript:">${i}</a>`
                            }else{
                                pg_html = pg_html + `<a class="num" id=${i} href="javascript:">${i}</a>`
                            }
                        }

                        pagediv.insertAdjacentHTML("beforeend", pg_html);

                        Array.prototype.forEach.call(pagediv.children,(element) => {
                            element.addEventListener("click", (e) => {e.preventDefault;get_write(g_id,element.id);})
                        })
                         
                    }
                }
            posts.forEach((post) => {
                console.log(post)

                var eat_when = "";
                if (post.eat_when == "morning") {
                    eat_when = "아침"
                } else if (post.eat_when == "lunch") {
                    eat_when = "점심"
                } else if (post.eat_when == "night") {
                    eat_when = "저녁"
                } else if (post.eat_when == "free") {
                    eat_when = "간식"
                }

                let images = JSON.parse(post.images.replace(/'/g, '"'));

                console.log(images)

                let image = "/assets/images/default-background.png"

                if (images.length > 0) {
                    image = images[0]
                }

                let html = `
                    <li id='p_${post.no}'>
                        <div class="img_box" href="javascript:">
                            <img alt="식단 이미지" src="${image}">
                        </div>
                        <div class="info_box">
                            <h2>${post.title}</h2>
                            <p class="date">05/03</p>
                            <p class="txt_info">${post.desc}</p>
                            <div class="bottom">
                                <div class="txt">
                                    <span class="y_txt">${eat_when}</span>
                                    <span class="kcal">${parseInt(post.total_kcal).toLocaleString("ko-KR")} kcal</span>
                                </div>
                                <div class="checkbox">
                                    <input id="p_a_${post.no}" type="checkbox">
                                    <label for="p_a_${post.no}">체크하기</label>
                                </div>
                            </div>
                        </div>
                    </li>`
                
                to_html = to_html + html

            })

            const alone_ul = document.querySelector(".my_record")
            alone_ul.insertAdjacentHTML('beforeend', to_html)
        })
    })
}

/** 우리 기록의 게시글을 불러오는 함수
 * (년:int, 월:int, 페이지:int)
 */
function get_with_posts(year, month, page) {
    if (page <= 0) {
        page = 1;
    }

    fetch("/api/diary/with", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
            year: year,
            month: month,
            page: page
        })
    }).then((e) => {
        e.json().then((json) => {
            let posts = json.posts
            let amount = json.total
                let pagediv = document.querySelector("#page_div")
                let to_page = amount / 7
                var maxpage
                if (Number.isInteger(to_page)) {
                    maxpage = to_page
                } else {
                    maxpage = Math.floor(to_page) + 1
                }

                console.log(page)
                console.log(maxpage)
                var startpage
                var endpage
                if (page / 10 > 1) {
                    startpage = Math.floor((page/10))*10
                    endpage = Math.floor((page/10))*10 + 1 + 10
                }else{
                    startpage = 1
                    endpage = 11
                }
                if (page - 1 >= 1) {
                    document.querySelector(".prev").addEventListener("click", (e) => {e.preventDefault;get_write(g_id,parseInt(page)-1);})
                }
                
                if ( page + 1 <= maxpage ) {
                    document.querySelector(".next").addEventListener("click", (e) => {e.preventDefault;get_write(g_id,parseInt(page)+1);})
                }

                pagediv.innerHTML = "";
                if (amount === 0) {
                    pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:">1</a>`)
                }else{
                    if (page > maxpage) {
                        //비정상 접근 시도 새로고침
                        location.reload();
                    }else if (page < 1) {
                        //비정상 접근 시도 새로고침
                        location.reload();
                    } else {  
                        let pg_html = ""                   
                        for (let i = startpage; i < maxpage+1; i++) {
                            if (i == page) {
                                pg_html = pg_html + `<a class="selected" id=${i} href="javascript:">${i}</a>`
                            }else{
                                pg_html = pg_html + `<a class="num" id=${i} href="javascript:">${i}</a>`
                            }
                        }

                        pagediv.insertAdjacentHTML("beforeend", pg_html);

                        Array.prototype.forEach.call(pagediv.children,(element) => {
                            element.addEventListener("click", (e) => {e.preventDefault;get_write(g_id,element.id);})
                        })
                         
                    }
                }
            posts.forEach((post) => {
                var eat_with = "";
                if (post.with == "friend") {
                    eat_with = "친구와"
                } else if (post.with == "couple") {
                    eat_with = "연인과"
                }
                var f_html = "";
                let friends = JSON.parse(post.friends.replace(/'/g, '"'));
                let f_i = 0
                const our_ul = document.querySelector(".our_record");
                let images = JSON.parse(post.images.replace(/'/g, '"'));

                console.log(images)

                let image = "/assets/images/default-background.png"

                if (images.length > 0) {
                    image = images[0]
                }
                    friends.forEach(async (friend) => {
                        friend = await get_user_info(friend)
                        f_html = f_html + `<span class="r_txt">${friend.Nickname}</span>`
                        f_i++

                        if (f_i == friends.length) {
                            let html = `<li id='p_${post.no}'>
                            <a class="img_box" href="javascript:">
                                <img alt="식단 이미지" src="${image}">
                            </a>
                            <div class="info_box">
                                <h2>${post.title}</h2>
                                <p class="date">05/03</p>
                                <p class="txt_info">오늘은 피그마로 디자인을 너무 열심히 한 탓에 허기가지고
                                    머리가 안돌아가서 타코야끼랑 딸기바나를 먹었지 당떨어지면 달달한게 최고야</p>
                                <div class="bottom">
                                    <div class="txt">
                                        <span class="y_txt">${eat_with}</span>
                                        ${f_html}
                                    </div>
                                    <div class="right_box">
                                        <a class="comment" href="javascript:">
                                            <i class="comment_icon"><img alt="댓글아이콘" src="/assets/images/comment-icon.svg"></i>
                                            댓글 <em>0</em>개
                                        </a>
                                        <div class="checkbox">
                                            <input id="p_w_${post.no}" type="checkbox">
                                            <label for="p_w_${post.no}">체크하기</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </li>`
        
                        our_ul.insertAdjacentHTML("beforeend", html) 
                        }
                    })


            })
        })
    })
}

/** 유저의 세부정보를 가져오는암수
 * @promise (유저의 아이디)
 */
async function get_user_info(user) {
    return new Promise((resolve, reject) => {
        let url = `/api/user/get_user?id=${user}`
        fetch(url, {
            headers: {
                Authorization: "Bearer cncztSAt9m4JYA9"
            }
        }).then((res) => {
            if (res.status != 200) {
                reject("오류.")
            }else{
                res.json().then(async (json) => {
                    let u_data = json[0]
                    resolve(u_data)
                })
            }
        })
    })
}

/*function getToday(){
    const h_week = document.querySelector(".date");
    const week = ['일', '월', '화', '수', '목', '금', '토']
    var date = new Date();
    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);
  
    h_week.innerText = year + "년 " + month + "월 " + day +"일 " + week[date.getDay()]+"요일";
}*/