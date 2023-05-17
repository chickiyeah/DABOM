"use strict";

let loginEmail = document.getElementById("login_email");
let loginPw = document.getElementById("login_pw");
let loginBtn = document.getElementById("login_btn");

// 데이터 읽기
let access_token = sessionStorage.getItem("access_token");
let refresh_token = sessionStorage.getItem("refresh_token");

let reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;
let reg_pw = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;

loginBtn.addEventListener("click", async () => { //async function() {} () => 
    await login();
})

async function login() { //메인함수가 동기상태에요. 기본으로요? ㄴㄴ 앞에다가 async 붙이면 비동기 ㅇ아부붙이면 동아 아아기기
  // 로그인
  return new Promise(async function (resolve, reject) { // 예만 비동기된거임 아하
    //정규식검사    
    console.log(loginEmail.value);
    console.log(loginPw.value);

    let email_val = loginEmail.value;
    let pw_val = loginPw.value;

    if (!loginEmail.value.match(reg_email)) {
      alert("아이디를 정확하게 입력하세요.");
      loginEmail.value = "";
      loginEmail.focus();
      console.log(0)
      reject("실패: 아이디 형식 오류");
    } else if (!loginPw.value.match(reg_pw)) {
      alert("비밀번호를 정확하게 입력하세요.");
      loginPw.value = ""; //여기에서 하는게아니라
      loginPw.focus();
      console.log(1)
      reject("실패: 비밀번호 형식 오류");
    } else {
      loginEmail.value = "";
      loginPw.value = "";
      console.log(2)
      alert("로그인 성공!");
    }

    console.log("approved");
    fetch("http://dabom.kro.kr/api/user/login", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
        // "Authorization" : sessionStorage.getItem("access_token")
      },
      body: JSON.stringify({
        "email": email_val,
        "password": pw_val,
      }),
    })
    .then(async function(data) { {}
      if (data.status == 200) {
        data.json().then(async (json) => {
              sessionStorage.setItem("access_token", json.access_token)
              sessionStorage.setItem("refresh_token", json.refresh_token)
              resolve(json);
          })
      } else if (data.status == 400 ) {
        data.json().then(async (json) => {
          let detail = json.detail;
          if (detail.code == "ER009") {
            reject( new Error("비밀번호 불일치"));
          }
        })
      }else{
        reject("SERVICE ERROR WITH UNKNOWN ERROR : " + data)
      }
    });
  });
}