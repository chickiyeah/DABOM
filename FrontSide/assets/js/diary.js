"use strict";

const images = sessionStorage.getItem("da_u_files"); //세션 스토리지에서 da_u_files의 키값을 가진 값(value)를 가져와라.


const imgBox = document.querySelector('.img_box'); // 고정 요소는 최대한 const로 
const imgItem = document.querySelector('.img_item');
const closeBtn = document.querySelector('.close_btn');
const buttons = document.querySelectorAll('#eat_when');

const searchFood = document.querySelector("#searchInput");
const sendFood = document.querySelector("#send");
const itemappend = document.querySelector(".search_info");
const kcalBox = document.querySelector("#kcalBox");

const loading = document.querySelector(".loading");

const close_f_btn = document.querySelector("#close_friend_list")
const open_f_btn = document.querySelector("#d_f_open")
const friend_back = document.querySelector(".friend_list_back")

var beforex = -1

function getToday(){
  const h_week = document.querySelector(".date");
  const week = ['일', '월', '화', '수', '목', '금', '토']
  var date = new Date();
  var year = date.getFullYear();
  var month = ("0" + (1 + date.getMonth())).slice(-2);
  var day = ("0" + date.getDate()).slice(-2);

  h_week.innerText = year + "년 " + month + "월 " + day +"일 " + week[date.getDay()]+"요일";
}

window.addEventListener('DOMContentLoaded', function() {
  getToday()
  
  if (this.location.href.includes('diary_update')) {
    init();
    const desc = document.querySelector(".content_box")
    fetch('/api/friends/all', {
      method: 'GET'
    }).then((res) => {
      res.json().then((data) => {
        data.friends.forEach((value) => {
          let html = `<li>
                        <div class="img_box">
                          <img alt="프로필이미지" src="${value.profile_image}">
                        </div>
                        <p class="name">${value.Nickname}</p>
                        <div class="button_box">
                        <input style="width:20px" type="checkbox" id="check-${value.ID}">
                          <label for="check-${value.ID}">
                          </label>
                        </div>
                    </li>`
          desc.insertAdjacentHTML("beforeend", html)
        })
      })
    })

    open_f_btn.addEventListener('click', function(e) {
      e.preventDefault()
      friend_back.style.display = "flex"
    })
    
    close_f_btn.addEventListener('click', function(e) {
      e.preventDefault()
      close_f_btn.parentElement.parentElement.style.display='none'
      s_friends = [];
      let f_html = close_f_btn.parentElement.children[2]
      Array.prototype.forEach.call(f_html.children, (element) => {
        console.log(element)
        let check = element.children[2].children[0]
        let uid = check.id.replace("check-","")
    
        if (check.checked) {
          s_friends.push(uid)
        }
      })
    })

    imgItem.addEventListener('dragover', function(e) {
      let onx = e.clientX
      var curx = document.querySelector('.img_item').scrollLeft
      if (beforex != -1) {
        if (beforex < onx) {
          //console.log('going right');
          document.querySelector('.img_item').scrollLeft = curx - 30
        }

        if (beforex == onx) {
          //console.log('staying')
        }

        if (beforex > onx) {
          //console.log('going left');
          document.querySelector('.img_item').scrollLeft = curx + 30
        }
      }
      beforex = onx;
    })
  }
})

//image -> (image) 여는 괄호는 어디로가썽요 임마박스는 뭐에요 date_item?? 아뇨 imgBox 가 왜 imaBox가 됬어요 앜ㅋ 오타.. ㅋㅋㅋㅋㅋ
function init() {
  console.log("init progressing")
  console.log(images)
  if (images != null) {
    let imglist = images.split(",");
    let img_data = imglist[0];
    // let imgId = img_data.ID;
    var num = 1;
    let imgId = img_data + num++;
    console.log(imgId);
    console.log(imglist)
    imglist.forEach((image) => {
      //imgBox.appendChild(image);
      console.log(image);
      if (image != null) {
        let html = ` <li id="img-${imgId}">
                      <div class="img_box"> 
                        <img src="${image}" alt="이미지">
                        <a class="close_btn" id="${imgId}" href="javascript:">
                          <object data="/assets/images/close-icon.svg" type="image/svg+xml"
                                  aria-label="닫기아이콘"></object>
                        </a>
                      </div>
                    </li>
                    `
                    imgItem.insertAdjacentHTML("afterbegin", html); // 땡 해당 스트링은 투입 위치를 지정하는것임 ( beforestart 요소가 위로 올라감 , afterstart 요소가 올라가지만 beforestart보다는 아래 , beforeend 요소가 아래로감 , afterend beforeend보다 더 아래로감 틀을 벗어날수잇음 )           
        }
        
    });
    remove_event()
  }
}

  // pointerevent는 이벤트 핸들러 함수, 마우스 이벤트, 터치 이벤트
  function closeevent(pointerevent) {
    console.log(1);
    // 해당 클릭이 발생한 HTML 요소
    let target = pointerevent.target;
    console.log(target.id);
    console.log(target.parentElement);
    console.log(target.parentElement.parentElement);
    if(confirm('정말 삭제하시겠어요?')){
      target.parentElement.parentElement.remove();
    }
  }

  function remove_event() {
    Array.prototype.forEach.call(imgItem.children,(element) =>{
      if (!element.children[0].classList.contains('img_upload')) {
        element.children[0].children[1].removeEventListener("click", closeevent);
        element.children[0].children[1].addEventListener("click", closeevent)
      }
    }) 
  }



// 버튼 선택하기
buttons.forEach(function(button) {
  button.addEventListener('click', function(event) {
    event.preventDefault(); // 기본 동작 (페이지 이동) 방지

          // 모든 버튼의 'on' 클래스 제거
          buttons.forEach(function(btn) {
            btn.classList.remove('on');
          });
    // 클릭한 버튼에 'on' 클래스 추가
    button.classList.add('on');
  });
});



// 음식 검색
const apiUrlor = 'http://localhost:8000/api/food/search/or';
const apiUrland = 'http://localhost:8000/api/food/search/and';
const progress_h = document.querySelector('#i_progress');
const h_search_count = document.querySelector('.search_count');
const h_search_count_num = document.querySelector('.search_count_num');
const kc_h_submit = document.querySelector("#kc_h_submit");

import { toast } from './toast.js';

kc_h_submit.addEventListener("click", (event) => {
  event.preventDefault();
  if (f_map.size === 0) {
    toast("선택한 음식이 없습니다!\n음식을 선택해주세요!")
  } else {
    f_map.forEach((value) => {
      console.log(value)
      let kcal = "해당 음식의 칼로리는 개당 "+value[1]+" kcal 이며, 전체 칼로리는 "+value[1]+" kcal 입니다."
      let html = `<div title="${kcal}" per="${value[1]}" s_code="${value[2]}" class="search_item">
                <a onclick="editamount(this.parentElement)" href="javascript:"><span>${value[0]}</span><span class="amount" style="display:none;"> X <span class="amount_num">2</span></span></a>
                <a onclick="remove_ele(this.parentElement)" href="javascript:">
                  <object data="/assets/images/close-icon.svg" type="image/svg+xml" aria-label="닫기아이콘"></object>
                </a>
              </div>`
      opener.document.querySelector(".search_box").insertAdjacentHTML("beforeend", html)
      var q_tokcal = parseInt(opener.document.querySelector("#tokcal").innerText) + parseInt(value[1]);
      opener.document.querySelector("#tokcal").innerText = q_tokcal;

    })
    window.close()
  }
})

sendFood.addEventListener("click", (event) => {
  event.preventDefault();
  //  console.log("검색 click");
  searchfood();
})

searchFood.addEventListener("keyup", (event) => {if(event.keyCode==13){
  searchfood();
}})

async function searchfood() {
return new Promise((resolve, reject) => {
  let keyword = searchFood.value.trim()
  progress_h.innerText = "서버에서 데이터를 취득중입니다.";
  if (keyword != "") {
    fetch("/api/food/search/or", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        "keywords": searchFood.value
      })
    })
    .then((data) => {
      f_map.clear(); // 체크박스 선택 기록 초기화
      progress_h.innerText = "서버로부터 받은 데이터를 정리중입니다."
      // API 응답 데이터를 검색하고자 하는 단어와 비교
      loading.style.display = 'flex';
      itemappend.style.display = 'none';
      itemappend.innerHTML = '';
      data.json().then((items) => { // function a () {} <==> () => {} 화살표 배워올게요
        let fd_leng = items.length;
        var i_food = [];
        var i_skip = 0;
        var to_html = "";

        let fd_n = 0;
        if (fd_leng < 1) {
          toast("검색 결과가 없습니다.")
        } else {
          items.forEach((item_var) =>{ //data를 돌리면 안되죠
            fd_n = fd_n + 1
            let percent = ((fd_n / fd_leng) * 100).toFixed(2)
            let progress = fd_n+" / "+fd_leng+" ( "+percent+" % )"

            progress_h.innerText = progress;
            //console.log(progress)
            //toast(percent+" %")
          //console.log(item_var) //됐져!! ㅇㅇ! 됬음~! 매우 감사합니다.. 큰절올려요 ㅋ ㅋㅋㅋㅋㅋ
          if (item_var != null) {
            
            let kcal_data = item_var.칼로리;
            // console.log(Number(item_var.value))
            //console.log(kcal_data + "여기는 칼로리 데이터")
            let foodid = item_var.SAMPLE_ID
            if (i_food.includes(foodid)) {
              i_skip = i_skip + 1;
              //console.error("데이터 중복 삽입 시도 발견 : "+foodid);
            } else {
              i_food.push(foodid);
              let kcalNum = Math.round(item_var.칼로리);
                if(item_var != null){
                  let html = `
                <li>
                  <div class="checkbox">
                      <input type="checkbox" id="${foodid}">
                      <label for="${foodid}">체크하기</label>
                  </div>
                  <p class="info_txt">${item_var.식품명}</p>
                  <div class="right_box">
                      <p style="margin-right:20px" class="kcal">${kcalNum} kcal</p>
                      <!--<a class="more_btn" id="moreBtn" href="javascript:">상세보기</a>-->
                  </div>
              </li>
                  `

                  to_html = to_html+html
                  //변수에다가 html을 삽입하라고하면 컴퓨터한테 뭘바라는거에요 쪼매만 기다려주숑 오키오키
                  
              }
            }
          }
        })
      }
      progress_h.innerText = "정돈된 데이터를 추가하는중입니다."
      itemappend.insertAdjacentHTML("beforeend", to_html); // 땡 해당 스트링은 투입 위치를 지정하는것임 ( beforestart 요소가 위로 올라감 , afterstart 요소가 올라가지만 beforestart보다는 아래 , beforeend 요소가 아래로감 , afterend beforeend보다 더 아래로감 틀을 벗어날수잇음 )           
                  check_event();
                  //more_event();
      itemappend.style.display = '';
      loading.style.display = 'none';
      h_search_count_num.innerText = fd_leng - i_skip;
      h_search_count.style.display = 'flex';
    }); // then에는 데이터가 있으니 데이터를 받아올 변수를 지정해줘야 이제 함순데 함수를 console.log 하나요 k아뉴 변수 생각요요 변수는 아무거나 해도되요
      
      /*for (let i = 0; i < data.length; i++) {
        const item = data;   
        const strfy = JSON.stringify(item);
        const str = JSON.parse(item); 
        console.log(strfy);
        console.log(str);
      }*/
    })
    .catch(error => {
      console.error('API 요청 중 오류가 발생했습니다.', error);
    });
  } else {
    toast("공백을 검색 할순 없습니다.")
  }
})}

function checkevent(e) {
  // let target = pointerevent.target
  // console.log("체크박스 이벤트"+target);
  // // console.log(target.id)    
  // const checkbox = document.getElementById(foodid);

  //f_map 체크한 음식 맵
  const f_check = e.target.parentElement.children[0];
  const f_obj = f_check.parentElement.parentElement;
  if (!f_check.checked) {
    let f_name = f_obj.children[1].innerText;
    let f_kcal = parseInt(f_obj.children[2].children[0].innerText.replace(" kcal", "")); 
    let f_data = [f_name, f_kcal, f_check.attributes.id.value]
    f_map.set(f_check.attributes.id.value, f_data)
    //console.log(f_map)
  } else {
    f_map.delete(f_check.attributes.id.value)
    //console.log(f_map)
  }
}

function check_event() {
  Array.prototype.forEach.call(kcalBox.children,(element) =>{
    element.children[0].children[1].removeEventListener("click", checkevent);
    element.children[0].children[1].addEventListener("click", checkevent)})
}


//JSON.parse("str") //스트링으로 있는 json계열 list를 변환한다  (STR -> JSON (ARRAY, LIST))
//JSON.stringify(json) //list형을 스트링으로 변환한다. (JSON (ARRAY, LIST) -> STR) 아하!


// 상세보기 팝업
function more_event(foodid) {
  //let moreBtn = document.querySelector("#moreBtn");
  let kcal_popup = document.querySelector(".kcal_popup_wrap");
  let bakcBtn = document.querySelector(".black_line_btn");
  /*moreBtn.addEventListener("click", (event) => {
    event.preventDefault();
    kcal_popup.style.display = "block";
    console.log("상세보기 click");
  })*/
  bakcBtn.addEventListener("click", (event) => {
    event.preventDefault();
    kcal_popup.style.display = "none";
  })
}