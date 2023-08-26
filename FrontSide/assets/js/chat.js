window.addEventListener('DOMContentLoaded', function() {
    if (location.href.includes('chat')) {
        let room = sessionStorage.getItem("chat_room")
        toast("로딩중입니다.")
        try_connect(room)
        get_online_user(room)
        console.log("비동기 동작중.")
    }
});

import { clickEnter } from "./enterEvent.js";
import { toast } from "./toast.js";
const chat_input = document.querySelector('#chat_input');
const send_button = document.querySelector('#send_button');
const players = document.querySelector('#online_players');
const players_m = document.querySelector('#online_players_m');
const msg_box = document.querySelector('.msg_box');
const inner = document.querySelector(".inner")

const drag_drop = document.querySelector(".file_drag_drop")
const loading = document.querySelector(".loading_box");

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

function isValid(data){
		
    //파일인지 유효성 검사
    if(data.types.indexOf('Files') < 0)
        return false;
    
    //이미지인지 유효성 검사
    /* if(data.files[0].type.indexOf('image') < 0){
        alert('이미지 파일만 업로드 가능합니다.');
        return false;
    }*/
    
    //파일의 개수는 1개씩만 가능하도록 유효성 검사
    if(data.files.length > 1){
        alert('파일은 하나씩 전송이 가능합니다.');
        return false;
    }
    
    //파일의 사이즈는 50MB 미만
    /*if(data.files[0].size >= 1024 * 1024 * 50){
        alert('50MB 이상인 파일은 업로드할 수 없습니다.');
        return false;
    }*/
    
    return true;
}
if (location.href.includes('chat')) {
inner.addEventListener('dragenter', function(e) {
    e.preventDefault();
    //console.log('dragenter');
    drag_drop.style.display = 'flex';

    //this.style.backgroundColor = 'green';
});

drag_drop.addEventListener('dragover', function(e) {
    e.preventDefault();
    console.log('dragover');
});

drag_drop.addEventListener('dragleave', function(e) {
    //console.log('dragleave');
    drag_drop.style.display = 'none';

    //this.style.backgroundColor = 'rgba(244,59,0 ,0.1 )';
});

drag_drop.addEventListener('drop', async function(e) {
    e.preventDefault();
    drag_drop.style.display = 'none';
    loading.style.display = 'flex';
    //console.log('drop');
    //this.style.backgroundColor = 'rgba(244,59,0 ,0.1 )';

    const data = e.dataTransfer;

    if(!isValid(data)) return;
    const formdata = new FormData();
    let file = data.files[0]
    let extentsion = file.name
    formdata.append('image', file)
        let xhr = new XMLHttpRequest();
        xhr.open('POST', `/chat/uploadfile?ext=${extentsion}`, true)

    let access_token = sessionStorage.getItem("access_token")
    xhr.setRequestHeader('Authorization', access_token)
    xhr.onload = xhr.onerror = async function () {
        let link = xhr.responseText.replace("\"","")
        if (location.href.includes('chat')) {
            var count = file.name.split('.').length - 1
            let extentsion = file.name.split('.')[count]
            let type = file.type
            var msg
            if(type == '') {
                if(extentsion == undefined){
                    msg = "file_message/*/no_type/no_file_extension/no_custom_extension/"+file.name+"/_/"+link
                } else {
                    msg = "file_message/*/no_type/no_file_extension/"+extentsion+"/"+file.name+"/_/"+link
                }
            } else {
                msg = "file_message/*/"+type+"/"+extentsion+"/"+file.name+"/_/"+link
            }

            send_message(msg)
        }
        let image = `<img src="${xhr.responseText}">`
        console.log(image)
        
        console.log(link)
        loading.style.display = 'none';

    };
    xhr.send(formdata)  
});
}
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
            loading.style.display = 'flex';
            let user = await verify_token()
            console.log(user[0])
            let us_id = user[0].ID
            console.log("token verified")
            let u_nick = user[0].Nickname
            if (room == null) {
                console.log(`wss://dabom.kro.kr/chat/ws?username=${u_nick}&u_id=${us_id}`)
                chat = new WebSocket(`wss://dabom.kro.kr/chat/ws?username=${u_nick}&u_id=${us_id}`) // 전역변수의 값을 바꿈   
                document.querySelector("#room_title").textContent = "로비 채널"
                document.querySelector("#room_title_m").textContent = "로비 채널"
            } else {
                chat = new WebSocket(`wss://dabom.kro.kr/chat/ws?username=${u_nick}&u_id=${us_id}&channel=${room}`) // 전역변수의 값을 바꿈
                let c_title = sessionStorage.getItem("chat_title")
                document.querySelector("#room_title").textContent = c_title 
                document.querySelector("#room_title_m").textContent = c_title
            }

            chat.onerror = async () => {
                console.error("웹소켓 연결실패 새로고침으로 문제 해결을 시도합니다.")
                location.reload()
            }

            chat.onopen = async function() { //전역변수 사용
                console.log("채팅서버 연결됨")
                connnect = true
                loading.style.display = 'none';
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
                    var f_return
                    if (f_type == "image") {
                        f_return = `<img class='image' src="${f_link}">`
                    } else if (f_type == "video" || f_type == "audio") {
                        f_return = `<video class='chat_video' src="${f_link}" alt="${f_name}" controls>`
                    } else {
                        f_return = `<div class='chat_file'><a href="${f_link}" target='_blank'>${f_name}</a></div>`
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

                    if (minute < 10) {
                        minute = "0"+minute
                    }
                    let newdate = `${a} ${hour}:${minute}`
                    console.log(newdate)
                    console.log(chatdata)
                    if (chatdata.u_id != u_id) {
                        let msg = `<div class="chat ch1">
                            <div class="profile_img">
                                <img src="../assets/images/default-profile.png" alt="프로필이미지">
                            </div>
                            <div class="text_box">
                                <div class="name">${chatdata.username}</div>
                                <div class="mag_info">
                                    <div class="chat_image">
                                        ${f_return}
                                    </div>
                                    <div class="time">${newdate}</div>
                                </div>
                            </div>
                        </div>`

                        msg_box.insertAdjacentHTML("beforeend", msg)
                        msg_box.scrollTop = msg_box.scrollHeight;  
                        //타인 메시지
                        
                    } else {
                        //본인 메시지
                        let msg = `<div class="chat ch2">
                            <div class="text_box">
                                <div class="mag_info">
                                    <div class="chat_image">
                                    ${f_return}
                                </div>
                                    <div class="time">${newdate}</div>
                                </div>
                            </div>
                        </div>`

                        msg_box.insertAdjacentHTML("beforeend", msg)
                        msg_box.scrollTop = msg_box.scrollHeight;  
                    }

                    console.log(f_return)
                }else{
                    if (msg.includes("youtube.com") || msg.includes("youtu.be")){
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
                        
                        var ytcode
                        if (msg.includes("youtu.be")) {
                            ytcode = msg.split("youtu.be/")[1].split("&")[0]
                        } else if (msg.includes("youtube.com/embed")) {
                            ytcode = msg.split("youtube.com/embed/")[1].split("&")[0]
                        } else if (msg.includes("youtube.com/shorts/")){
                            ytcode = msg.split("youtube.com/shorts/")[1].split("&")[0]
                        } else if (msg.includes("youtube.com")) {
                            try {
                                ytcode = msg.split("v=")[1].split("&")[0]
                            } catch (e) {
                                new Error("Invalid YouTube URL")
                            }
                        }

                        let yt_ht = `<iframe width="300" height="170" src="https://www.youtube.com/embed/${ytcode}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`
                        if (chatdata.u_id != u_id) {
                            let msg = `<div class="chat ch1">
                                <div class="profile_img">
                                    <img src="../assets/images/default-profile.png" alt="프로필이미지">
                                </div>
                                <div class="text_box">
                                    <div class="name">${chatdata.username}</div>
                                    <div class="mag_info">
                                        <div class="chat_video">
                                            ${yt_ht}
                                        </div>
                                        <div class="time">${newdate}</div>
                                    </div>
                                </div>
                            </div>`  
                            
                            msg_box.insertAdjacentHTML("beforeend", msg)
                            msg_box.scrollTop = msg_box.scrollHeight; 
                        }else{
                            let msg = `<div class="chat ch2">
                            <div class="text_box">
                                <div class="mag_info">
                                    <div class="chat_image">
                                    ${yt_ht}
                                </div>
                                    <div class="time">${newdate}</div>
                                </div>
                            </div>
                        </div>`

                            msg_box.insertAdjacentHTML("beforeend", msg)
                            msg_box.scrollTop = msg_box.scrollHeight; 
                        }

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
            }
            
            window.onunload = async function(event) {
                connnect = false
                chat.close();
            }

            window.onbeforeunload = async function(event) {
                
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

        if (minute < 10) {
            minute = "0"+minute
        }
        let newdate = `${a} ${hour}:${minute}`
        //본인 메시지
        if (message.includes("file_message/*/")) {
            let f_data = message.split('/*/')[1]
            let f_type = f_data.split('/')[0]
            let f_type_extension = f_data.split('/')[1]
            let f_file_extension = f_data.split('/')[2]
            let f_name = f_data.split('/')[3]
            let f_link = f_data.split('/_/')[1].replace("\"","")

            var f_return

            if (f_type == "image") {
                f_return = `<img class='image' src="${f_link}">`
            } else if (f_type == "video" || f_type == "audio") {
                f_return = `<video class='chat_video' src="${f_link}"  alt="${f_name}" controls>`
            } else {
                f_return = `<div class='chat_file'><a href="${f_link}" download='${f_name}' target='_blank'>${f_name}</a></div>`
            }

                //본인 메시지
                let msg = `<div class="chat ch2">
                    <div class="text_box">
                        <div class="mag_info">
                            <div class="chat_image">
                            ${f_return}
                        </div>
                            <div class="time">${newdate}</div>
                        </div>
                    </div>
                </div>`

                msg_box.insertAdjacentHTML("beforeend", msg)
                msg_box.scrollTop = msg_box.scrollHeight;  

            console.log(f_return)
        }else{
            if (message.includes("youtube.com") || message.includes("youtu.be")){
                
                var ytcode
                if (message.includes("youtu.be")) {
                    ytcode = message.split("youtu.be/")[1].split("&")[0]
                } else if (message.includes("youtube.com/embed")) {
                    ytcode = message.split("youtube.com/embed/")[1].split("&")[0]
                } else if (message.includes("youtube.com/shorts/")){
                    ytcode = message.split("youtube.com/shorts/")[1].split("&")[0]
                } else if (message.includes("youtube.com")) {
                    try {
                        ytcode = message.split("v=")[1].split("&")[0]
                    } catch (e) {
                        new Error("Invalid YouTube URL")
                    }
                }

                let yt_ht = `<iframe width="300" height="170" src="https://www.youtube.com/embed/${ytcode}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`
            
                let msg = `<div class="chat ch2">
                    <div class="text_box">
                        <div class="mag_info">
                            <div class="chat_image">
                            ${yt_ht}
                        </div>
                            <div class="time">${newdate}</div>
                        </div>
                    </div>
                </div>`

                msg_box.insertAdjacentHTML("beforeend", msg)
                msg_box.scrollTop = msg_box.scrollHeight;
            }else{
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
            }
        }
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
                res.json().then((json) => {
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
                    players.innerHTML = ""
                    players_m.innerHTML = ""  
                    json.reverse().forEach(data => {
                        let nick = data.Nickname
                        let profile = data.profile_image || "../assets/images/default-profile.png"
                        players.insertAdjacentHTML("beforeend", userlist(nick, profile))
                        players_m.insertAdjacentHTML("beforeend", userlist(nick, profile))
                    })
                })
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
        if(lo_access_token == null || lo_refresh_token == null || lo_access_token.length < 12 || lo_refresh_token.length < 12) {
        console.log("here?")
        localStorage.clear()
        location.href = "/login";
      }else{
        fetch(`/api/user/cookie/autologin?access_token=${lo_access_token}&refresh_token=${lo_refresh_token}`, {method: 'GET'}).then((res) => {
            if (res.status === 200) {
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

                  if (detail.code === "ER011") {
                    localStorage.clear();
                    location.href = "/login";
                  }
                })
              }
        })  
      }
    }
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
