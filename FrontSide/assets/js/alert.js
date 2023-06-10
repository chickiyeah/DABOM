window.addEventListener('DOMContentLoaded', async function() {
    connnect()
    get_unread_amount()
    get_alerts(1)
})

var alertsocket

const loading = document.querySelector(".loading");

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
                console.log(item)
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
            console.log(json.amount)
        })
    })
}

async function LoadCookie(){
    let cookie = document.cookie
    let lo_access_token = localStorage.getItem("access_token")
    let lo_refresh_token = localStorage.getItem("refresh_token")
    let access_token = sessionStorage.getItem('access_token');
    let refresh_token = sessionStorage.getItem('refresh_token');
    if (location.href.includes("login") == false && location.href.includes("register") == false) {
    if (access_token == null || refresh_token == null) {
      if(lo_access_token == null || lo_refresh_token == null) {
        console.log("here?")
        localStorage.clear()
        location.href = "/login";
      }else{
        /*let cookies = cookie.split(";");
        //let keys = [];
        //cookies.forEach(cookie => {
        //  let key = cookie.split("=")[0];
        //  keys.push(key);
        //})
        //console.log(keys)
        if((keys.includes("access_token") && keys.includes("refresh_token")) || (keys.includes(" access_token") && keys.includes(" refresh_token"))){
          cookies.forEach(async (cookie) => {
            let key = cookie.split("=")[0];
            if(key == "access_token" || key == " access_token") {
              sessionStorage.setItem("access_token", lo_access_token);
              let access = sessionStorage.getItem("access_token")
            }

            if(key == "refresh_token" || key == " refresh_token") {
              sessionStorage.setItem("refresh_token", lo_refresh_token);
            }
            
            await verify_token()
            console.log("자동로그인 및 토큰 검증 성공.")
            loading.style.display = 'none';
            location.reload()
          })
        }else{
          document.cookie = "access_token = ; expires=Thu, 01 Jan 1970 00:00:01 GMT;"
          document.cookie = "refresh_token = ; expires=Thu, 01 Jan 1970 00:00:01 GMT;"
          location.href = "/login";
        }*/

        sessionStorage.setItem("refresh_token", lo_refresh_token);
        sessionStorage.setItem("access_token", lo_access_token);
        console.log(sessionStorage.getItem("refresh_token"));
        console.log(sessionStorage.getItem("access_token"));
        await verify_token()
            console.log("자동로그인 및 토큰 검증 성공.")
            loading.style.display = 'none';
            location.reload()
      }
    }else{
      location.href = "/login";
    }
  }}


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
                    await LoadCookie();
                    loading.style.display = 'none';
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        if (detail_error.code == "ER998") {
                            console.log(refresh_token_fun())
                            resolve(refresh_token_fun())
                           
                        }else{
                            reject(JSON.stringify(detail_error))
                            //localStorage.clear();
                            sessionStorage.clear();
                            loading.style.display = 'none';
                            location.href = "/login"
                        }
                    });
                }
            } else {
                loading.style.display = "none"
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

//알림 채널명 : Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr
async function connnect() {
    let user = await verify_token()
    alertsocket = new WebSocket(`ws://dabom.kro.kr/chat/ws?username=${user.nick}&u_id=${user.uid}&channel=Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr`)

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
            if (typeof(alert) == "string") {
                alert = JSON.parse(alert)
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

/** 알림 전송 ( 알림 종류, 목표의 유저 아이디, 알림을 클릭하면 이동할 링크, 메시지(선택) ) */
export async function send_alert(type, tar_id, url) {
    let user = await get_user_info(tar_id);
    console.log(user);
    let nick = user.Nickname
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
        let url = `/api/user/get_user?id=${user}`;
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
    });
}