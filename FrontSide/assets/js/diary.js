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

var beforex = -1

window.addEventListener('DOMContentLoaded', function() {
  init();
  if (this.location.href.includes('diary_update')) {
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
                    imgItem.insertAdjacentHTML("beforeend", html); // 땡 해당 스트링은 투입 위치를 지정하는것임 ( beforestart 요소가 위로 올라감 , afterstart 요소가 올라가지만 beforestart보다는 아래 , beforeend 요소가 아래로감 , afterend beforeend보다 더 아래로감 틀을 벗어날수잇음 )           
                    remove_event()
        }
    });
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
    console.log(imgId);
    if(target.id == imgId){
      if(confirm('정말 삭제하시겠어요?')){
        target.parentElement.parentElement.remove();
      }else{

      }
    }
  }

  function remove_event() {
    Array.prototype.forEach.call(imgItem.children,(element) =>{
      element.children[0].children[1].removeEventListener("click", closeevent);
      element.children[0].children[1].addEventListener("click", closeevent)})
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

sendFood.addEventListener("click", (event) => {
  event.preventDefault();
  console.log("검색 click");
  searchfood();
})

async function searchfood() {
  let access_token = sessionStorage.getItem("access_token");
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
    // API 응답 데이터를 검색하고자 하는 단어와 비교
    data.json().then((items) => { // function a () {} <==> () => {} 화살표 배워올게요
      console.log(items)//대써여!! 이제 이거를 foreach 돌려야죠
      itemappend.innerHTML = '';
      items.forEach((item_var) =>{ //data를 돌리면 안되죠
      console.log(item_var) //됐져!! ㅇㅇ! 됬음~! 매우 감사합니다.. 큰절올려요 ㅋ ㅋㅋㅋㅋㅋ
      if (item_var != null) {
        let kcal_data = item_var.칼로리;
        // console.log(Number(item_var.value))
        console.log(kcal_data + "여기는 칼로리 데이터")
        let foodid = item_var.SAMPLE_ID
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
                <p class="kcal">${kcalNum} kcal</p>
                <a class="more_btn" id="moreBtn" href="javascript:">상세보기</a>
            </div>
        </li>
            `
            //변수에다가 html을 삽입하라고하면 컴퓨터한테 뭘바라는거에요 쪼매만 기다려주숑 오키오키
            itemappend.insertAdjacentHTML("beforeend", html); // 땡 해당 스트링은 투입 위치를 지정하는것임 ( beforestart 요소가 위로 올라감 , afterstart 요소가 올라가지만 beforestart보다는 아래 , beforeend 요소가 아래로감 , afterend beforeend보다 더 아래로감 틀을 벗어날수잇음 )           
            check_event(foodid);
            more_event(foodid);
        }
      }
    })
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
}

function checkevent(e) {
  // let target = pointerevent.target
  // console.log("체크박스 이벤트"+target);
  // // console.log(target.id)    
  // const checkbox = document.getElementById(foodid);
  console.log("e" + e);
  const checkbox = e.target;
  const foodid = checkbox.id;
  console.log("e.target :" + checkbox);
  console.log("foodid :" + foodid);
  if(foodid != null){
    checkbox.addEventListener("click", (event) => {
      if (checkbox.checked) {
        console.log(foodid + "선택됨.");
      }else{
        console.log(foodid + "해제됨.");
      }
    });
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
  let moreBtn = document.querySelector("#moreBtn");
  let kcal_popup = document.querySelector(".kcal_popup_wrap");
  let bakcBtn = document.querySelector(".black_line_btn");
  moreBtn.addEventListener("click", (event) => {
    event.preventDefault();
    kcal_popup.style.display = "block";
    console.log("검색 click");
  })
  bakcBtn.addEventListener("click", (event) => {
    event.preventDefault();
    kcal_popup.style.display = "none";
  })
}