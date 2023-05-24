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
const joinBirmon = document.querySelector("#join_bir_mon");
const joinBirday = document.querySelector("#join_bir_day");
const joinBircol = document.querySelector("#join_bir_col");

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
          }else{ //여기서 뭐하심? 27줄보세유!
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


// 회원가입
async function join() { 

  return new Promise(async function (resolve, reject) { // 로그인은 다했을걸요?s]오키욤
    var email_val
    var pw_val
    var name_val
    var gender_val
    var tail_val
    var weight_val
    var bir_val

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
    }else if(!joinTail.value.match(reg_num)){
      alert("키를 정확하게 입력하세요.");
      joinTail.value = ""; 
      joinTail.focus();
      reject("실패: 키 형식 오류");
    }else if(!joinWeight.value.match(reg_num)){
      alert("몸무게를 정확하게 입력하세요.");
      joinWeight.value = ""; 
      joinWeight.focus();
      reject("실패: 몸무게 형식 오류");
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
      gender_val = joinGender.value;
      tail_val = joinTail.value;
      weight_val = joinWeight.value;
      bir_mon_val = joinBirmon.value;
      bir_col_val = joinBircol.value;
      bir_day_val = joinBirday.value;

      loginPw.value="";
      loginPwre.value="";
      joinName.value="";
      joinGender.value="";
      joinTail.value="";
      joinWeight.value="";
      joinBirmon.value = "";
      joinBircol.value = "";
      joinBirday.value = "";
    }

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
        "profie_image": h_f_link
      }),
    })
  });
}

// 아이디, 비밀번호 찾기 탭 on 처리
const tab_id = document.querySelector('#tab_id');
const tab_pw = document.querySelector('#tab_pw');

const tab_id_val = document.querySelector('.find_id');
const tab_pw_val = document.querySelector('.find_pw');

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

fetch("http://dabom.kro.kr/api/user/findid", {
  method: "POST", 
  headers: {
    "Content-Type": "application/json",
    // "Authorization" : sessionStorage.getItem("access_token")
  },
  body: JSON.stringify({
    "birthday": `${bir_mon_val}/${bir_col_val}/${bir_day_val}`,
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
          if (detail.code == "ER039") {
            reject( new Error("생일이 올바르지 않습니다."));
            loginVal.insertAdjacentHTML('afterbegin', '<p>이메일의 입력값이 이메일이 아니거나, 이메일이 유효하지 않습니다.</p>' );
            document.querySelector(".loading").style.display = 'none';
          }else{ //여기서 뭐하심? 27줄보세유!ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ
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