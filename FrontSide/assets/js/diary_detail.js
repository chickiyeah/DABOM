document.addEventListener("DOMContentLoaded", function() {
    if (this.location.href.includes("?")) {
        if (this.location.href.split("?")[1].includes("id")) {
            const parameters = this.location.href.split("?")[1].split("&");
            parameters.forEach((param) => {
                let key = param.split("=")[0];
                let value = param.split("=")[1];
                if (key === "id") {
                    get_post(value);
                    get_comments(value);
                }
            })
        } else {
            history.back();
        }
    } else {
        history.back();
    }
})



const img_dev = document.querySelector(".swiper-wrapper")

function setdate(date){
    const p_date = document.querySelector("#post_date");
    const week = ['일', '월', '화', '수', '목', '금', '토']
    var date = new Date(date);
    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);
  
    p_date.innerText = year + "년 " + month + "월 " + day +"일 " + week[date.getDay()]+"요일";
}

function get_post(post_no) {
    const title = document.querySelector("#post_title");
    const desc = document.querySelector("#post_desc");
    console.log(post_no);

    fetch(`/api/diary/detail/${post_no}`, {
        method: "GET",
        credentials: "include"
    }).then((response) => {
        response.json().then((data) => {
            let imgs = ""
            //console.log(data)
            JSON.parse(data.images.replace(/'/g, '"')).forEach((image) => {
                let img_html = `
                <div class="swiper-slide">
                    <div class="img_box">
                        <img alt="이미지" src="${image}">
                    </div>
                </div>`
                imgs = imgs + img_html
            })
            setdate(data.created_at)
            document.querySelector(".swiper-wrapper").innerHTML = imgs

            var eat_when = "";
            if (data.eat_when == "morning") {
                eat_when = "아침"
            } else if (data.eat_when == "lunch") {
                eat_when = "점심"
            } else if (data.eat_when == "night") {
                eat_when = "저녁"
            } else if (data.eat_when == "free") {
                eat_when = "간식"
            }
            document.querySelector(".y_txt").innerText = eat_when

            desc.innerText = data.desc
            document.querySelector(".kcal").innerText = data.total_kcal+" Kcal"

            document.querySelector("#eat_txt").querySelectorAll(".r_txt").forEach((ele) => ele.remove())
            title.innerText = data.title
            if (data.with != "alone") {
                JSON.parse(data.friends.replace(/'/g, '"')).forEach(async (friend) => { 
                    let friend_d = await get_user_info(friend)
                    let f_html  = `<span class="r_txt">${friend_d.Nickname}</span>`
                    //console.log(f_html)
                    document.querySelector("#eat_txt").insertAdjacentHTML("beforeend", f_html)
                })
            }
            document.querySelector("#post_foods").innerHTML=""
            JSON.parse(data.foods.replace(/'/g, '"')).forEach(async (food) => {
                let code = food.code
                let amount = food.amount
                let food_data = await get_food_info(code)
                let food_h = `<tr>
                    <td>${food_data.name}</td>
                    <td>${food_data.kcal} Kcal</td>
                    <td>${amount} 개</td>
                </tr>`
                document.querySelector("#post_foods").insertAdjacentHTML("beforeend", food_h)
            })
            document.querySelector("#p_like_count").innerText = data.likecount
        })
    })
}

function get_comments(post_no) {
    fetch(`/api/diary/detail/${post_no}/comments`,{
        method: "GET",
        credentials: "include"
    }).then((response) => {
        response.json().then((comments) => {
            document.querySelector("#p_comment_count").innerText = comments.length
            console.log(comments)
            comments.forEach(async (comment) => {
                console.log(comment)
                let user = await get_user_info(comment.writer)
                let writed_at = new Date(comment.created_at)
                let head_h = `
                <li id=${comment.id}>
                    <div class="comment_text_box">
                        <div class="nick_box">
                            <div class="profile_img">
                                <img alt="프로필이미지" src="${user.profile_image}">
                            </div>
                            <div class="info">
                                <div class="nick">${user.Nickname}</div>
                                <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                            </div>
                        </div>
                        <div class="text_box">${comment.comment}</div>
                        <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                            <i>
                                <object aria-label="댓글아이콘" data="/assets/images/add-box-icon.svg"
                                        type="image/svg+xml"></object>
                            </i>답글 달기
                        </button>

                        <button id="hide_more_comment_${comment.id}" style="display:none" onclick="hide_sub_comment(this)">
                            <i>
                                <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                        type="image/svg+xml"></object>
                            </i>숨기기
                        </button>
                    </div>
                    
                    <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                `
                let subcomment_h_f = "";
                let i = 0;
                comment.sub_comments.forEach(async (sub_commment) => {
                    console.log(sub_commment)
                    let sub_writer = await get_user_info(sub_commment.writer);
                    let sub_writed_at = new Date(sub_commment.created_at);
                    let subcomment_h = `
                    <li>
                        <div class="nick_box">
                            <div class="profile_img">
                                <img alt="프로필이미지" src="${sub_writer.profile_image}">
                            </div>
                            <div class="info">
                                <div class="nick">${sub_writer.Nickname}</div>
                                <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                            </div>
                        </div>
                        <div class="text_box">${sub_commment.comment}</div>
                    </li>`
                    subcomment_h_f = subcomment_h_f + subcomment_h
                    i++
                    if (comment.sub_comments.length == i) {
                        let to_html = head_h + subcomment_h_f + `<li>
                        <div class="inner_comment">
                            <textarea placeholder="댓글을 작성하세요" role="textbox" rows="3"></textarea>
                            <div class="inner_comment_btn">
                                <a onclick="remove_writing_comment(this)" style="width:140px" href="javascript:">작성중인 댓글 모두 지우기</a>
                                <a onclick="write_sub_comment(this)" href="javascript:">댓글 작성</a>
                            </div>
                        </div>
                    </li></ul></li>`

                        document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                    }
                })  
            })
        })
    })
}

function show_sub_comment(element) {
    element.style.display = "none"
    element.parentElement.children[3].style.display = "";
    element.parentElement.parentElement.children[1].style.display = "";
}

function hide_sub_comment(element) {
    element.style.display = "none"
    element.parentElement.children[2].style.display = "";
    element.parentElement.parentElement.children[1].style.display = "none";
}

function remove_writing_comment(element) {
    let res = confirm("정말 작성중인 댓글을 모두 삭제하시겠습니까?\n이 작업은 취소할 수 없습니다!")

    if (res) {
        element.parentElement.parentElement.children[0].value = ""
    }
}

function write_sub_comment(element) {
    let res = confirm("댓글 작성후 수정/삭제가 불가합니다.\n작성 하시겠습니까?\n\n관리자가 보기에 부적절한 댓글이면,\n미 안내 삭제될 수 있습니다.")

    if (res) {
        let comment = element.parentElement.parentElement.children[0].value
        if (comment.trim() === '') {
            alert("댓글이 공백일수는 없습니다.")
        } else {
            console.log(comment)
        }
    }
}

/* 댓글 전체 html
                        <li>
                            <div class="comment_text_box">
                                <div class="nick_box">
                                    <div class="profile_img">
                                        <img alt="프로필이미지" src="/assets/images/default-profile.png">
                                    </div>
                                    <div class="info">
                                        <div class="nick">다봄어터</div>
                                        <div class="date">2023/04/25</div>
                                    </div>
                                </div>
                                <div class="text_box">아침은 든든히 먹어야지!!!!</div>
                                <button class="comment_btn">
                                    <i id="show_more_comment">
                                        <object aria-label="댓글아이콘" data="/assets/images/add-box-icon.svg"
                                                type="image/svg+xml"></object>
                                    </i>답글 달기
                                    <i id="hide_more_comment">
                                        <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                type="image/svg+xml"></object>
                                    </i>숨기기
                                </button>
                            </div>
                            
                            <ul class="comment_view_box"> 여기까지 초반에 들어감
                                
                                <li>
                                    <div class="nick_box">
                                        <div class="profile_img">
                                            <img alt="프로필이미지" src="/assets/images/default-profile.png">
                                        </div>
                                        <div class="info">
                                            <div class="nick">주인장</div>
                                            <div class="date">2023/04/25</div>
                                        </div>
                                    </div>
                                    <div class="text_box">그치만 너무너무 귀찮다~~</div>
                                </li>
                                <li>
                                    <div class="nick_box">
                                        <div class="profile_img">
                                            <img alt="프로필이미지" src="/assets/images/default-profile.png">
                                        </div>
                                        <div class="info">
                                            <div class="nick">주인장</div>
                                            <div class="date">2023/04/25</div>
                                        </div>
                                    </div>
                                    <div class="text_box">그치만 너무너무 귀찮다~~</div>
                                </li>
                                <li>
                                    <div class="inner_comment">
                                        <textarea placeholder="댓글을 작성하세요" role="textbox" rows="3"></textarea>
                                        <div class="inner_comment_btn">
                                            <a href="javascript:">취소</a>
                                            <a href="javascript:">댓글 작성</a>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </li>
*/

/** 음식의 세부정보를 가져오는 함수 
 * @promise (음식의 아이디)
*/
async function get_food_info(food_id) {
    return new Promise((resolve) => {
        //console.log(food_id)
        fetch(`/api/food/detail/${food_id}`, {
            method: 'GET'
        }).then((response) => {
            response.json().then((data) => {
                resolve(data)
            })
        })
    })
}

/** 유저의 세부정보를 가져오는 함수
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