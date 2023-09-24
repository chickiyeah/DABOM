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
                    connnect_alert();
                    cur_post_no = value;
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
const loading = document.querySelector(".loading");

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

    if (opener != null) {

        if (opener.document.location.href.includes("group/detail")) {
            document.getElementById("share").style.display = "none"
            let g_id = opener.document.location.href.split("?")[1]
            if (g_id.includes("id=")) {
                document.getElementById("editbox").style.display = "none";
                g_id = g_id.split("id=")[1].split("&")[0];


                fetch(`/api/diary/detail/${g_id}/${post_no}`, {
                    method: "GET",
                    credentials: "include"
                }).then((response) => {
                    if (response.status === 200) {
                        response.json().then(async (data) => {
                            let me = await get_me_all();
                            let like_icon = document.getElementById("like_icon")
                            JSON.parse(me.liked_post.replace(/'/g, '"')).forEach((post) => {
                                if (post === parseInt(post_no)) {
                                    like_icon.attributes.data.value = "../assets/images/liked-icon.svg"
                                }
                            })

                            let imgs = ""
                            document.getElementById("p_like_count").innerText = data.likecount
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
                    } else {
                        alert("비정상 접근으로 의심됩니다. 다시 시도해주세요.")
                        opener.location.reload()
                        window.close()
                    }
                })
            }
        }

        if (opener.location.href.includes('record') || opener.location.href.includes('posts')) {
            document.getElementById("share").setAttribute('onclick', `share_post(${post_no})`)

            document.getElementById("editbox").children[0].href = "/diary_update?id="+post_no
            
            fetch(`/api/diary/detail/${post_no}`, {
                method: "GET",
                credentials: "include"
            }).then((response) => {
                if (response.status === 200) {
                    response.json().then(async (data) => {
                        let me = await get_me_all();
                        let like_icon = document.getElementById("like_icon")
                        JSON.parse(me.liked_post.replace(/'/g, '"')).forEach((post) => {
                            if (post === parseInt(post_no)) {
                                like_icon.attributes.data.value = "../assets/images/liked-icon.svg"
                            }
                        })

                        let imgs = ""
                        document.getElementById("p_like_count").innerText = data.likecount
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
                } else {
                    alert("비정상 접근으로 의심됩니다. 다시 시도해주세요.")
                    opener.location.reload()
                    window.close()
                }
            })
        }
    } else {
        // 공유 링크로 접속
        document.getElementById("share").style.display = "none"
        let key = document.location.href.split("?")[1]
        if (key.includes("v_key=")) {
            key = key.split("v_key=")[1].split("&")[0];
        }
        document.getElementById("editbox").style.display = "none";
        fetch(`/api/diary/${post_no}/check_key`, {
            method: 'POST',
            body: JSON.stringify({
                "verify_key": key
            })
        }).then(function (response) {
            if (response.status === 200) {
                response.json().then(async (data) => {
                    console.log(data)
                    //let me = await get_me_all();
                    /*let like_icon = document.getElementById("like_icon")
                    JSON.parse(me.liked_post.replace(/'/g, '"')).forEach((post) => {
                        if (post === parseInt(post_no)) {
                            like_icon.attributes.data.value = "../assets/images/liked-icon.svg"
                        }
                    })*/

                    let imgs = ""
                    document.getElementById("p_like_count").innerText = data.likecount
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


                    //댓글
                    let comments = data.comments
                    
                        document.querySelector("#p_comment_count").innerText = comments.length
                        console.log(comments)
                        //let sender = await get_me()
                        comments.forEach(async (comment) => {
                            console.log(comment)
                            let user = await get_user_info(comment.writer)
                            let writed_at = new Date(comment.created_at)
                            let n_comment = comment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                            let head_h = ""
        
                            
                                head_h = `
                                        <li id=${comment.id}>
                                            <div class="comment_text_box" id="comment_normal_${comment.id}">
                                                <div class="comment_area">
                                                    <div class="nick_box">
                                                        <div class="profile_img">
                                                            <img alt="프로필이미지" src="${user.profile_image}">
                                                        </div>
                                                        <div class="info">
                                                            <div id=${user.ID} class="nick">${user.Nickname}</div>
                                                            <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="text_box" id="comment_default_${comment.id}">${n_comment}</div>
                                                
                                                <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>답글 달기
                                                </button>
        
                                                <button id="hide_more_comment_${comment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment(this)">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>숨기기
                                                </button>
                                            </div>
                                            <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                                                <li id="sub_comments_${comment.id}_main">
                                                    <div class="inner_comment" id="write_sub_${comment.id}">
                                                    <div class="sub_comment_area" contenteditable></div>
                                                        <div class="inner_comment_btn">
                                                            <a id="${comment.id}" onclick="hide_sub_comment(this)" href="javascript:">취소</a>
                                                            <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                        </div>
                                                    </div>
                                                </li>
                                `
                            
                            let subcomment_h_f = "";
                            let i = 0;
                            
                            if (comment.sub_comments.length > 0) {
                                comment.sub_comments.forEach(async (sub_commment) => {
                                    console.log(sub_commment)
                                    let sub_writer = await get_user_info(sub_commment.writer);
                                    let sub_writed_at = new Date(sub_commment.created_at);
                                    let n_comment = sub_commment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                                    let subcomment_h = ""
                                    
                                     subcomment_h = `
                                                    <li id="sub_comments_${comment.id}_${sub_commment.id}">
                                                        <div id="comment_normal_${sub_commment.id}">
                                                            <div class="comment_area">
                                                                <div class="nick_box">
                                                                    <div class="profile_img">
                                                                        <img alt="프로필이미지" src="${sub_writer.profile_image}">
                                                                    </div>
                                                                    <div class="info">
                                                                        <div id=${sub_writer.ID} class="nick">${sub_writer.Nickname}</div>
                                                                        <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div class="text_box" id="comment_default_${sub_commment.id}">${n_comment}</div>
                                                            <button class="comment_btn" id="show_more_comment_${sub_commment.id}" onclick="show_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>답글 달기
                                                            </button>
                                                            <button id="hide_more_comment_${sub_commment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>숨기기
                                                            </button>
                                                        </div>
                                                        <div class="inner_comment" style="display:none" id="write_sub_${sub_commment.id}">
                                                            <div class="sub_comment_area" contenteditable><b style="color: orange" id=tag_${sub_commment.writer} contenteditable="false">@${sub_writer.Nickname}&nbsp;</b></div>
                                                            <div class="inner_comment_btn">
                                                                <a id="${sub_commment.id}" onclick="hide_sub_comment_write(this)" href="javascript:">취소</a>
                                                                <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                            </div>
                                                        </div>
                                                    </li>`
                                    
                                    subcomment_h_f = subcomment_h_f + subcomment_h
                                    i++
                                    if (comment.sub_comments.length == i) {
                                        let to_html = head_h + subcomment_h_f + `</ul></li>`
        
                                        document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                                    }
                                })
                            } else {
                                let to_html = head_h + `</ul></li>`
                                document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                            }
                        })
                    
                })
            } else {
                alert("링크가 손상되었습니다.\n글 작성자에게 다시 링크를 요청해보세요.")
                window.close()
            }
        })
    }
}

function get_comments(post_no) {
    if (opener != null) {
        if (opener.document.location.href.includes("group/detail")) {
            let g_id = opener.document.location.href.split("?")[1]
            if (g_id.includes("id=")) {
                g_id = g_id.split("id=")[1]

                fetch(`/api/diary/detail/${g_id}/${post_no}/comments`,{
                    method: "GET",
                    credentials: "include"
                }).then((response) => {
                    response.json().then(async (comments) => {
                        document.querySelector("#p_comment_count").innerText = comments.length
                        console.log(comments)
                        let sender = await get_me()
                        comments.forEach(async (comment) => {
                            console.log(comment)
                            let user = await get_user_info(comment.writer)
                            let writed_at = new Date(comment.created_at)
                            let n_comment = comment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                            let head_h = ""
        
                            if (sender.ID === user.ID) {
                                head_h = `
                                        <li id=${comment.id}>
                                            <div class="comment_text_box" id="comment_normal_${comment.id}">
                                                <div class="comment_area">
                                                    <div class="nick_box">
                                                        <div class="profile_img">
                                                            <img alt="프로필이미지" src="${user.profile_image}">
                                                        </div>
                                                        <div class="info">
                                                            <div id=${user.ID} class="nick">${user.Nickname}</div>
                                                            <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                                                        </div>
                                                    </div>
                                                    <div class="comment_button">
                                                        <button type="button" onclick="comment_edit(${comment.id})">수정</button>
                                                        <button type="button" onclick="comment_delete(${comment.id})">삭제</button>
                                                    </div>
                                                </div>
                                                <div class="text_box" id="comment_default_${comment.id}">${n_comment}</div>
                                                
                                                <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>답글 달기
                                                </button>
        
                                                <button id="hide_more_comment_${comment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment(this)">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>숨기기
                                                </button>
                                            </div>
                                            <div id="comment_edit_${comment.id}" style="display: none">
                                                    <div class="sub_comment_area" contenteditable>${comment.comment}</div>
                                                        <div class="inner_comment_btn" style="text-align: right; margin-top: 5px; margin-bottom: 5px;">
                                                            <a href="javascript:" onclick="comment_edit_hide(${comment.id})" style="display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">취소</a>
                                                            <a href="javascript:" onclick="comment_update(${comment.id})" style="backgroung: white; border: 1px solid #222; border-radius: 3px; display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">수정 완료</a>
                                                        </div>
                                            </div>
                                            <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                                                <li id="sub_comments_${comment.id}_main">
                                                    <div class="inner_comment" id="write_sub_${comment.id}">
                                                    <div class="sub_comment_area" contenteditable></div>
                                                        <div class="inner_comment_btn">
                                                            <a id="${comment.id}" onclick="hide_sub_comment(this)" href="javascript:">취소</a>
                                                            <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                        </div>
                                                    </div>
                                                </li>
                                `
                            } else {
                                head_h = `
                                        <li id=${comment.id}>
                                            <div class="comment_text_box" id="comment_normal_${comment.id}">
                                                <div class="comment_area">
                                                    <div class="nick_box">
                                                        <div class="profile_img">
                                                            <img alt="프로필이미지" src="${user.profile_image}">
                                                        </div>
                                                        <div class="info">
                                                            <div id=${user.ID} class="nick">${user.Nickname}</div>
                                                            <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="text_box" id="comment_default_${comment.id}">${n_comment}</div>
                                                
                                                <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>답글 달기
                                                </button>
        
                                                <button id="hide_more_comment_${comment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment(this)">
                                                    <i>
                                                        <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                type="image/svg+xml"></object>
                                                    </i>숨기기
                                                </button>
                                            </div>
                                            <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                                                <li id="sub_comments_${comment.id}_main">
                                                    <div class="inner_comment" id="write_sub_${comment.id}">
                                                    <div class="sub_comment_area" contenteditable></div>
                                                        <div class="inner_comment_btn">
                                                            <a id="${comment.id}" onclick="hide_sub_comment(this)" href="javascript:">취소</a>
                                                            <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                        </div>
                                                    </div>
                                                </li>
                                `
                            }
                            let subcomment_h_f = "";
                            let i = 0;
                            
                            if (comment.sub_comments.length > 0) {
                                comment.sub_comments.forEach(async (sub_commment) => {
                                    console.log(sub_commment)
                                    let sub_writer = await get_user_info(sub_commment.writer);
                                    let sub_writed_at = new Date(sub_commment.created_at);
                                    let n_comment = sub_commment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                                    let subcomment_h = ""
                                    if (sender.ID === user.ID) {
                                        subcomment_h = `
                                                    <li id="sub_comments_${comment.id}_${sub_commment.id}">
                                                        <div id="comment_normal_${sub_commment.id}">
                                                            <div class="comment_area">
                                                                <div class="nick_box">
                                                                    <div class="profile_img">
                                                                        <img alt="프로필이미지" src="${sub_writer.profile_image}">
                                                                    </div>
                                                                    <div class="info">
                                                                        <div id=${sub_writer.ID} class="nick">${sub_writer.Nickname}</div>
                                                                        <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                                                                    </div>
                                                                </div>
                                                                <div class="comment_button">
                                                                    <button type="button" onclick="comment_edit(${sub_commment.id})">수정</button>
                                                                    <button type="button" onclick="comment_delete(${sub_commment.id})">삭제</button>
                                                                </div>
                                                            </div>
                                                            <div class="text_box" id="comment_default_${sub_commment.id}">${n_comment}</div>
                                                            <button class="comment_btn" id="show_more_comment_${sub_commment.id}" onclick="show_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>답글 달기
                                                            </button>
                                                            <button id="hide_more_comment_${sub_commment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>숨기기
                                                            </button>
                                                        </div>
                                                        <div id="comment_edit_${sub_commment.id}" style="display: none">
                                                            <div class="sub_comment_area" contenteditable>${n_comment}</div>
                                                            <div class="inner_comment_btn" style="text-align: right; margin-top: 5px; margin-bottom: 5px;">
                                                                <a href="javascript:" onclick="comment_edit_hide(${sub_commment.id})" style="display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">취소</a>
                                                                <a href="javascript:" onclick="comment_update(${sub_commment.id})" style="background: white; border: 1px solid #222; border-radius: 3px; display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">수정 완료</a>
                                                            </div>
                                                        </div>
                                                        <div class="inner_comment" style="display:none" id="write_sub_${sub_commment.id}">
                                                            <div class="sub_comment_area" contenteditable><b style="color: orange" id=tag_${sub_commment.writer} contenteditable="false">@${sub_writer.Nickname}&nbsp;</b></div>
                                                            <div class="inner_comment_btn">
                                                                <a id="${sub_commment.id}" onclick="hide_sub_comment_write(this)" href="javascript:">취소</a>
                                                                <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                            </div>
                                                        </div>
                                                    </li>`
                                    } else {
                                        subcomment_h = `
                                                    <li id="sub_comments_${comment.id}_${sub_commment.id}">
                                                        <div id="comment_normal_${sub_commment.id}">
                                                            <div class="comment_area">
                                                                <div class="nick_box">
                                                                    <div class="profile_img">
                                                                        <img alt="프로필이미지" src="${sub_writer.profile_image}">
                                                                    </div>
                                                                    <div class="info">
                                                                        <div id=${sub_writer.ID} class="nick">${sub_writer.Nickname}</div>
                                                                        <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div class="text_box" id="comment_default_${sub_commment.id}">${n_comment}</div>
                                                            <button class="comment_btn" id="show_more_comment_${sub_commment.id}" onclick="show_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>답글 달기
                                                            </button>
                                                            <button id="hide_more_comment_${sub_commment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment_write(this)">
                                                                <i>
                                                                    <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                            type="image/svg+xml"></object>
                                                                </i>숨기기
                                                            </button>
                                                        </div>
                                                        <div class="inner_comment" style="display:none" id="write_sub_${sub_commment.id}">
                                                            <div class="sub_comment_area" contenteditable><b style="color: orange" id=tag_${sub_commment.writer} contenteditable="false">@${sub_writer.Nickname}&nbsp;</b></div>
                                                            <div class="inner_comment_btn">
                                                                <a id="${sub_commment.id}" onclick="hide_sub_comment_write(this)" href="javascript:">취소</a>
                                                                <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                            </div>
                                                        </div>
                                                    </li>`
                                    }
                                    subcomment_h_f = subcomment_h_f + subcomment_h
                                    i++
                                    if (comment.sub_comments.length == i) {
                                        let to_html = head_h + subcomment_h_f + `</ul></li>`
        
                                        document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                                    }
                                })
                            } else {
                                let to_html = head_h + `</ul></li>`
                                document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                            }
                        })
                    })
                })
            }
        }

        if (opener.location.href.includes("record") || opener.location.href.includes('posts')) {
            fetch(`/api/diary/detail/${post_no}/comments`,{
                method: "GET",
                credentials: "include"
            }).then((response) => {
                response.json().then(async (comments) => {
                    document.querySelector("#p_comment_count").innerText = comments.length
                    console.log(comments)
                    let sender = await get_me()
                    comments.forEach(async (comment) => {
                        console.log(comment)
                        let user = await get_user_info(comment.writer)
                        let writed_at = new Date(comment.created_at)
                        let n_comment = comment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                        let head_h = ""
    
                        if (sender.ID === user.ID) {
                            head_h = `
                                    <li id=${comment.id}>
                                        <div class="comment_text_box" id="comment_normal_${comment.id}">
                                            <div class="comment_area">
                                                <div class="nick_box">
                                                    <div class="profile_img">
                                                        <img alt="프로필이미지" src="${user.profile_image}">
                                                    </div>
                                                    <div class="info">
                                                        <div id=${user.ID} class="nick">${user.Nickname}</div>
                                                        <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                                                    </div>
                                                </div>
                                                <div class="comment_button">
                                                    <button type="button" onclick="comment_edit(${comment.id})">수정</button>
                                                    <button type="button" onclick="comment_delete(${comment.id})">삭제</button>
                                                </div>
                                            </div>
                                            <div class="text_box" id="comment_default_${comment.id}">${n_comment}</div>
                                            
                                            <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                                                <i>
                                                    <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                            type="image/svg+xml"></object>
                                                </i>답글 달기
                                            </button>
    
                                            <button id="hide_more_comment_${comment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment(this)">
                                                <i>
                                                    <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                            type="image/svg+xml"></object>
                                                </i>숨기기
                                            </button>
                                        </div>
                                        <div id="comment_edit_${comment.id}" style="display: none">
                                                <div class="sub_comment_area" contenteditable>${comment.comment}</div>
                                                    <div class="inner_comment_btn" style="text-align: right; margin-top: 5px; margin-bottom: 5px;">
                                                        <a href="javascript:" onclick="comment_edit_hide(${comment.id})" style="display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">취소</a>
                                                        <a href="javascript:" onclick="comment_update(${comment.id})" style="backgroung: white; border: 1px solid #222; border-radius: 3px; display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">수정 완료</a>
                                                    </div>
                                        </div>
                                        <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                                            <li id="sub_comments_${comment.id}_main">
                                                <div class="inner_comment" id="write_sub_${comment.id}">
                                                <div class="sub_comment_area" contenteditable></div>
                                                    <div class="inner_comment_btn">
                                                        <a id="${comment.id}" onclick="hide_sub_comment(this)" href="javascript:">취소</a>
                                                        <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                    </div>
                                                </div>
                                            </li>
                            `
                        } else {
                            head_h = `
                                    <li id=${comment.id}>
                                        <div class="comment_text_box" id="comment_normal_${comment.id}">
                                            <div class="comment_area">
                                                <div class="nick_box">
                                                    <div class="profile_img">
                                                        <img alt="프로필이미지" src="${user.profile_image}">
                                                    </div>
                                                    <div class="info">
                                                        <div id=${user.ID} class="nick">${user.Nickname}</div>
                                                        <div class="date">${writed_at.getFullYear()}/${writed_at.getMonth()+1}/${writed_at.getDate()}</div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="text_box" id="comment_default_${comment.id}">${n_comment}</div>
                                            
                                            <button id="show_more_comment_${comment.id}" onclick="show_sub_comment(this)" class="comment_btn">
                                                <i>
                                                    <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                            type="image/svg+xml"></object>
                                                </i>답글 달기
                                            </button>
    
                                            <button id="hide_more_comment_${comment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment(this)">
                                                <i>
                                                    <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                            type="image/svg+xml"></object>
                                                </i>숨기기
                                            </button>
                                        </div>
                                        <ul id="sub_comments_${comment.id}" class="comment_view_box" style="display:none">
                                            <li id="sub_comments_${comment.id}_main">
                                                <div class="inner_comment" id="write_sub_${comment.id}">
                                                <div class="sub_comment_area" contenteditable></div>
                                                    <div class="inner_comment_btn">
                                                        <a id="${comment.id}" onclick="hide_sub_comment(this)" href="javascript:">취소</a>
                                                        <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                    </div>
                                                </div>
                                            </li>
                            `
                        }
                        let subcomment_h_f = "";
                        let i = 0;
                        
                        if (comment.sub_comments.length > 0) {
                            comment.sub_comments.forEach(async (sub_commment) => {
                                console.log(sub_commment)
                                let sub_writer = await get_user_info(sub_commment.writer);
                                let sub_writed_at = new Date(sub_commment.created_at);
                                let n_comment = sub_commment.comment.replace(/&lt;/g,"<").replace(/&gt;/g,">")
                                let subcomment_h = ""
                                if (sender.ID === user.ID) {
                                    subcomment_h = `
                                                <li id="sub_comments_${comment.id}_${sub_commment.id}">
                                                    <div id="comment_normal_${sub_commment.id}">
                                                        <div class="comment_area">
                                                            <div class="nick_box">
                                                                <div class="profile_img">
                                                                    <img alt="프로필이미지" src="${sub_writer.profile_image}">
                                                                </div>
                                                                <div class="info">
                                                                    <div id=${sub_writer.ID} class="nick">${sub_writer.Nickname}</div>
                                                                    <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                                                                </div>
                                                            </div>
                                                            <div class="comment_button">
                                                                <button type="button" onclick="comment_edit(${sub_commment.id})">수정</button>
                                                                <button type="button" onclick="comment_delete(${sub_commment.id})">삭제</button>
                                                            </div>
                                                        </div>
                                                        <div class="text_box" id="comment_default_${sub_commment.id}">${n_comment}</div>
                                                        <button class="comment_btn" id="show_more_comment_${sub_commment.id}" onclick="show_sub_comment_write(this)">
                                                            <i>
                                                                <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                        type="image/svg+xml"></object>
                                                            </i>답글 달기
                                                        </button>
                                                        <button id="hide_more_comment_${sub_commment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment_write(this)">
                                                            <i>
                                                                <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                        type="image/svg+xml"></object>
                                                            </i>숨기기
                                                        </button>
                                                    </div>
                                                    <div id="comment_edit_${sub_commment.id}" style="display: none">
                                                        <div class="sub_comment_area" contenteditable>${n_comment}</div>
                                                        <div class="inner_comment_btn" style="text-align: right; margin-top: 5px; margin-bottom: 5px;">
                                                            <a href="javascript:" onclick="comment_edit_hide(${sub_commment.id})" style="display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">취소</a>
                                                            <a href="javascript:" onclick="comment_update(${sub_commment.id})" style="background: white; border: 1px solid #222; border-radius: 3px; display: inline-block; text-align: center; font-size: 12px; width: 80px; height: 24px; line-height: 2">수정 완료</a>
                                                        </div>
                                                    </div>
                                                    <div class="inner_comment" style="display:none" id="write_sub_${sub_commment.id}">
                                                        <div class="sub_comment_area" contenteditable><b style="color: orange" id=tag_${sub_commment.writer} contenteditable="false">@${sub_writer.Nickname}&nbsp;</b></div>
                                                        <div class="inner_comment_btn">
                                                            <a id="${sub_commment.id}" onclick="hide_sub_comment_write(this)" href="javascript:">취소</a>
                                                            <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                        </div>
                                                    </div>
                                                </li>`
                                } else {
                                    subcomment_h = `
                                                <li id="sub_comments_${comment.id}_${sub_commment.id}">
                                                    <div id="comment_normal_${sub_commment.id}">
                                                        <div class="comment_area">
                                                            <div class="nick_box">
                                                                <div class="profile_img">
                                                                    <img alt="프로필이미지" src="${sub_writer.profile_image}">
                                                                </div>
                                                                <div class="info">
                                                                    <div id=${sub_writer.ID} class="nick">${sub_writer.Nickname}</div>
                                                                    <div class="date">${sub_writed_at.getFullYear()}/${sub_writed_at.getMonth()+1}/${sub_writed_at.getDate()}</div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div class="text_box" id="comment_default_${sub_commment.id}">${n_comment}</div>
                                                        <button class="comment_btn" id="show_more_comment_${sub_commment.id}" onclick="show_sub_comment_write(this)">
                                                            <i>
                                                                <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                                        type="image/svg+xml"></object>
                                                            </i>답글 달기
                                                        </button>
                                                        <button id="hide_more_comment_${sub_commment.id}" style="display:none" class="comment_btn" onclick="hide_sub_comment_write(this)">
                                                            <i>
                                                                <object aria-label="댓글아이콘" data="/assets/images/minu-box-icon.svg"
                                                                        type="image/svg+xml"></object>
                                                            </i>숨기기
                                                        </button>
                                                    </div>
                                                    <div class="inner_comment" style="display:none" id="write_sub_${sub_commment.id}">
                                                        <div class="sub_comment_area" contenteditable><b style="color: orange" id=tag_${sub_commment.writer} contenteditable="false">@${sub_writer.Nickname}&nbsp;</b></div>
                                                        <div class="inner_comment_btn">
                                                            <a id="${sub_commment.id}" onclick="hide_sub_comment_write(this)" href="javascript:">취소</a>
                                                            <a href="javascript:" onclick="write_sub_comment(this)">답글 작성</a>
                                                        </div>
                                                    </div>
                                                </li>`
                                }
                                subcomment_h_f = subcomment_h_f + subcomment_h
                                i++
                                if (comment.sub_comments.length == i) {
                                    let to_html = head_h + subcomment_h_f + `</ul></li>`
    
                                    document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                                }
                            })
                        } else {
                            let to_html = head_h + `</ul></li>`
                            document.querySelector(".comment_list").insertAdjacentHTML("beforeend",to_html)
                        }
                    })
                })
            })
        }
    } 
}

` 수정된 댓글 html
                        <li>
                            <div class="comment_text_box">
                                <div class="comment_area">
                                    <div class="nick_box">
                                        <div class="profile_img">
                                            <img alt="프로필이미지" src="../assets/images/default-profile.png">
                                        </div>
                                        <div class="info">
                                            <div class="nick">다봄어터</div>
                                            <div class="date">2023/04/25</div>
                                        </div>
                                    </div>
                                    <a href="javascript:" class="comment_button">
                                        <i><img src="/assets/images/more-icon.svg" alt="더보기버튼"></i>
                                        <div class="comment_button_box">
                                            <button type="button" onclick="comment_edit({comment.id})">수정</button>
                                            <button type="button" onclick="comment_delete({comment.id})>삭제</button>
                                        </div>
                                    </a>
                                </div>
                                <div class="text_box">아침은 든든히 먹어야지!!!!</div>
                                <button class="comment_btn">
                                    <i>
                                        <object aria-label="댓글아이콘" data="../assets/images/add-box-icon.svg"
                                                type="image/svg+xml"></object>
                                    </i>답글 달기
                                </button>
                            </div>
                            <ul class="comment_view_box">
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
`

function show_sub_comment(element) {
    element.style.display = "none"
    let id = parseInt(element.id.replace("show_more_comment_", ""))
    let hide_sub_comment = document.getElementById(`hide_more_comment_${id}`)
    let sub_comment_div = document.getElementById(`sub_comments_${id}`)
    sub_comment_div.style.display = "";
    hide_sub_comment.style.display = "";
}

function hide_sub_comment(element) {
    let id = parseInt(element.id.replace("hide_more_comment_", ""))
    let show_sub_comment = document.getElementById(`show_more_comment_${id}`)
    let hide_sub_comment = document.getElementById(`hide_more_comment_${id}`)
    let sub_comment_div = document.getElementById(`sub_comments_${id}`)
    sub_comment_div.style.display = "none";
    hide_sub_comment.style.display = "none";
    show_sub_comment.style.display = "";
}

function show_sub_comment_write(element) {
    element.style.display = "none"
    let id = parseInt(element.id.replace("show_more_comment_", ""))
    let hide_sub_comment = document.getElementById(`hide_more_comment_${id}`)
    let sub_comment_div = document.getElementById(`write_sub_${id}`)
    sub_comment_div.style.display = "";
    hide_sub_comment.style.display = "";
}

function hide_sub_comment_write(element) {
    let id = parseInt(element.id.replace("hide_more_comment_", ""))
    let show_sub_comment = document.getElementById(`show_more_comment_${id}`)
    let hide_sub_comment = document.getElementById(`hide_more_comment_${id}`)
    let sub_comment_div = document.getElementById(`write_sub_${id}`)
    sub_comment_div.style.display = "none";
    hide_sub_comment.style.display = "none";
    show_sub_comment.style.display = "";
}

function comment_edit(comment_id) {
    let normal_div = document.getElementById(`comment_normal_${comment_id}`)
    let edit_div = document.getElementById(`comment_edit_${comment_id}`)
    let default_comment = document.getElementById(`comment_default_${comment_id}`)
    edit_div.children[0].innerHTML = default_comment.innerHTML
    normal_div.style.display = "none"
    edit_div.style.display = ""
}

function comment_edit_hide(comment_id) {
    let normal_div = document.getElementById(`comment_normal_${comment_id}`)
    let edit_div = document.getElementById(`comment_edit_${comment_id}`)
    normal_div.style.display = ""
    edit_div.style.display = "none"
}

function comment_update(comment_id) {
    let normal_div = document.getElementById(`comment_normal_${comment_id}`)
    let edit_div = document.getElementById(`comment_edit_${comment_id}`)
    const loading = document.querySelector(".loading");
    
    let new_comment = edit_div.children[0].innerHTML
    loading.style.display = ""
    fetch(`api/diary/detail/${cur_post_no}/comment/${comment_id}/edit`, {
        method: 'POST',
        credentials: "include",
        body: JSON.stringify({
            "comment": new_comment
        })
    }).then((response) => {
        if (response.status === 200) {
            /*normal_div.style.display = ""
            edit_div.style.display = "none"
            loading.style.display = "none"*/
            location.reload()
        } else {
            alert("댓글 수정중 알수없는 오류가 발생하였습니다.")
            loading.style.display = "none"
        }
    })
}

function comment_delete(comment_id) {
    let con = confirm("이 댓글을 정말 삭제하시겠습니까?")
    if (con) {
        const loading = document.querySelector(".loading");
        loading.style.display = ""
        fetch(`api/diary/detail/${cur_post_no}/comment/${comment_id}/remove`, {
            method: 'DELETE',
            credentials: "include"
        }).then((response) => {
            if (response.status === 200) {
                location.reload()
            } else {
                alert("댓글 삭제중 알수없는 오류가 발생하였습니다.")
                loading.style.display = "none"
            }
        })
    }
}

async function verify_token() {
    return new Promise(async function(resolve, reject) {
        fetch("/api/user/cookie/get_info",{ methon: 'GET', credentials: "include" }).then(async (res) => {if (res.status === 200) { res.json().then(async (json) => {resolve(json)})} else { }})
    })
}

//알림 채널명 : Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr
async function connnect_alert() {
    let user = await verify_token()
    console.log(user[0])
    let us_id = user[0].ID
    console.log("token verified")
    let u_nick = user[0].Nickname
    alertsocket = new WebSocket(`wss://dabom.kro.kr/chat/ws?username=${u_nick}&u_id=${us_id}&channel=Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr`)

    alertsocket.onerror = async () => {
        console.error("웹소켓 연결실패 새로고침으로 문제 해결을 시도합니다.")
        location.reload()
    }

    alertsocket.onopen = async () => {
        console.log("알림 소켓 연결됨.")
    }

    alertsocket.onmessage = async (event) => {
        let alert
        try {
            alert = JSON.parse(event.data)
            if (typeof(alert) === "string") {
                alert = JSON.parse(alert)
                console.log(alert)
            }
        } catch (e) {
            alert = event.data
        }

        if (alert.message.includes("alert")) {
            console.log(alert)
            let a_data = alert.message.split("/*/")
                let tar_id = a_data[2]
                let pf_image = a_data[3]
                let url = a_data[4]
                let title = a_data[5]
                let msg = a_data[6]

                if (tar_id === us_id) {
                    bell_new_alert.style.display = 'block'
                    let html = `<a class="bell_item" href="${url}" target="_black">
                                    <div id="new_alert" class="dabom_alert"></div>
                                    <div class="profile_img">
                                        <img alt="프로필이미지" src="${pf_image}">
                                    </div>
                                    <div class="txt_box">
                                        <p>${title}</p>
                                        <p>${msg}</p>
                                    </div>
                                </a>`
                    alert_list.insertAdjacentHTML('afterbegin', html);
                    apply_event()
                }
            //loading.style.display = 'none';
        }
    }
}

/** 알림 전송 ( 알림 종류, 목표의 유저 아이디, 알림을 클릭하면 이동할 링크, 메시지(선택) ) */
async function send_alert(type, tar_id, url) {
    let user = await get_user_info(tar_id);
    let sender = await get_me()
    console.log(sender)
    let nick = sender.Nickname
    console.log(nick)
    let id = user.ID
    let profile_image = user.profile_image || "../assets/images/default-profile.png"
    let alerts = ['post_main_comment', 'post_sub_comment', 'post_tag_comment']

    if (id === sender.ID) { location.reload(); } else {
        if (alerts.includes(type) === true) {
            var msg
            var title

            if (type === "post_main_comment") {
                msg = `${nick} 님이 회원님이 작성한 글에 댓글을 달았습니다.`
                title = "작성한 글에 댓글이 달렸습니다."
            }

            if (type === "post_sub_comment") {
                msg = `${nick} 님이 회원님이 작성한 댓글에 답글을 달았습니다.`
                title = "작성한 댓글에 답글이 달렸습니다."
            }

            if (type === "post_tag_comment") {
                msg = `${nick} 님이 댓글에서 회원님을 언급했습니다.`
                title = "댓글에 언급되었습니다."
            }

            msg = `alert/*/${type}/*/${id}/*/${profile_image}/*/${url}/*/${title}/*/${msg}`
            console.log(msg)
            alertsocket.send(msg)
            console.log("알림 전송됨")
            location.reload();
        }else{
            console.log("알림 타입 포함 오류")
            throw new Error("알수 없는 알림 타입입니다. 타입을 확인하세요.")
        }
    }
} 

async function get_me() {
    return new Promise(async function(resolve, reject) {fetch("/api/user/cookie/get_info", {method: "GET"}).then((res) => {res.json().then((data) => {resolve(data[0])});})})
}

async function get_me_all() {
    return new Promise(async function(resolve, reject) {fetch("/api/user/cookie/me", {method: "GET"}).then((res) => {res.json().then((data) => {resolve(data)});})})
}

function write_comment(element) {
    let comment = element.parentElement.children[1].value
    const loading = document.querySelector(".loading");
    if (comment.trim() === '') {
        alert("댓글은 공백 일수 없습니다.")
    } else {
        loading.style.display = ""
        fetch(`/api/diary/detail/${cur_post_no}/comment/main`, {
            method: 'POST',
            credentials: 'include',
            body: JSON.stringify({
                'comment': comment
            })
        }).then(async (response) => {
            if (response.status === 200) {
                let sender = await get_me()
                send_alert("post_main_comment", sender.ID, location.href);
            } else {
                loading.style.display = "none"
                if (response.status === 422) {
                    alert("다봄에 로그인해야 댓글 작성이 가능합니다!")
                }
            }
        })
    }
}


function write_sub_comment(element) {
    let comment = element.parentElement.parentElement.children[0].innerHTML
    if (comment.trim() === '') {
        alert("답글은 공백 일수 없습니다.")
    } else {
        let main_comment_id = parseInt(element.parentElement.parentElement.parentElement.parentElement.parentElement.id)
        fetch(`/api/diary/detail/${cur_post_no}/comment/${main_comment_id}/sub`, {
            method: 'POST',
            credentials: 'include',
            body: JSON.stringify({
                'comment': comment
            })
        }).then(async (response) => {
            if (response.status === 422) {
                alert("다봄에 로그인해야 답글 작성이 가능합니다!")
                loading.style.display = "none"
            }

            if (response.status === 200) {
                let sender = await get_me()
                if (comment.includes(`<b style="color: orange" id="tag_`)) {
                    let id = comment.split(`<b style="color: orange" id="tag_`)[1].split("\"")[0]
                    send_alert("post_tag_comment", id, location.href);
                }
                send_alert("post_sub_comment", sender.ID, location.href);
            }
        })
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


function like_switch(ele) {
    let button = ele.children[0].children[0].attributes.data.value

    if (button.includes("liked")) {
        //좋아요 취소

        fetch(`/api/diary/${cur_post_no}/unlike`, {
            method: 'POST',
            credentials: "include"
        }).then((response) => {
            if (response.status === 200) {
                location.reload()
            } 

            if (response.status === 403) {
                alert("다봄에 로그인해야 좋아요 조작이 가능합니다!")
            }
        })
    } else {
        //좋아요

        fetch(`/api/diary/${cur_post_no}/like`, {
            method: 'POST',
            credentials: "include"
        }).then((response) => {
            if (response.status === 200) {
                location.reload()
            } 

            if (response.status === 403) {
                alert("다봄에 로그인해야 좋아요가 가능합니다!")
            }
        })
    }
}

/** 게시글을 삭제하는 함수 */
function delete_post() {

        let del_con = confirm("정말 게시글을 삭제하시겠습니까?")

        if (del_con) {
            let ids = []
            ids.push(cur_post_no)
            console.log(ids)
            fetch("/api/diary/delete", {
                method: "DELETE",
                credentials: "include",
                body: JSON.stringify({
                    post_ids : ids
                })
            }).then((response) => {
                if (response.status === 200) {
                    opener.location.reload()
                    window.close()
                }
            })
        }
    
} 

/** 선택한 게시글을 공유하는 함수 */
function share_post(post_id) {
    fetch(`/api/diary/${post_id}/share`, {
        method: 'POST'
    }).then((response) => {
        if (response.status === 200) {
            response.json().then((data) => {
                console.log(data)
                navigator.clipboard.writeText(data)
                    .then(() => {
                    alert("공유링크가 클립보드에 복사되었습니다.")
                })
                    .catch(err => {
                    console.log('Something went wrong', err);
                })
            })
        }
    })
}
