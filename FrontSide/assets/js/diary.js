"use strict";

const images = sessionStorage.getItem("da_u_files"); //세션 스토리지에서 da_u_files의 키값을 가진 값(value)를 가져와라.


const imgBox = document.querySelector('.img_box'); // 고정 요소는 최대한 const로 
const imgItem = document.querySelector('.img_item');

window.addEventListener('DOMContentLoaded', function() {
  init()
})

//image -> (image) 여는 괄호는 어디로가썽요 임마박스는 뭐에요 date_item?? 아뇨 imgBox 가 왜 imaBox가 됬어요 앜ㅋ 오타.. ㅋㅋㅋㅋㅋ
function init() {
  console.log("init progressing")
  console.log(images)
  let imglist = images.split(",")
  console.log(imglist)
  imglist.forEach((image) => {
    //imgBox.appendChild(image);
    console.log(image);
    if (image != null) {
      let html = ` 
                        <li>
                            <div class="img_box">
                                <img src="${image}" alt="이미지">
                            </div>
                            <a class="close_btn" href="javascript:">
                                <object data="/assets/images/close-icon.svg" type="image/svg+xml"aria-label="닫기아이콘"></object>
                            </a>
                        </li>
                  `
      imgBox.insertAdjacentHTML("beforeend", html); // 땡 해당 스트링은 투입 위치를 지정하는것임 ( beforestart 요소가 위로 올라감 , afterstart 요소가 올라가지만 beforestart보다는 아래 , beforeend 요소가 아래로감 , afterend beforeend보다 더 아래로감 틀을 벗어날수잇음 )           
    }
  });
}
