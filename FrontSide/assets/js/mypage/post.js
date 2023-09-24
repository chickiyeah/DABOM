window.addEventListener('DOMContentLoaded', async function() {
    get_all_posts(1);
})

/** 내가 작성한 전체 게시글을 불러오는 함수
 * (년:int, 월:int, 페이지:int)
 */
function get_all_posts(page) {
    curpage = page
    if (page <= 0) {
        page = 1;
    }

    fetch("/api/diary/all", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({
            page: page
        })
    }).then((e) => {
        if (e.status === 404) {
            const post_ul = document.querySelector(".post_ul")
            post_ul.innerHTML = ""
            post_ul.insertAdjacentHTML("beforeend","<span style='margin: auto;'>글이 존재 하지 않습니다! 하나 작성해보세요!</span>") 
        } else if (e.status === 422) {
            location.href = "/login"
        } else {  
            const post_ul = document.querySelector(".post_ul")
            post_ul.innerHTML = ""
            e.json().then((json) => {    
                var to_html = "";
                let posts = json.posts
                let amount = json.total
                    let pagediv = document.querySelector("#page_div")
                    let to_page = amount / 6
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
                        document.querySelector(".prev").addEventListener("click", (e) => {e.preventDefault;get_alone_posts(last_year, lastselmonth ,parseInt(page)-1);})
                    }

                    if ( page + 1 <= maxpage ) {
                        document.querySelector(".next").addEventListener("click", (e) => {e.preventDefault;get_alone_posts(last_year, lastselmonth ,parseInt(page)+1);})
                    }

                    pagediv.innerHTML = "";
                    if (amount === 0) {
                        pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:">1</a>`)
                    }else{
                        if (page > maxpage) {ㄹ
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
                                element.addEventListener("click", (e) => {e.preventDefault;get_all_posts(element.id);})
                            })
                            
                        }
                    }
                posts.forEach((post) => {
                    //console.log(post)

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

                    //console.log(images)

                    let image = "/assets/images/default-background.png"

                    if (images.length > 0) {
                        image = images[0]
                    }
                    let p_date = new Date(post.created_at)
                    let p_year =  p_date.getFullYear()
                    let p_month = p_date.getMonth()+1
                    let p_day = p_date.getDate()
                    if (p_month.toString().length === 1) {
                        p_month = "0"+p_month.toString()
                    }

                    if (p_day.toString().length === 1) {
                        p_day = "0"+p_day.toString()
                    }

                    let html = `<li id='p_${post.no}'>
                        <div class="checkbox">
                            <input name="post" onclick="select_post(this)" id="p_a_${post.no}" type="checkbox">
                            <label for="p_a_${post.no}">체크박스</label>
                        </div>
                        <span class="kcal">${parseInt(post.total_kcal).toLocaleString("ko-KR")} Kcal</span>
                        <a href="javascript:">
                            <img src="${image}" alt="게시글 이미지">
                        </a>
                        <div class="info_box">
                            <p onclick='window.open(\"record_my?id=${post.no}\")' style="cursor:pointer" class="title">${p_year}-${p_month}-${p_day}</p>
                            <p class="sub_txt">${post.desc}</p>
                        </div>
                    </li>`
                    
                    to_html = to_html + html

                })

                const post_ul = document.querySelector(".post_ul")
                post_ul.insertAdjacentHTML('beforeend', to_html)
            })
        }
    })
}

/** 선택한 게시글을 공유하는 함수 */
function share_post() {
    if (checked.length == 0) {
        alert("공유할 게시글을 선택해주세요!")
    } else {
        if (checked.length == 1) {
            let ids = [] 
            checked.forEach((val) => {
                ids.push(parseInt(val.replace("p_a_", "")))
            })
            fetch(`/api/diary/${ids[0]}/share`, {
                method: 'POST'
            }).then((response) => {
                if (response.status === 200) {
                    let l_input = document.getElementById("s_link")
                    response.json().then((data) => {
                        console.log(data)
                        l_input.value = data
                    })
                }
            })
        } else {
            alert("공유는 한번에 하나만 할 수 있습니다.")
        }
    }
}

/** 선택한 게시글을 삭제하는 함수 */
function delete_post() {
    if (checked.length == 0) {
        alert("삭제할 게시글을 선택해주세요!")
    } else {
        let del_con = confirm("정말 "+checked.length+"개의 게시글을 삭제하시겠습니까?")

        if (del_con) {
            let ids = []
            checked.forEach((val) => {
                ids.push(parseInt(val.replace("p_a_", "")))
            })

            console.log(ids)
            fetch("/api/diary/delete", {
                method: "DELETE",
                credentials: "include",
                body: JSON.stringify({
                    post_ids : ids
                })
            }).then((response) => {
                if (response.status === 200) {
                    location.reload()
                }
            })
        }
    }
} 

function select_post(checkbox) {
    if (checkbox.checked) {
        checked.push(checkbox.id);
    } else {
        const idx = checked.indexOf(checkbox.id)
        if (idx > -1) {checked.splice(idx, 1)}
    }
}