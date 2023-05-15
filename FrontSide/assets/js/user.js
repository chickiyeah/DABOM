"use strict";

let loginId = document.getElementById("login_id");
let loginPw = document.getElementById("login_pw");
let loginBtn = document.getElementById("login_btn");

let access_token = sessionStorage.getItem("access_token")

// const loginbtn1 = document.querySelector("#login_btn")

let reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;
let reg_pw = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;

loginBtn.addEventListener("click", async () => {
    await login()
})

async function login(e) { //메인함수가 동기상태에요. 기본으로요? ㄴㄴ 앞에다가 async 붙이면 비동기 ㅇ아부붙이면 동아 아아기기
  // 로그인
  return new Promise(async function (resolve, reject) { // 예만 비동기된거임 아하
        // 정규식검사
    console.log(loginId.value)
    console.log(loginPw.value)
    if (!loginId.value.match(reg_email)) {
      alert("아이디를 정확하게 입력하세요.");
      loginId.value = "";
      loginId.focus();
      console.log(0)
    } else if (!loginPw.value.match(reg_pw)) {
      alert("비밀번호를 정확하게 입력하세요.");
      loginPw.value = "";
      loginPw.focus();
      console.log(1)
    } else {
      loginId.value = "";
      loginPw.value = "";
      console.log(2)
      alert("로그인 성공!");
    }

    console.log("approved");
    fetch("http://dabom.kro.kr/api/user/login", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        userid: loginId.value,
        userpw: loginPw.value,
      }),
    })
    .then(async function(res) {
      if (response.status == 200) {
          res.json().then(async (json) => {
              console.log("성공" + json)
              resolve(json)
          })
      } else {
        console.log(res)
        reject("error: " + res)
      }
    });
  });
}