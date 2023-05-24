window.addEventListener('DOMContentLoaded', async function() {
    if(location.href.includes('friend')){
        console.log(await list(1))

    }
})

const loading = document.querySelector(".loading");

async function request(uid) {
    return new Promise(async function(resolve, reject) {
        await verify_token()
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
                        reject(new Error("해당 유저와 이미 친구입니다."))
                    }

                    if (detail_error.code == "ER027") {
                        reject(new Error("인증키에 저장된 정보와 상이합니다."))
                    }

                    if (detail_error.code == "ER041") {
                        reject(new Error("본인에게 친구요청을 할순 없습니다"))
                    }
                })
            }else{
                resolve("친구요청을 전송했습니다.")
            }
        })
    })
}

async function ban_friend(tar_id) {
    return new Promise(async function(resolve, reject) {
        await verify_token()
        let access_token = sessionStorage.getItem("access_token")
        fetch(`/api/friends/ban?user_id=${tar_id}`, {
            method: "POST",
            headers: {
                Authorization: access_token
            }
        })
    })
}

async function rm_friend(delid) {
    return new Promise(async function(resolve, reject) {
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
                resolve("친구를 삭제했습니다.")
                location.reload()
            }
        })
    })
}

async function list(page) {
    return new Promise(async function(resolve, reject) {
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
                    }
                })
            }else{
                res.json().then(async (json) => {
                    console.log(json)
                    json.forEach(data => {
                        get_user_info(data.ID, data.message)
                    })
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
                    let nick = json.Nickname
                    let profile = json.profile_image || "../assets/images/default-profile.png"
                    //players.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    //players_m.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    json[0].infomsg = imsg
                    //data = json[0]

                    console.log(json[0])
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