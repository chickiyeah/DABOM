window.addEventListener('DOMContentLoaded', async function() {
    connnect()
    get_unread_amount()
    get_alerts(1)
})

var alertsocket

var page = 1

async function get_alerts(page) {
    loading.style.display = 'flex';
    await verify_token()
    let access_token = sessionStorage.getItem("access_token")
    fetch(`/api/alert/alerts?page=${page}`, {
        method: 'GET',
        headers: {
            Authorization: access_token
        }
    }).then(function(res) {
        res.json().then((json) => {
            console.log(json)
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
                    localStorage.clear();
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
                            localStorage.clear();
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
                    localStorage.clear();
                    sessionStorage.clear();
                    loading.style.display = 'none';
                    location.href = "/login"
                }else{
                    res.json().then((json) => {
                        let detail_error = json.detail;
                        reject(JSON.stringify(detail_error));
                        localStorage.clear();
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
    alertsocket = new WebSocket(`ws://localhost:8000/chat/ws?username=${user.nick}&u_id=${user.uid}&channel=Va8%r@!UQGEOkHI@O6nVpLY-5-Ul{gefAFr`)

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