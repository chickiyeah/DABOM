window.addEventListener('DOMContentLoaded', async function() {
    if(this.location.href.includes('?')) {
        let parameters = this.location.href.split('?')[1].split('&');
        parameters.forEach((param) => {
            let key = param.split('=')[0];
            let value = param.split('=')[1];
            if (key === 'id') {
                // 가입중인거
                fetch(`/api/group/p_groups`, {
                method: 'GET',
                credentials: "include"
                }).then((res) => {
                    res.json().then((data) => {
                        let joined = JSON.parse(data.groups)
                        if (joined.includes(parseInt(value))) {
                            get_group_data(value)
                            get_write(value, 1)
                            if (this.location.href.includes("detail")) {
                                let info_btn = document.querySelector("#edit_btn")
                                info_btn.setAttribute("onclick", `show_info()`)
                                mem_list_invite.remove()
                                mem_list_admin_check.remove()
                            } else {
                                let edit_btn = document.querySelector("#edit_btn")
                                edit_btn.innerHTML = "수정하기"
                                edit_btn.setAttribute("onclick", `show_info_edit(${value})`)
                                //group_change_popup
                            }
                        } else {
                            this.alert("올바르지 않은 접근입니다.")
                            this.location.href = "/groups?page=1&type=public"
                        }
                    })
                })
            }
        })
    }
})

const banner_img = document.querySelector(".banner_img").children[0]
const title = document.querySelector(".top_txt").children[0]
const members = document.querySelector(".top_txt").children[1]
const member_list = document.querySelector(".member")
const cls_btn = document.querySelector("#close_mem_list")
const mem_ul = document.querySelector(".content_box")
const mem_ul_title = document.querySelector("#mem_ul_title")
const mem_list_invite = document.querySelector(".content_box").children[0]
const mem_list_admin_check = document.querySelector(".admin_check")

member_list.addEventListener("click", () => {
    document.querySelector(".group_list_popup").style.display = "flex"
})

cls_btn.addEventListener("click", () => {
    document.querySelector(".group_list_popup").style.display = "none"
})

/** 그룹의 글을 가져오는 함수입니다. (그룹 아이디, 페이지) 
 * morning (아침) lunch (점심) night (저녁) free (간식)
*/
function get_write(g_id, page) {
    fetch(`/api/diary/group/${g_id}/${page}`, {
        method: "GET",
        credentials: "include"
    }).then((res) => {
        if (res.status === 200) {
            res.json().then(async (data) => {
                console.log(data)
                let amount = data.total
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

                let posts = data.posts
                let p_html = "";

                const post_div = document.querySelector(".list_box");

                await posts.forEach(async (post) => {
                    console.log(post)
                    let writer = await get_user_info(post.id)
                    console.log(writer)
                    let when
                    if (post.eat_when == "morning") {
                        when = "아침"
                    } else if (post.eat_when == "lunch") {
                        when = "점심"
                    } else if (post.eat_when == "night") {
                        when = "저녁"
                    } else {
                        when = "간식"
                    }

                    let friends = JSON.parse(post.friends.replace(/'/g, '"'));
                    let images = JSON.parse(post.images.replace(/'/g, '"'));

                    console.log(images)

                    let image = "/assets/images/default-background.png"

                    if (images.length > 0) {
                        image = images[0]
                    }

                    let f_html = `<span>${writer.Nickname}</span>`;
                    var f_i = 0
                    if (friends.length > 0) {
                    friends.forEach(async (friend) => {
                        friend = await get_user_info(friend)
                        f_html = f_html + `<span>${friend.Nickname}</span>`
                        f_i++;
                        if(f_i === friends.length) {
                            let _day = post.created_at.split(" ")[0].split("-");

                            let html = `<li>
                                <a class="img_box" href="javascript:">
                                    <img alt="식단 이미지" src="${image}">
                                </a>
                                <div class="info_box">
                                    <h2 style="cursor:pointer" onclick='window.open(\"/record_my?id=${post.no}\")'>${post.title}</h2>
                                    <p class="meal">${when}</p>
                                    <p class="txt_info">${post.desc.substring(0, 130).replaceAll("\n", "")}</p>
                                    <div class="bottom">
                                        <div class="txt">
                                            ${f_html}
                                        </div>
                                        <div class="right_box">
                                            <p class="date">${_day[1]} / ${_day[2].split("T")[0]}</p>
                                            <a class="comment" href="javascript:">
                                                <i class="comment_icon"><img alt="댓글아이콘" src="/assets/images/comment-icon.svg"></i>
                                                댓글 <em>${post.comments.length}</em>개
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </li>`
        
                            post_div.insertAdjacentHTML("beforeend", html);
                            console.log("html placed")
                        }
                    })} else {
                        let _day = post.created_at.split(" ")[0].split("-");

                            let html = `<li>
                                <a class="img_box" href="javascript:">
                                    <img alt="식단 이미지" src="/assets/images/default-background.png">
                                </a>
                                <div class="info_box">
                                    <h2 style="cursor:pointer" onclick='window.open(\"/record_my?id=${post.no}\")'>${post.title}</h2>
                                    <p class="meal">${when}</p>
                                    <p class="txt_info">${post.desc.substring(0, 130).replaceAll("\n", "")}</p>
                                    <div class="bottom">
                                        <div class="txt">
                                            ${f_html}
                                        </div>
                                        <div class="right_box">
                                            <p class="date">${_day[1]} / ${_day[2].split("T")[0]}</p>
                                            <a class="comment" href="javascript:">
                                                <i class="comment_icon"><img alt="댓글아이콘" src="/assets/images/comment-icon.svg"></i>
                                                댓글 <em>${post.comments.length}</em>개
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </li>`
        
                            post_div.insertAdjacentHTML("beforeend", html);
                            console.log("html placed")
                    }
                })
            })
        }
    })
}

/** 그룹의 관리자로 임명하는 함수 (마우스 이벤트) */
function appoint(mouseevent) {
    let target = mouseevent.target
    let tar_name = target.parentElement.parentElement.children[1].innerText
    let tar_uid = target.attributes.uid.value
    let r_confirm = confirm(`정말 ${tar_name}님을 모임의 관리자로 임명하시겠습니까?`)

    if (r_confirm === true) {
        let parameters = location.href.split('?')[1].split('&');
        parameters.forEach((param) => {
            let key = param.split('=')[0];
            let value = param.split('=')[1];
            if (key === 'id') {
                let g_id = value
                fetch(`/api/group/appoint?group_id=${g_id}&user_id=${tar_uid}`, {
                    method: 'POST'
                }).then((response) => {
                    if (response.status === 200) {
                        alert(`${tar_name}님을 모임의 관리자로 임명했습니다.`);
                        location.reload();
                    }
                })
            }
        })
    }
}

/** 그룹의 관리자에서 해임하는 함수 (마우스 이벤트) */
function be_deprived(mouseevent) {
    let target = mouseevent.target
    let tar_name = target.parentElement.parentElement.children[1].innerText
    let tar_uid = target.attributes.uid.value
    let r_confirm = confirm(`정말 ${tar_name}님을 모임의 관리자직에서 해임하시겠습니까?`)

    if (r_confirm === true) {
        let parameters = location.href.split('?')[1].split('&');
        parameters.forEach((param) => {
            let key = param.split('=')[0];
            let value = param.split('=')[1];
            if (key === 'id') {
                let g_id = value
                fetch(`/api/group/be_deprived?group_id=${g_id}&user_id=${tar_uid}`, {
                    method: 'POST'
                }).then((response) => {
                    if (response.status === 200) {
                        alert(`${tar_name}님을 관리자직에서 해임했습니다.`);
                        location.reload();
                    }
                })
            }
        })
    }
}


/** 그룹의 멤버를 그룹에서 추방하는 함수 (마우스 이벤트) */
function kick(mouseevent) {
    let target = mouseevent.target
    let tar_name = target.parentElement.parentElement.children[1].innerText
    let tar_uid = target.attributes.uid.value
    let r_confirm = confirm(`정말 ${tar_name}님을 모임에서 추방하시겠습니까?`)
    if (r_confirm) {
        let parameters = location.href.split('?')[1].split('&');
        parameters.forEach((param) => {
            let key = param.split('=')[0];
            let value = param.split('=')[1];
            if (key === 'id') {
                let g_id = value
                fetch("/api/group/kick_member", {
                    method: "POST",
                    body: JSON.stringify({
                        "member_id": tar_uid,
                        "group_id": g_id
                    })
                }).then((response) => {
                    if (response.status === 200) {
                        location.reload();
                    } else {
                        response.json().then((data) => {
                            alert(data.detail)
                        })
                    }
                })
            }
        })
    }
}


/** 그룹의 세부 정보를 받아오는 함수 (그룹 아이디) */
function get_group_data(id) {
    fetch(`/api/group/detail/${id}`,{
        method: 'GET'
    }).then((res) => {
        res.json().then((group) => {
            let mem = JSON.parse(group.members.replace(/'/g, '"')).length
            let memlist = JSON.parse(group.members.replace(/'/g, '"'))
            let owner = group.owner
            let name = group.name
            let img = group.groupimg
            let no = group.id
            let ops = JSON.parse(group.operator)
            let desc = group.description
            document.getElementById("e_g_name").value = name
            document.getElementById("e_g_desc").value = desc
            document.getElementById("e_g_pf").src = img
            document.getElementById("g_info").innerHTML = desc
            mem_ul_title.innerText = "그룹 멤버 "+mem

            banner_img.src = img
            title.innerText = name
            members.innerHTML = "멤버 : "+mem+" 명 <i class=\"user_List_icon\"><object data=\"../assets/images/user-list-icon.svg\" type=\"image/svg+xml\" aria-label=\"왼쪽 화살표\"></object></i>"
            document.querySelector(".red_btn").style.display = "block"
            document.querySelector(".red_btn").href = `javascript:sessionStorage.setItem('chat_room', ${no});sessionStorage.setItem('chat_title', '${name} 모임의 채팅방');window.open('/chat', '채팅')`

            memlist.forEach(async (mem) => {
                let u_data = await get_user_info(mem)
                let nick = u_data.Nickname
                let id = u_data.ID
                let profile = u_data.profile_image || "../assets/images/default-profile.png"
                let infomsg = u_data.infomsg
                if (mem === owner) {
                    let html = `<li id="owner">
                                    <div class="img_box">
                                        <img alt="프로필이미지" src="${profile}">
                                    </div>
                                    <p class="name">${nick}</p>
                                    <span><i id="crown_icon_owner" class="crown_icon"></i>그룹장</span>
                                </li>`

                    mem_ul.insertAdjacentHTML("beforeend", html)
                } else if (ops.includes(mem)) {
                    var html
                    if (location.href.includes("detail")) {
                        html = `<li id="sub_owner">
                                        <div class="img_box">
                                            <img alt="프로필이미지" src="${profile}">
                                        </div>
                                        <p class="name">${nick}</p>
                                        <span><i id="crown_icon_sub" class="crown_icon"></i>관리자</span>
                                    </li>`
                    } else {
                        html = `<li id="sub_owner">
                                        <div class="img_box">
                                            <img alt="프로필이미지" src="${profile}">
                                        </div>
                                        <p class="name">${nick}</p>
                                        <span><i id="crown_icon_sub" class="crown_icon"></i>관리자</span>
                                        <div class="button_box">
                                            <button type="button" id="sown" uid=${id} btype="be" active>
                                                <object aria-label="왕관아이콘" data="/assets/images/crown-icon-yellow.svg"type="image/svg+xml"></object>
                                            </button>
                                            <button type="button" id="kick" uid=${id}>
                                                <object aria-label="닫기아이콘" data="/assets/images/close-icon.svg"type="image/svg+xml"></object>
                                            </button>
                                        </div>
                                    </li>`
                    }

                    mem_ul.insertAdjacentHTML("beforeend", html)
                } else {
                    var html
                    if (location.href.includes("detail")) {
                        html = `<li>
                                    <div class="img_box">
                                        <img alt="프로필이미지" src="${profile}">
                                    </div>
                                    <p class="name">${nick}</p>
                                </li>`
                    } else {
                        html = `<li>
                                    <div class="img_box">
                                        <img alt="프로필이미지" src="${profile}">
                                    </div>
                                    <p class="name">${nick}</p>
                                    <div class="button_box">
                                        <button type="button" id="nown" uid=${id} btype="be">
                                            <object aria-label="왕관아이콘" data="/assets/images/crown-icon-yellow.svg"type="image/svg+xml"></object>
                                        </button>
                                        <button type="button" id="kick" uid=${id}>
                                            <object aria-label="닫기아이콘" data="/assets/images/close-icon.svg"type="image/svg+xml"></object>
                                        </button>
                                    </div>
                                </li>`
                    }

                    mem_ul.insertAdjacentHTML("beforeend", html)
                }
                
                document.querySelectorAll("#nown").forEach((element) => {
                    element.removeEventListener("click", appoint);
                    element.addEventListener("click", appoint)
                })

                document.querySelectorAll("#sown").forEach((element) => {
                    element.removeEventListener("click", be_deprived);
                    element.addEventListener("click", be_deprived)
                })

                document.querySelectorAll("#kick").forEach((element) => {
                    element.removeEventListener("click", kick);
                    element.addEventListener("click", kick)
                })
            })

        })
    })
}

//아이디로 유저가져와서 html에 적용

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