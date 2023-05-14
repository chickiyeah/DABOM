window.addEventListener('DOMContentLoaded', async function() {
    let room = sessionStorage.getItem("chat_room")
    console.log(await try_connect(room))
});

async function decodeUnicode(unicodeString) {
	var r = /\\u([\d\w]{4})/gi;
	unicodeString = unicodeString.replace(r, function (match, grp) {
	    return String.fromCharCode(parseInt(grp, 16)); } );
	return decodeURI(unicodeString);
}

async function try_connect(room) {
    return new Promise(async function (resolve, reject) {
        user = await verify_token()
        console.log("token verified")
        const chat = new WebSocket(`ws://dabom.kro.kr/chat/ws?username=${user.nick}&u_id=${user.uid}`)
        chat.onopen = async function() {
            console.log("채팅서버 연결됨")
        }

        chat.onmessage = async function(event) {
            try {
                chatdata = JSON.parse(event.data)
            } catch (e) {
                chatdata = event.data
            }

            console.log(chatdata)
        }

        window.onbeforeunload = async function() {
            chat.close()
        }
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
                    
                    console.log(json.access_token)
                    console.log(json)
                    sessionStorage.setItem("access_token", json.access_token);
                    sessionStorage.setItem("refresh_token", json.refresh_token);
                    resolve("token refresed")
                })
            }
        })
    })
}

/*                  
    if (detail_error.code === "ER011") {
        reject( new Error("해당 유저는 존재하지 않습니다."));
    } else if (detail_error.code === "ER997") {
        reject( new Error("재로그인이 필요합니다."));
    } else if (detail_error.code === "ER998") {
        reject( new Error("재로그인이 필요합니다."));
    } else if (detail_error.code === "ER999") {
        reject( new Error("비활성화된 유저입니다. 관리자에게 문의해주세요."));
    }
*/
