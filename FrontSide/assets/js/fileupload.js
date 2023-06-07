const inputElement = document.getElementById("input").addEventListener("change", handleFiles)
const loading = document.querySelector(".loading");

import { send_message } from './chat.js'

async function handleFiles() {
    const filelist = this.files
    const loading = document.querySelector(".loading");
    loading.style.display = 'flex';
    var files = []
    await verify_token()
    for (let i = 0, numFiles = filelist.length; i < numFiles; i++) {
        let file = filelist[i]
        let formdata = new FormData()
        formdata.append('image', file)
        let extentsion = file.name
        let url = await makeRequest(extentsion, file, formdata)
        files.push(url)
    }
    console.log(files)
    loading.style.display = 'none';
    sessionStorage.setItem("da_u_files", files)
    if (location.href.includes("diary_add")) {
        location.href = "/diary_update"
    }
}

function makeRequest(extentsion, file, formdata) {
    return new Promise(function(resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.open('POST', `/chat/uploadfile?ext=${extentsion}`, true)
        let access_token = sessionStorage.getItem("access_token")
        xhr.setRequestHeader('Authorization', access_token)
        xhr.onload = xhr.onerror = async function () {
            let link = xhr.responseText.replace("\"","")
            if (location.href.includes('register')) {
                if (file.type.indexOf('image') < 0) {
                    alert('프로필은 사진만 허용됩니다.')
                    loading.style.display = 'none';
                    return new Error('프로필은 사진만 허용됩니다.')
                }
            }

            //채팅 구역
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
                loading.style.display = 'none';
            }
            let image = `<img src="${xhr.responseText}">`
            console.log(image)
            
            
            let h_f_link = link.replace('\"',"") // 여기가 단일 파일의 다운로드 링크(URL)
            console.log(h_f_link)
            // 단일 다운로드 링크(URL) 을 files 변수의 리스트에 추가한다.
            resolve(h_f_link)
            //console.log(files)
            
        };
        xhr.send(formdata)
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