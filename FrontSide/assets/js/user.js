"use strict";

import { toast } from "./toast.js";

window.addEventListener('DOMContentLoaded', async function () {
    if (this.location.href.includes("login") || this.location.href.includes("register") || this.location.href.includes("findaccount")){
      document.querySelector(".loading").style.display = "none"
      if (this.location.href.includes("login")) {
        if (this.location.href.includes("?")) {
          let r = this.location.href.split("?")[1]
          if (r === "t=r") {
            toast("인증 이메일이 발송되었으니 확인해주세요!")
          }
        }
      }
    }else{loading.style.display = "flex";verify_token();}
});

// 로그인
const loginEmail = document.querySelector("#login_email");
const loginPw = document.querySelector("#login_pw");
// let loginPwre = document.getElementById("login_pwre"); //이걸
const loginPwre = document.querySelector("#login_pwre"); //요로코롬 아이디는 # 클래스는 . 
const loginVal = document.querySelector('#login_val');
// const loginSave = document.querySelector('#save');

const loading = document.querySelector(".loading");

// 회원가입
const joinName = document.querySelector("#join_name");
const joinGender = document.querySelector("#join_gender");
const joinTail = document.querySelector("#join_tail");
const joinWeight = document.querySelector("#join_weight");
const joinBirmon = document.querySelector("#join_bir_mon");
const joinBirday = document.querySelector("#join_bir_day");
const joinBircol = document.querySelector("#join_bir_col");

const male_radio = document.querySelector("#male_radio");
const female_radio = document.querySelector("#female_radio");
const private_radio = document.querySelector("#private_radio");

const rstpw_button = document.querySelector("#rstpw_submit");
const rstpw_email = document.querySelector("#rstpw_email");



if (location.href.includes("findaccount")) {
  rstpw_button.addEventListener("click", (event) => {
    event.preventDefault();
    rstpw()
  })

  rstpw_email.addEventListener("keydown", function (e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      rstpw()
    }
  });
}

if (location.href.includes("register")) {
  male_radio.addEventListener("click", (e) => {
    e.preventDefault()
    male_radio.children[0].checked = true
    joinGender.attributes.value.value = "male"
    console.log("남성 클릭 감지")
  })

  female_radio.addEventListener("click", (e) => {
    e.preventDefault()
    female_radio.children[0].checked = true
    joinGender.attributes.value.value = "female"
    console.log("여성 클릭 감지")
  })

  private_radio.addEventListener("click", (e) => {
    e.preventDefault()
    private_radio.children[0].checked = true
    joinGender.attributes.value.value = "private"
    console.log("비공개 클릭 감지")
  })
}

// 데이터 읽기
let access_token = sessionStorage.getItem("access_token");
let refresh_token = sessionStorage.getItem("refresh_token");

// 정규식 검사
const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;
const reg_pw = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;
const reg_pwre = /(?=.*\d)(?=.*[a-zA-ZS]).{8,}/;
const reg_korean = /^[ㄱ-ㅎ|가-힣]+$/;
const reg_num = /^[0-9]+$/; 

// 라이도버튼 체크 해제
var ele = document.getElementsByName('colors'); 
const reg_radio = ele;
var count = ele.length; // 라디오버튼 길이
console.log('라디오버튼 갯수 ', count); // "라디오버튼 갯수 ", 4 출력

for(var i=0; i < ele.length; i++) {
	if(ele[i].checked === true) { // checked 속성이 true 와 같은지 비교합니다.
  	console.log(ele[i].value); //blue 만 출력합니다.
  }
}


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

if (location.href.includes("findaccount")) {
  const find_email = document.querySelector('#find_email');

  find_email.addEventListener("click", async () => { //async function() {} () => 
    await findaccount();
    })
  }

  function is_checked() {
    const loginSave = document.querySelector('#save');
    const is_checked = loginSave.checked;
    return is_checked
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

              if (detail.code === "ER013") {
                localStorage.clear();
                location.href = "/login";
              }
            })
          }
        })  
      }
    }
  }


async function cookieSave(json) {
     if (is_checked()) {
        fetch("/api/user/cookie/get_all", {method: "GET"}).then((res) => {
          res.json().then((data) => {
            console.log(data)
            localStorage.setItem("access_token", data.access_token)
            localStorage.setItem("refresh_token", data.refresh_token);
          })
        })
    }
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
            response.json().then(async (json) => {
              loading.style.display = "none"
              resolve(json[1])
            })
          }
      })
  })
}

  // 로그인
async function login() { //메인함수가 동기상태에요. 기본으로요? ㄴㄴ 앞에다가 async 붙이면 비동기 ㅇ아부붙이면 동아 아아기기
  return new Promise(async function (resolve, reject) { // 예만 비동기된거임 아하
    var email_val
    var pw_val
    if (!loginEmail.value.match(reg_email)) {
      alert("이메일을 정확하게 입력하세요.");
      loginEmail.value = "";
      loginEmail.focus();
      reject("실패: 이메일 형식 오류");
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
    fetch("/api/user/login", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
        "Authorization" : sessionStorage.getItem("access_token")
      },
      body: JSON.stringify({
        "email": email_val,
        "password": pw_val,
      }),
    })
    .then(async function(data) { {}
      if (data.status == 200) {
        data.json().then(async (json) => {
            //sessionStorage.setItem("access_token", json.access_token)
            //sessionStorage.setItem("refresh_token", json.refresh_token)
            //여기에 두면되죠 조건문 너어서
            await cookieSave(json)
            console.log(json);
            document.querySelector(".loading").style.display = 'none';
            resolve(json);
            location.href = "/"
          })
      } else if (data.status == 400 ) {
        data.json().then(async (json) => {
          let detail = json.detail;
          // console.log(detail);
          loginVal.innerHTML = '';
          if (detail.code == "ER008") {
            reject( new Error("이메일의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다."));
            loginVal.insertAdjacentHTML('afterbegin', '<p>이메일의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.</p>' );
            document.querySelector(".loading").style.display = 'none';
          }else if(detail.code == "ER009"){
            reject( new Error("비밀번호 불일치"));
            loginVal.insertAdjacentHTML('afterbegin', '<p>비밀번호 불일치</p>' );
            document.querySelector(".loading").style.display = 'none';
          }else if(detail.code == "ER012"){
            reject( new Error("이메일 인증이 필요합니다"));
            loginVal.insertAdjacentHTML('afterbegin', '<p>이메일 인증이 필요합니다</p>' );
            document.querySelector(".loading").style.display = 'none';
          }else if(detail.code == "ER040"){
            reject( new Error("너무 많은 시도가 있었습니다. 나중에 시도해주세요."));
            loginVal.insertAdjacentHTML('afterbegin', '');
            loginVal.insertAdjacentHTML('afterbegin', '<p>너무 많은 시도가 있었습니다. 나중에 시도해주세요.</p>');
            document.querySelector(".loading").style.display = 'none';
          }else{
            reject("정의되지 않은 오류입니다");
            alert("정의되지 않은 오류입니다");
            document.querySelector(".loading").style.display = 'none';
          }
        });
      } else if (data.status == 422) {
        toast("이메일 혹은 비밀번호가 입력되지 않았습니다.")
        document.querySelector(".loading").style.display = 'none';
      }else{
        reject("SERVICE ERROR WITH UNKNOWN ERROR : " + data)
      }
    });
  });
}





// 아이디, 비밀번호 찾기 탭 on 처리
const tab_id = document.querySelector('#tab_id');
const tab_pw = document.querySelector('#tab_pw');

const tab_id_val = document.querySelector('.find_id');
const tab_pw_val = document.querySelector('.find_pw');

if (document.location.href.includes("findaccount")) {
  tab_id.addEventListener('click', () =>{
    tab_id.classList.add("on");
    tab_id_val.classList.add("on");
    tab_pw_val.classList.remove('on');
    tab_pw.classList.remove('on');
  });

  tab_pw.addEventListener('click', () =>{
    tab_pw.classList.add("on");
    tab_pw_val.classList.add("on");
    tab_id_val.classList.remove('on');
    tab_id.classList.remove('on');
  });
}



// 회원가입
async function join() { 
  return new Promise(async function (resolve, reject) { 
    var email_val
    var pw_val
    var pwre_val
    var name_val
    var gender_val
    var tail_val
    var weight_val
    var bir_mon_val
    var bir_col_val
    var bir_day_val

    if (!loginEmail.value.match(reg_email)) {
      alert("이메일을 정확하게 입력하세요.");
      loginEmail.value = "";
      loginEmail.focus();
      reject("실패: 이메일 형식 오류");
    } else if (!loginPw.value.match(reg_pw)) {
      alert("비밀번호를 정확하게 입력하세요.");
      loginPw.value = "";
      loginPw.focus();
      reject("실패: 비밀번호 형식 오류");
    }else if(!loginPwre.value.match(reg_pwre)){
      alert("비밀번호를 확인을 정확하게 입력하세요.");
      loginPwre.value = ""; 
      loginPwre.focus();
      reject("실패: 비밀번호확인 형식 오류");
    }else if(!joinName.value.match(reg_korean)){
      alert("이름을 정확하게 입력하세요.");
      joinName.value = ""; 
      joinName.focus();
      reject("실패: 이름 형식 오류");
    // }else if(!joinTail.value.match(reg_num)){
    //   alert("키를 정확하게 입력하세요.");
    //   joinTail.value = ""; 
    //   joinTail.focus();
    //   reject("실패: 키 형식 오류");
    // }else if(!joinWeight.value.match(reg_num)){
    //   alert("몸무게를 정확하게 입력하세요.");
    //   joinWeight.value = ""; 
    //   joinWeight.focus();
    //   reject("실패: 몸무게 형식 오류");
    }else if(!joinBirmon.value.match(reg_num)){
      alert("생년월일을 정확하게 입력하세요.");
      joinBirmon.value = ""; 
      joinBirmon.focus();
      reject("실패: 생년월일 형식 오류");
    }else if(joinBircol.options[joinBircol.selectedIndex].value  == ''){
      alert("생년월일을 정확하게 입력하세요.");
      joinBircol.focus();
      reject("실패: 생년월일 형식 오류");
    }else if(!joinBirday.value.match(reg_num)){
      alert("생년월일을 정확하게 입력하세요.");
      joinBirday.value = ""; 
      joinBirday.focus();
      reject("실패: 생년월일 형식 오류");
    }else if(loginPw.value !== loginPwre.value){
      alert("비밀번호가 일치 하지 않습니다.");
      loginPw.value = ""; 
      loginPw.focus();
      loginPwre.value = ""; 
      loginPwre.focus();
      reject("실패: 비밀번호와 비밀번호 확인 불일치");
    }else {
      email_val = loginEmail.value;
      pw_val = loginPw.value;
      pwre_val = loginPwre.value;
      name_val = joinName.value;
      gender_val = joinGender.attributes.value.value;
      tail_val = joinTail.value;
      weight_val = joinWeight.value;
      bir_mon_val = joinBirmon.value;
      bir_col_val = joinBircol.value;
      bir_day_val = joinBirday.value;

      loginPw.value="";
      loginPwre.value="";
      joinName.value="";
      joinGender.attributes.value.value = ""
      joinTail.value="";
      joinWeight.value="";
      joinBirmon.value = "";
      joinBircol.value = "";
      joinBirday.value = "";
    }
    loading.style.display = 'flex';
    fetch("http://dabom.kro.kr/api/user/register", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
        // "Authorization" : sessionStorage.getItem("access_token")
      },
      body: JSON.stringify({
        "email": email_val,
        "password": pw_val,
        "nickname": name_val,
        "gender": gender_val,
        "birthday": `${bir_mon_val}/${bir_col_val}/${bir_day_val}`,
        "height": tail_val,
        "weight": weight_val,
        "profile_image": h_f_link
      }),
    })
    .then(async (res) => {
      if (res.status == 201) {
        location.href = "/login?t=r"
      }else{
        res.json().then(async (json) => {
          let detail = json.detail
          if (detail.code == "ER010") {
            alert("이미 사용중인 이메일입니다. 다른 이메일을 사용해주세요.")
            loading.style.display = 'none';
          }

          if (detail.code == "ER020") {
            alert("성별 선택 오류입니다. 성별을 다시 선택해주세요.")
            loading.style.display = 'none';
          }
        })
      }
    })
    .catch(reject);
  });
}


// 아이디 찾기
async function findaccount(){
  return new Promise(async function (resolve, reject) {

  var bir_mon_val
  var bir_col_val
  var bir_day_val

  if(!joinBirmon.value.match(reg_num)){
    alert("생년월일을 정확하게 입력하세요.");
    joinBirmon.value = ""; 
    joinBirmon.focus();
    reject("실패: 생년월일 형식 오류");
  }else if(joinBircol.options[joinBircol.selectedIndex].value  == ''){
    alert("생년월일을 정확하게 입력하세요.");
    joinBircol.focus();
    reject("실패: 생년월일 형식 오류");
  }else if(!joinBirday.value.match(reg_num)){
    alert("생년월일을 정확하게 입력하세요.");
    joinBirday.value = ""; 
    joinBirday.focus();
    reject("실패: 생년월일 형식 오류");
  }else {
    bir_mon_val = joinBirmon.value;
    bir_col_val = joinBircol.value;
    bir_day_val = joinBirday.value;
    joinBirmon.value = "";
    joinBircol.value = "";
    joinBirday.value = "";
  }
  document.querySelector(".loading").style.display = 'flex';
fetch("http://dabom.kro.kr/api/user/findid?birthday="+`${bir_mon_val}/${bir_col_val}/${bir_day_val}`, {
  method: "POST", 
  headers: {
    "Content-Type": "application/json",
  }
})
.then(async function(data) { {}
      if (data.status == 200) {
        data.json().then(async (json) => {
            document.querySelector("#r_id_amount").innerText = "검색된 아이디의 갯수 " + json.amount + "개"
            document.querySelector('.tab_menu').remove()
            document.querySelector('.find_id').remove()
            document.querySelector('.find_pw').remove()
            
            const id_ul = document.querySelector("#r_ids")
            json.data.forEach(element => {
              console.log(element)
              id_ul.insertAdjacentHTML("beforeend", `<li>${element.email}</li>`)
            });
              console.log(json);
              document.querySelector('.res_find_id').style.display = "flex"
              document.querySelector(".loading").style.display = 'none';
              resolve(json);
          })
      } else if (data.status == 400 ) {
        data.json().then(async (json) => {
          let detail = json.detail;
          // console.log(detail);
          loginVal.innerHTML = '';
          if (detail.code == "ER039") {
            reject( new Error("생일이 올바르지 않습니다."));
            loginVal.insertAdjacentHTML('afterbegin', '<p>이메일의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.</p>' );
            document.querySelector(".loading").style.display = 'none';
          }else{
            reject("정의되지 않은 오류입니다");
            alert("정의되지 않은 오류입니다");
            document.querySelector(".loading").style.display = 'none';
          }
        });
        // loginVal.remove();
      }else{
        reject("SERVICE ERROR WITH UNKNOWN ERROR : " + data)
      }
    });
  });
}

async function rstpw() {
  let val = rstpw_email.value
  if (!rstpw_email.value.match(reg_email)) {
    alert("이메일을 정확하게 입력하세요.");
    rstpw_email.value = "";
    rstpw_email.focus();
    reject("실패: 이메일 형식 오류");
  }else{
    loading.style.display = "flex"
    fetch("/api/user/resetpw", {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify({
        "email":val
      })
    }).then(function(response) {
      if (response.status == 200) {
        alert("비밀번호 재설정 이메일을 전송했습니다.")
        location.href = "/login"
      }else{
        response.json().then(async (json) => {
          let detail = json.detail;
          if (detail.code == "ER008") {
            alert("이메일이 올바르지 않습니다.");
            loading.style.display = "none"
          }

          if (detail.code == "ER011") {
            alert("해당 이메일의 유저는 존재하지 않습니다.");
            loading.style.display = "none"
          }
        })
      }
    })
  }
}