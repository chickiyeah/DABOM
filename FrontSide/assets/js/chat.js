window.addEventListener('DOMContentLoaded', async function() {
    let room = sessionStorage.getItem("chat_room")
    try_connect(room)
    get_online_user(room)
    console.log("비동기 동작중.")
});

import { clickEnter } from "./enterEvent.js";

const chat_input = document.querySelector('#chat_input');
const send_button = document.querySelector('#send_button');

clickEnter(chat_input, send_button);
send_button.addEventListener('click', async (event) => {
    let room = sessionStorage.getItem("chat_room")
    console.log("inhere")
    send_message(chat_input.value)
});


var chat
let connnect = false
var nick

async function try_connect(room) {
    return new Promise(async function (resolve, reject) {
        let user = await verify_token()
        console.log("token verified")
        if(user.nick == null) {
            location.reload();
        }else{
            nick = user.nick
        }
        if (room == null) {
            chat = new WebSocket(`ws://localhost:8000/chat/ws?username=${user.nick}&u_id=${user.uid}`)          
        } else {
            chat = new WebSocket(`ws://dabom.kro.kr/chat/ws?username=${user.nick}&u_id=${user.uid}&channel=${room}`)
        }

        chat.onopen = async function() {
            console.log("채팅서버 연결됨")
            connnect = true
        }

        chat.onmessage = async function(event) {
            let chatdata
            try {
                chatdata = JSON.parse(event.data)
            } catch (e) {
                chatdata = event.data
            }
            
            if (chatdata.username == "userupdate") {
                get_online_user(room)
            }
            console.log(chatdata)
        }

        window.onbeforeunload = async function() {
            connnect = false
            chat.close()
        }
    })  
}

export async function send_message(message) {
    return new Promise(async function(resolve, reject) {
        chat.send(message)
        resolve("메시지 전송됨")
        let send_data = ({"username":nick,"message":message})
        console.log(send_data)
    })
}


async function get_online_user(room) {
    return new Promise(async function(resolve, reject) {
        let requrl = ""
        if (room == null) {
            requrl = `/chat/members?group=lobby`
        }else{
            requrl = `/chat/members?group=${room}`
        }

        setTimeout(() => {               
            fetch(requrl, {
                method: 'GET',
            }).then(async function(res) {
                res.json().then(async (json) => {
                    const members = JSON.parse(json.members);
                    //접속 아이디 전송
                    get_users_info(members)
                })
            })
        }, 2000);
    })
}

//아이디로 유저가져와서 html에 적용
async function get_users_info(users) {
    return new Promise((resolve, reject) => {
        let url = `/api/user/get_users?id=${JSON.stringify(users)}`
        fetch(url, {
            headers: {
                Authorization: "Bearer cncztSAt9m4JYA9"
            }
        }).then((res) => {
            console.log(res.status)
            if (res.status != 200) {
                reject("오류.")
            }else{
                res.json().then(async (json) => {
                    console.log(json)
                    resolve(json)
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
                    //$(".loading").hide()
                    //location.href = "/login"
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        if (detail_error.code == "ER998") {
                            console.log(refresh_token())
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

async function post_example(value) {
    return new Promise(async function (resolve, reject) {
        fetch(requrl, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                access_token: access_token
            })             
        }).then(async function(res) {

            if (response.status !== 200) {
                res.json().then(async (json) => {
                    console.log(json)
                    resolve(json)
                })
            } else {
                reject("error: " + res)
            }
        })
    })
}