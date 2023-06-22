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
            if (location.href.includes('group/add')) {
                let img = document.querySelector('.upload_img').children[0]
                img.src = h_f_link
            }
            resolve(h_f_link)
            //console.log(files)
            
        };
        xhr.send(formdata)
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
              response.json().then(async (json) => {
                loading.style.display = "none"
                resolve(json[1])
              })
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
            })
          }
        })  
      }
    }
  }