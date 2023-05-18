window.addEventListener('DOMContentLoaded', async function() {
    if (location.href.includes('chat')) {
        let room = sessionStorage.getItem("chat_room")
        try_connect(room)
        console.log("비동기 동작중.")
    }
});

import { clickEnter } from "./enterEvent.js";
const chat_input = document.querySelector('#chat_input');
const send_button = document.querySelector('#send_button');
const players = document.querySelector('#online_players');
const msg_box = document.querySelector('.msg_box');

if (location.href.includes('chat')) {
    clickEnter(chat_input, send_button);
    send_button.addEventListener('click', async (event) => {
        let room = sessionStorage.getItem("chat_room")
        send_message(chat_input.value)
    });
}

var chat
let connnect = false
var nick
var u_id

function in_out_message(nick, status) {
    let msg = `
    <div class="chat">
        <div class="text_box">
            <div class="mag_in_out">
                <div class="message">${nick}님이 ${status}했습니다.</div>
            </div>
        </div>
    </div>
    `

    return msg
}

async function try_connect(room) {
    return new Promise(async function (resolve, reject) {
        if (location.href.includes('chat')) {
            let user = await verify_token()
            u_id = user.uid
            console.log("token verified")
            if(user.nick == null) {
                location.reload();
            }else{
                nick = user.nick
            }
            if (room == null) {
                chat = new WebSocket(`ws://localhost:8000/chat/ws?username=${user.nick}&u_id=${user.uid}`) // 전역변수의 값을 바꿈   
                document.querySelector("#room_title").textContent = "로비 채널"
            } else {
                chat = new WebSocket(`ws://dabom.kro.kr/chat/ws?username=${user.nick}&u_id=${user.uid}&channel=${room}`) // 전역변수의 값을 바꿈
                document.querySelector("#room_title").textContent = room
            }

            chat.onopen = async function() { //전역변수 사용
                console.log("채팅서버 연결됨")
                connnect = true
            }

            chat.onmessage = async function(event) { //전역변수 사용
                let chatdata
                try {
                    chatdata = JSON.parse(event.data)
                } catch (e) {
                    chatdata = event.data
                }
                
                if (chatdata.username == "userupdate") {
                    let username = chatdata.message.split("님이")[0]
                    let status = chatdata.message.split(" ")[2].split("했습니다.")[0]
                    msg_box.insertAdjacentHTML("beforeend", in_out_message(username, status))
                    msg_box.scrollTop = msg_box.scrollHeight;
                    get_online_user(room)
                }


                let id = chatdata.u_id
                let nick = chatdata.nick
                let msg = chatdata.message

                var f_return

                if (msg.includes("file_message/*/")) {
                    let f_data = msg.split('/*/')[1]
                    let f_type = f_data.split('/')[0]
                    let f_type_extension = f_data.split('/')[1]
                    let f_file_extension = f_data.split('/')[2]
                    let f_name = f_data.split('/')[3]
                    let f_link = f_data.split('/_/')[1].replace("\"","")

                    if (f_type == "image") {
                        f_return = `<img class='chat_image' src="${f_link}">`
                    } else if (f_type == "video") {
                        f_return = `<video class='chat_video' src="${f_link}">`
                    } else {
                        f_return = `<div class='chat_file'><a href="${f_link}">${f_name}</a></div>`
                    }

                    let date = new Date(chatdata.time)
                    var hour = date.getHours()
                    let minute = date.getMinutes()
                    var a
                    if (hour > 12) {
                        a = "오후"
                        hour = hour - 12
                    } else if (hour < 12) {
                        a = "오전"
                    } else if (hour == 12) {
                        a = "오후"
                    }
                    let newdate = `${a} ${hour}:${minute}`
                    console.log(newdate)
                    console.log(chatdata)
                    if (chatdata.u_id != u_id) {
                        //타인 메시지
                        other_message(msg, id, newdate)
                    } else {
                        //본인 메시지
                    }

                    console.log(f_return)
                }else{
                    if (chatdata.username != "userupdate") {
                        let date = new Date(chatdata.time)
                        var hour = date.getHours()
                        let minute = date.getMinutes()
                        var a
                        if (hour > 12) {
                            a = "오후"
                            hour = hour - 12
                        } else if (hour < 12) {
                            a = "오전"
                        } else if (hour == 12) {
                            a = "오후"
                        }
                        let newdate = `${a} ${hour}:${minute}`
                        console.log(newdate)
                        console.log(chatdata)
                        if (chatdata.u_id != u_id) {
                            //타인 메시지
                            let profile = chatdata.pf_image || "../assets/images/default-profile.png"
                            let msg = `<div class="chat ch1">
                                     <div class="profile_img">
                                        <img src="${profile}" alt="프로필이미지">
                                    </div>
                                    <div class="text_box">
                                        <div class="name">${chatdata.username}</div>
                                        <div class="mag_info">
                                            <div class="mag">${chatdata.message}</div>
                                            <div class="time">${newdate}</div>
                                        </div>
                                    </div>
                                </div>`
                                        
                            msg_box.insertAdjacentHTML("beforeend", msg)
                            msg_box.scrollTop = msg_box.scrollHeight;                                    
                                
                        } else {
                            //본인 메시지
                            setTimeout(() => {
                                let msg = `<div class="chat ch2">
                                                <div class="text_box">
                                                    <div class="mag_info">
                                                        <div class="mag">${chatdata.message}</div>
                                                        <div class="time">${newdate}</div>
                                                    </div>
                                                </div>
                                            </div>`
                                
                                console.log(msg)
                                msg_box.insertAdjacentHTML("beforeend", msg)
                                msg_box.scrollTop = msg_box.scrollHeight;
                            },100)
                        }
                    }
                }
            }

            window.onbeforeunload = async function() {
                connnect = false
                chat.close()
            }
        }
    })  
}

export async function send_message(message) {
    return new Promise(async function(resolve, reject) {
        chat.send(message)
        chat_input.value = ""
        let date = new Date()
        var hour = date.getHours()
        let minute = date.getMinutes()
        var a
        if (hour > 12) {
            a = "오후"
            hour = hour - 12
        } else if (hour < 12) {
            a = "오전"
        } else if (hour == 12) {
            a = "오후"
        }
        let newdate = `${a} ${hour}:${minute}`
        //본인 메시지
        let msg = `<div class="chat ch2">
                        <div class="text_box">
                            <div class="mag_info">
                                <div class="mag">${message}</div>
                                <div class="time">${newdate}</div>
                            </div>
                        </div>
                    </div>`

        msg_box.insertAdjacentHTML("beforeend", msg)
        msg_box.scrollTop = msg_box.scrollHeight;
        resolve("메시지 전송됨")
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
             
            fetch(requrl, {
                method: 'GET',
            }).then(async function(res) {
                res.json().then(async (json) => {
                    const members = JSON.parse(json.members);
                    //접속 아이디 전송
                    get_users_info(members)
                })
            })
    })
}

function userlist(nick, image) {
    let profile =`
    <li>
        <div class="profile_img">
            <img src="${image}" alt="프로필이미지">
        </div>
        <p>${nick}</p>
    </li>
    `


    return profile
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
            if (res.status != 200) {
                reject("오류.")
            }else{
                res.json().then(async (json) => {
                    players.setHTML("")
                    json.reverse().forEach(data => {
                        let nick = data.Nickname
                        let profile = data.profile_image || "../assets/images/default-profile.png"
                        players.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    })
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
