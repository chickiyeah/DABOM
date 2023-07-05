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
                            if (this.location.href.includes("detail")) {
                                mem_list_invite.remove()
                                mem_list_admin_check.remove()
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

function get_group_data(id) {
    fetch(`/api/group/detail/${id}`,{
        method: 'GET'
    }).then((res) => {
        res.json().then((group) => {
            let mem = JSON.parse(group.members).length
            let memlist = JSON.parse(group.members)
            let owner = group.owner
            let name = group.name
            let img = group.groupimg
            let no = group.id
            let ops = JSON.parse(group.operator)
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
                                            <button type="button" uid=${id}>
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
                                        <button type="button" uid=${id}>
                                            <object aria-label="닫기아이콘" data="/assets/images/close-icon.svg"type="image/svg+xml"></object>
                                        </button>
                                    </div>
                                </li>`
                    }

                    mem_ul.insertAdjacentHTML("beforeend", html)
                }
            })
        })
    })
}

//아이디로 유저가져와서 html에 적용
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