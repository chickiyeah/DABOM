"use strict";

// 로그인
const loginEmail = document.querySelector("#login_email");
const loginPw = document.querySelector("#login_pw");
// let loginPwre = document.getElementById("login_pwre"); //이걸
const loginPwre = document.querySelector("#login_pwre"); //요로코롬 아이디는 # 클래스는 . 
const loginVal = document.querySelector('#login_val');

// 회원가입
const joinName = document.querySelector("#join_name");
const joinGender = document.querySelector("#join_gender");
const joinTail = document.querySelector("#join_tail");
const joinWeight = document.querySelector("#join_weight");
const joinBir = document.querySelector("#join_bir");

// 데이터 읽기
let access_token = sessionStorage.getItem("access_token");
let refresh_token = sessionStorage.getItem("refresh_token");

// 정규식 검사
const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;
const reg_pw = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;
const reg_pwre = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;


// 로그인
if (location.href.includes("login")) {
  const loginBtn = document.getElementById("login_btn");
  loginBtn.addEventListener("click", async () => { //async function() {} () => 
      await login();
  });
}

if (location.href.includes("register")) {
    const joinBtn = document.querySelector("#join_btn");
    joinBtn.addEventListener("click", async () => { //async function() {} () => 
      await join();
    })
}

  // 로그인
async function login() { //메인함수가 동기상태에요. 기본으로요? ㄴㄴ 앞에다가 async 붙이면 비동기 ㅇ아부붙이면 동아 아아기기
  return new Promise(async function (resolve, reject) { // 예만 비동기된거임 아하

    var email_val
    var pw_val
    if (!loginEmail.value.match(reg_email)) {
      alert("아이디를 정확하게 입력하세요.");
      loginEmail.value = "";
      loginEmail.focus();
      reject("실패: 아이디 형식 오류");
    } else if (!loginPw.value.match(reg_pw)) {
      alert("비밀번호를 정확하게 입력하세요.");
      loginPw.value = ""; //여기에서 하는게아니라
      loginPw.focus();
      reject("실패: 비밀번호 형식 오류");
    } else {
      email_val = loginEmail.value
      pw_val = loginPw.value
      loginEmail.value = "";
      loginPw.value = "";
    }
    document.querySelector(".loading").style.display = 'flex';
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
              console.log(json);
              document.querySelector(".loading").style.display = 'none';
              location.href = "/"
          })
      } else if (data.status == 400 ) {
        data.json().then(async (json) => {
          let detail = json.detail;
          // console.log(detail);
          loginVal.innerHTML = '';
          if (detail.code == "ER008") {
            reject( new Error("아이디의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다."));
            loginVal.insertAdjacentHTML('afterbegin', '<p>아이디의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.</p>' );
          }else if(detail.code == "ER009"){
            reject( new Error("비밀번호 불일치"));
            loginVal.insertAdjacentHTML('afterbegin', '<p>비밀번호 불일치</p>' );
          }else if(detail.code == "ER012"){
            reject( new Error("이메일 인증이 필요합니다"));
            loginVal.insertAdjacentHTML('afterbegin', '<p>이메일 인증이 필요합니다</p>' );
          }else if(detail.code == "ER040"){
            reject( new Error("너무 많은 시도가 있었습니다. 나중에 시도해주세요."));
            loginVal.insertAdjacentHTML('afterbegin', '');
            loginVal.insertAdjacentHTML('afterbegin', '<p>너무 많은 시도가 있었습니다. 나중에 시도해주세요.</p>');
          }else{ //여기서 뭐하심? 27줄보세유!
            reject("정의되지 않은 오류입니다");
            alert("정의되지 않은 오류입니다");
          }
        });
        // loginVal.remove();
      }else{
        reject("SERVICE ERROR WITH UNKNOWN ERROR : " + data)
      }
    });
  });
}


// 회원가입
async function join() { 
  return new Promise(async function (resolve, reject) { // 예만 비동기된거임 아하
    if (!loginEmail.value.match(reg_email)) {
      alert("아이디를 정확하게 입력하세요.");
      loginEmail.value = "";
      loginEmail.focus();
      reject("실패: 아이디 형식 오류");
    } else if (!loginPw.value.match(reg_pw)) {
      alert("비밀번호를 정확하게 입력하세요.");
      loginPw.value = "";
      loginPw.focus();
      reject("실패: 비밀번호 형식 오류");
    }else if(!loginPwre.value.match(reg_pwre)){
      alert("비밀번호를 확인을 정확하게 입력하세요.");
      loginPwre.value = ""; 
      loginPwre.focus();
      reject("실패: 비밀번호 형식 오류");
    } else {
      loginEmail.value = "";
      loginPw.value = "";
      loginPwre.value = "";
    }
    fetch("http://dabom.kro.kr/api/user/login", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
        // "Authorization" : sessionStorage.getItem("access_token")
      },
      body: JSON.stringify({
        "email": email_val,
        "password": pw_val,
        "nickname": pw_valre,
        "gender": gender,
        "birthday": birthday,
        "height": height,
        "weight": weight,
      }),
    })
  });
}
