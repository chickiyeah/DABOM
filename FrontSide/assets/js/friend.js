window.addEventListener('DOMContentLoaded', async function() {
    if(this.location.href.includes('friend')){
        if(location.href.includes('?')){
            let param = this.location.href.split('?')[1];
            let params = param.split('&');
            var keys = [];
            params.forEach(async (data) => {       
                let key = data.split('=')[0]
                let value = data.split('=')[1]
                keys.push(key)
                if (key == "page") {
                    if (!isNaN(value)) {
                        if (value < 1) {
                            location.href = "/friend?page=1"
                        }else{
                            await list(value)
                        }
                    } else {
                        this.location.href = "/friend?page=1"
                    }
                }
            })

            if (!keys.includes("page")){
                this.location.href = "/friend?page=1"
            }
        }else{
            this.location.href = "/friend?page=1"
        }
    }
})

import { clickEnter } from "./enterEvent.js";
import { send_alert } from "./alert.js";

const loading = document.querySelector(".loading");
const pagediv = document.querySelector(".numdiv");
const friend_list_div = document.querySelector(".friends");

const friend_req_input = document.querySelector("#friend_req_input");
const friend_req_button = document.querySelector("#friend_req_button");

const error = document.querySelector("#error");
const success = document.querySelector("#success");

const delete_ban = document.querySelector(".friend_box .top .btn");

const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;

clickEnter(friend_req_input, friend_req_button)

friend_req_button.addEventListener("click", async (event) => {
    if (!friend_req_input.value.match(reg_email)) {
        friend_req_input.focus();
        try {document.querySelector("#detail_msg").remove()} catch {}
        try {document.querySelector("#success_msg").remove()} catch {}
        error.insertAdjacentHTML('afterbegin', '<p id="detail_msg">이메일을 확인해주세요.</p>' );
        reject(new Error("이메일 형식 오류"));
    }else{
        request(friend_req_input.value)
    }
})

function checkbox_event(pointerevent) {
    let target = pointerevent.target
    console.log("체크박스 이벤트"+target.id);
    console.log(target.id)
    if (target.checked == true) {
        Array.prototype.forEach.call(friend_list_div.children,(element) => {
            let s_checkbox = element.children[0].children[0]
            if (s_checkbox.id != target.id) {
                s_checkbox.checked = false
            }
        })

        Array.prototype.forEach.call(delete_ban.children, (element) => {
            if (element.innerText == '차단') {
                element.style.backgroundColor = "white"
                element.style.color = "black"
                element.removeEventListener("click", ban_friend);
                element.addEventListener("click", ban_friend);
            }

            if (element.innerText == "삭제") {
                element.style.backgroundColor = "white"
                element.style.color = "black"
                element.removeEventListener("click", rm_friend);
                element.addEventListener("click", rm_friend);
            }
        });
    } else  {
        Array.prototype.forEach.call(delete_ban.children, (element) => {
            if (element.innerText == '차단') {
                element.style.backgroundColor = ""
                element.style.color = ""
                element.removeEventListener("click", ban_friend)
            }

            if (element.innerText == "삭제") {
                element.style.backgroundColor = ""
                element.style.color = ""
                element.removeEventListener("click", rm_friend)
            }
        });
    }
}

function apply_event() {
    Array.prototype.forEach.call(friend_list_div.children,(element) =>{
        element.children[0].children[0].removeEventListener("click", checkbox_event);
        element.children[0].children[0].addEventListener("click", checkbox_event)})
}

async function request(uid) {
    return new Promise(async function(resolve, reject) {
        loading.style.display = "flex"
        let user_data = await verify_token()
        let access_token = sessionStorage.getItem("access_token")
        fetch(`/api/friends/request?uid=${uid}`,{
            method: 'POST',
            headers: {
                Authorization: access_token
            }
        }).then(async function(res) {
            if (res.status !== 200) {
                res.json().then(async (json) => {
                    let detail_error = json.detail;
                    if (detail_error.code == "ER029") {
                        friend_req_input.focus();
                        try {document.querySelector("#detail_msg").remove()} catch {}
                        try {document.querySelector("#success_msg").remove()} catch {}
                        error.insertAdjacentHTML('afterbegin', '<p id="detail_msg">해당 유저와 이미 친구관계입니다.</p>' );
                        reject(new Error("해당 유저와 이미 친구입니다."))
                        loading.style.display = "none"
                    }

                    if (detail_error.code == "ER027") {
                        friend_req_input.focus();
                        try {document.querySelector("#detail_msg").remove()} catch {}
                        try {document.querySelector("#success_msg").remove()} catch {}
                        error.insertAdjacentHTML('afterbegin', '<p id="detail_msg">인증키에 저장된 정보와 상이힙니다.</p>' );
                        reject(new Error("인증키에 저장된 정보와 상이합니다."))
                        loading.style.display = "none"
                    }

                    if (detail_error.code == "ER041") {
                        friend_req_input.focus();
                        try {document.querySelector("#detail_msg").remove()} catch {}
                        try {document.querySelector("#success_msg").remove()} catch {}
                        error.insertAdjacentHTML('afterbegin', '<p id="detail_msg">자기 자신에게 친구요청을 할순 없습니다.</p>' );
                        reject(new Error("본인에게 친구요청을 할순 없습니다"))
                        loading.style.display = "none"
                    }

                    if (detail_error.code == "ER011") {
                        friend_req_input.focus();
                        try {document.querySelector("#detail_msg").remove()} catch {}
                        try {document.querySelector("#success_msg").remove()} catch {}
                        error.insertAdjacentHTML('afterbegin', '<p id="detail_msg">해당 이메일의 유저는 존재하지 않습니다.</p>' );
                        reject(new Error("존재하지 않는 유저입니다."))
                        loading.style.display = "none"
                    }
                })
            }else{
                try {document.querySelector("#detail_msg").remove()} catch {}
                try {document.querySelector("#success_msg").remove()} catch {}
                friend_req_input.value = ""
                console.log(user_data)
                res.json().then(async (json) => {
                    send_alert('friend_request', user_data.uid, json)
                })
                success.insertAdjacentHTML('afterbegin', '<p id="success_msg">친구요청을 전송했습니다.</p>' );
                resolve("친구요청을 전송했습니다.")
                loading.style.display = "none"
            }
        })
    })
}

async function ban_friend(pointerevent) {
    return new Promise(async function(resolve, reject) {
        var checked = false
        var tar_id
        Array.prototype.forEach.call(friend_list_div.children,(element) => {
            let s_checkbox = element.children[0].children[0]
            if (s_checkbox.checked == true) {
                checked = true
                tar_id = s_checkbox.id.split('-')[1];
            }
        })

        if (checked == true) {
            await verify_token()
            let access_token = sessionStorage.getItem("access_token")
            fetch(`/api/friends/ban?user_id=${tar_id}`, {
                method: "POST",
                headers: {
                    Authorization: access_token
                }
            }).then(async (res) => {
                if (res.status !== 200) {
                    res.json().then(async (json) => {
                        let detail_error = json.detail;
                        if(detail_error.code == "ER037") {
                            reject(new Error("이미 차단된 유저입니다."))
                        }
                    })
                }else{
                    alert("친구를 차단했습니다.")
                    resolve("친구를 차단했습니다.")
                    location.reload()
                }
            })
        } else {
            alert("먼저 친구를 선택해주세요.")
        }
    })
}

async function pardon_friend(pointerevent) {
    return new Promise(async function(resolve, reject) {
        let tar_id = pointerevent.target.id.split('-')[1];
        await verify_token()
        let access_token = sessionStorage.getItem("access_token")
        fetch(`/api/friends/ban?user_id=${tar_id}`, {
            method: "POST",
            headers: {
                Authorization: access_token
            }
        }).then(async (res) => {
            if (res.status !== 200) {
                res.json().then(async (json) => {
                    let detail_error = json.detail;
                    if(detail_error.code == "ER038") {
                        reject(new Error("이미 차단되지 않은 유저입니다."))
                    }
                })
            }else{
                alert("유저를 차단헤제 했습니다")
                resolve("유저를 차단헤제 했습니다.")
            }
        })
    })
}

async function rm_friend(pointerevent) {
    return new Promise(async function(resolve, reject) {
        var checked = false
        var delid
        Array.prototype.forEach.call(friend_list_div.children,(element) => {
            let s_checkbox = element.children[0].children[0]
            if (s_checkbox.checked == true) {
                checked = true
                delid = s_checkbox.id.split('-')[1];
            }
        })
        
        if (checked == true) {
            await verify_token()
            let access_token = sessionStorage.getItem("access_token")
            fetch(`/api/friends/remove?delid=${delid}`,{
                method: "DELETE",
                headers: {
                    Authorization: access_token
                }
            }).then(async (res) => {
                if (res.status !== 200) {
                    res.json().then(async (json) => {
                        let detail_error = json.detail;
                        if (detail_error.code == "ER030") {
                            reject(new Error("친구 관계가 아닙니다."))
                        }
                    })
                }else{
                    alert("친구를 삭제했습니다.")
                    resolve("친구를 삭제했습니다.")
                    location.reload()
                }
            })
        } else {
            alert("먼저 친구를 선택해주세요.")
        }
    })
}

function goto(obj) {
    console.log(obj)
}

async function list(page) {
    return new Promise(async function(resolve, reject) {
        loading.style.display = "flex"
        await verify_token()
        let access_token = sessionStorage.getItem("access_token")
        fetch(`/api/friends/list?page=${page}`,{
            method: "GET",
            headers: {
                Authorization: access_token
            }
        }).then(async function(res) {
            if (res.status !== 200) {
                res.json().then(async (json) => {
                    let detail = json.detail
                    if (detail.code == "ER042") {
                        resolve([])
                        loading.style.display = "none"
                    }
                })
            }else{
                res.json().then(async (json) => {
                    console.log(json)
                    let amount = json.amount
                    document.querySelector("#friend_amount").innerText = `친구 (${amount} 명)`
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
                    document.querySelector(".prev").href = `javascript:location.href='/friend?page=${page-1}'`
                    document.querySelector(".next").href = `javascript:location.href='/friend?page=${page+1}'`

                    if (page > maxpage) {
                        location.href = "/friend?page="+maxpage
                    }else{
                        for (let i = startpage; i < maxpage+1; i++) {
                            if (i == page) {
                                pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:location.href='/friend?page=${i}'">${i}</a>`)
                            }else{
                                pagediv.insertAdjacentHTML("beforeend", `<a class="num" href="javascript:location.href='/friend?page=${i}'">${i}</a>`)
                            }
                        }
                    }

                    json.friends.forEach(data => {
                        get_user_info(data.ID, data.message)
                    })
                    loading.style.display = "none"
                    resolve(res)
                })
            }
        })
    })
}

//아이디로 유저가져와서 html에 적용
async function get_user_info(user, imsg) {
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
                    console.log(u_data)
                    let nick = u_data.Nickname
                    let id = u_data.ID
                    let profile = u_data.profile_image || "../assets/images/default-profile.png"
                    let infomsg = u_data.infomsg
                    //players.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    //players_m.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    
                    let html = `<li>
                        <div class="checkbox">
                            <input type="checkbox" id="check-${id}">
                            <label for="check-${id}">
                                <span class="profile_img">
                                    <img src="${profile}" alt="프로필이미지">
                            </span>
                            </label>
                        </div>
                        <div class="txt_box">
                            <p class="name">${nick} <em class="data">(${imsg})</em></p>
                        </div>
                        <a href="javascript:">식단보기</a>
                    </li>`

                    friend_list_div.insertAdjacentHTML("beforeend", html)
                    apply_event()
                })
            }
        })
    })
}

async function verify_token() {
    return new Promise(async function(resolve, reject) {
        //토큰 검증
        let access_token = sessionStorage.getItem("access_token")
        fetch("/api/user/verify_token",{
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                access_token: access_token
            })     
        }).then(async function(response) {
            if (response.status !== 200) {
                if (response.status === 422) {
                    reject(new Error( "{\"code\": \"ER013\", \"message\": \"로그인이 필요합니다.\"}"))
                    //localStorage.clear();
                    sessionStorage.clear();
                    loading.style.display = 'none';
                    location.href = "/login"
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        if (detail_error.code == "ER998") {
                            resolve(refresh_token())
                        }else{
                            reject(JSON.stringify(detail_error));
                            //localStorage.clear();
                            sessionStorage.clear();
                            loading.style.display = 'none';
                            location.href = "/login"
                        }
                    });
                }
            } else {
                resolve(response.json())
            }
        })
    })
}

async function refresh_token() {
    return new Promise(async function(resolve, reject) {
        let refresh_token = sessionStorage.getItem('refresh_token');
        fetch("/api/user/refresh_token", {
            method: "post",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              refresh_token: refresh_token,
            })
        })
        .then((res) => {
            if (res.status !== 200) {
                if (res.status === 422) {
                    reject(new Error("로그인이 필요합니다."))
                    //localStorage.clear();
                    sessionStorage.clear();
                    loading.style.display = 'none';
                    location.href = "/login"
                }else{
                    res.json().then((json) => {
                        let detail_error = json.detail;
                        reject(JSON.stringify(detail_error));
                        //localStorage.clear();
                        sessionStorage.clear();
                        loading.style.display = 'none';
                        location.href = "/login"
                    });
                }
            }else{
                res.json().then((json) => {
                    sessionStorage.setItem("access_token", json.access_token);
                    sessionStorage.setItem("refresh_token", json.refresh_token);
                    resolve("token refresed")
                })
            }
        })
    })
} 