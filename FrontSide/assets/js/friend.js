async function request(target_mail) {
    await verify_token()
    let access_token = sessionStorage.getItem("access_token")
    fetch(`/api/friends/request?email=${email}`)
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
                    //$(".loading").hide()
                    //location.href = "/login"
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        if (detail_error.code == "ER998") {
                            resolve(refresh_token())
                        }else{
                            reject(JSON.stringify(detail_error));
                            localStorage.clear();
                            sessionStorage.clear();
                            $(".loading").hide()
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
                    //sessionStorage.clear();
                    //$(".loading").hide()
                    //location.href = "/login"
                }else{
                    res.json().then((json) => {
                        let detail_error = json.detail;
                        reject(JSON.stringify(detail_error));
                        //localStorage.clear();
                        //sessionStorage.clear();
                        //$(".loading").hide()
                        //location.href = "/login"
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