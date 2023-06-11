"use strict";

const images = sessionStorage.getItem("da_u_files"); //세션 스토리지에서 da_u_files의 키값을 가진 값(value)를 가져와라.


const imgBox = document.querySelector('.img_box'); // 고정 요소는 최대한 const로 
const imgItem = document.querySelector('.img_item');
const closeBtn = document.querySelector('.close_btn');


var beforex = -1

window.addEventListener('DOMContentLoaded', function() {
  init();

  imgItem.addEventListener('dragover', function(e) {
    let onx = e.clientX
    var curx = document.querySelector('.img_item').scrollLeft
    if (beforex != -1) {
      if (beforex < onx) {
        console.log('going right');
        document.querySelector('.img_item').scrollLeft = curx - 30
      }

      if (beforex == onx) {
        console.log('staying')
      }

      if (beforex > onx) {
        console.log('going left');
        document.querySelector('.img_item').scrollLeft = curx + 30
      }
    }
    beforex = onx;
  })
})

//image -> (image) 여는 괄호는 어디로가썽요 임마박스는 뭐에요 date_item?? 아뇨 imgBox 가 왜 imaBox가 됬어요 앜ㅋ 오타.. ㅋㅋㅋㅋㅋ
function init() {
  console.log("init progressing")
  console.log(images)
  let imglist = images.split(",");
  let img_data = imglist[0];
  // let imgId = img_data.ID;
  var num = 1;
  let imgId = img_data + num++;
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
}


