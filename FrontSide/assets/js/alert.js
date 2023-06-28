window.addEventListener('DOMContentLoaded', async function() {
    connnect()
    get_unread_amount()
    get_alerts(1)
})

var alertsocket

const loading = document.querySelector(".loading");
const alert_list = document.querySelector(".bell_menu");
const bell_new_alert = document.querySelector("#bell_new_alert");

var page = 1

async function get_alerts(page) {
    await verify_token()
    loading.style.display = 'flex';
    let access_token = sessionStorage.getItem("access_token")
    fetch(`/api/alert/alerts?page=${page}`, {
        method: 'GET',
        headers: {
            Authorization: access_token
        }
    }).then(function(res) {
        res.json().then((json) => {
            json.forEach((item) => {
                if (item.read === 'False') {
                    let html = `<a class="bell_item" href="${item.url}" target="_black">
                                    <div id="new_alert" class="dabom_alert"></div>
                                    <div class="profile_img">
                                        <img alt="프로필이미지" src="${item.profile_image}">
                                    </div>
                                    <div class="txt_box">
                                        <p>${item.title}</p>
                                        <p>${item.msg}</p>
                                    </div>
                                </a>`
                    alert_list.insertAdjacentHTML('beforeend', html);
                } else {
                    let html = `<a class="bell_item" href="${item.url}" target="_black">
                                    <div class="dabom_alert"></div>
                                    <div class="profile_img">
                                        <img alt="프로필이미지" src="${item.profile_image}">
                                    </div>
                                    <div class="txt_box">
                                        <p>${item.title}</p>
                                        <p>${item.msg}</p>
                                    </div>
                                </a>`
                    alert_list.insertAdjacentHTML('beforeend', html);
                }
            })
            loading.style.display = 'none';
        })
    })
}

async function get_unread_amount() {
    await verify_token()
    let access_token = sessionStorage.getItem("access_token")
    fetch("/api/alert/u_amount", {
        method: 'GET',
        headers: {
            Authorization: access_token
        }
    }).then(function(res) {
        res.json().then((json) => {
            let amount = json.amount
            if (amount > 0) {
                bell_new_alert.style.display = 'block'
            }
        })
    })
}

async function verify_token() {
    return new Promise(async function(resolve, reject) {
        //토큰 검증
        fetch("/api/user/cookie/verify",{
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        }).then(async function(response) {
            if (response.status !== 200) {
                if (response.status === 422) {                   
                    await LoadCookie();
                    loading.style.display = 'none';
                }else if (response.status === 307) {
                    location.href = "/login";
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        console.log(detail_error)
                        if (detail_error.code == "ER998") {
                          await LoadCookie();
                        }
                        if (detail_error.code === "ER013") {
                            await LoadCookie();
                        }
                    });
                }
            } else {
                fetch("/api/user/cookie/get_info",{ methon: 'GET', credentials: "include" }).then(async (res) => {if (res.status === 200) { res.json().then(async (json) => {loading.style.display = "none";resolve(json)})}})
            }
        })
    })
  }

  async function LoadCookie(){
    let lo_access_token = localStorage.getItem("access_token")
    let lo_refresh_token = localStorage.getItem("refresh_token")
    if (location.href.includes("login") == false && location.href.includes("register") == false) {
      if(lo_access_token == null || lo_refresh_token == null) {
        console.log("here?")
        localStorage.clear()
        location.href = "/login";
      }else{
        fetch(`/api/user/cookie/autologin?access_token=${lo_access_token}&refresh_token=${lo_refresh_token}`, {method: 'GET'}).then((res) => {
            if (res.status === 200) {
                if (res.url.includes('login')) {
                    location.href = "/login";
                }
                console.log("자동로그인 및 토큰 검증 성공.")
                loading.style.display = 'none';
                location.reload()
              } else {
                res.json().then((data) => {
                  let detail = data.detail
                  if (detail.code === "ER015") {
                    localStorage.clear();
                    location.href = "/login";
                  }

                  if (detail.code === "ER013") {
                    localStorage.clear();
                    location.href = "/login";
                  }
                })
              }
        })  
      }
    }
  }
  
//알림 채널명 : Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr
async function connnect() {
    let user = await verify_token()
    console.log(user[0])
    let us_id = user[0].ID
    console.log("token verified")
    let u_nick = user[0].Nickname
    alertsocket = new WebSocket(`ws://dabom.kro.kr/chat/ws?username=${u_nick}&u_id=${us_id}&channel=Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr`)

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
            loading.style.display = 'none';
        }
    }
}

export async function get_me() {
    return new Promise(async function(resolve, reject) {fetch("/api/user/cookie/get_info", {method: "GET"}).then((res) => {res.json().then((data) => {resolve(data[0])});})})
}

/** 알림 전송 ( 알림 종류, 목표의 유저 아이디, 알림을 클릭하면 이동할 링크, 메시지(선택) ) */
export async function send_alert(type, tar_id, url) {
    let user = await get_user_info(tar_id);
    let sender = await get_me()
    console.log(sender)
    let nick = sender.Nickname
    console.log(nick)
    let id = user.ID
    let profile_image = user.profile_image || "../assets/images/default-profile.png"
    let alerts = ['friend_request', 'guild_invite']

    if (alerts.includes(type) === true) {
        var msg
        var title
        if (type === "friend_request") {
            msg = `${nick} 님으로부터 친구요청이 도착했습니다!`
            title = "친구요청이 도착했습니다."
        }

        if (type === "guild_invite") {
            msg = `${nick} 님으로부터 모임초대가 도착했습니다!`
            title = "모임초대가 도착했습니다."
        }

        msg = `alert/*/${type}/*/${id}/*/${profile_image}/*/${url}/*/${title}/*/${msg}`
        console.log(msg)
        alertsocket.send(msg)
        console.log("알림 전송됨")
    }else{
        console.log("알림 타입 포함 오류")
        throw new Error("알수 없는 알림 타입입니다. 타입을 확인하세요.")
    }
} 


/** 단일 유저정보 조회 (유저 아이디 ) */
async function get_user_info(user) {
    return new Promise((resolve, reject) => {
        fetch(`/api/user/email/user_id?email=${user}`,{method: 'GET'}).then((res) => (res.json().then((data) => {
            let url = `/api/user/get_user?id=${data}`;
            fetch(url, {
                headers: {
                    Authorization: "Bearer cncztSAt9m4JYA9"
                }
            }).then((res) => {
                if (res.status != 200) {
                    reject("오류.")
                }else{
                    res.json().then(async (json) => {
                        let u_data = json[0];
                        console.log(u_data);
                        resolve(u_data)
                    });
                };
            })
        })));     
    });
}