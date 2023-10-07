document.addEventListener("DOMContentLoaded", function() {
    if (this.location.href.includes("?")) {
        if (this.location.href.split("?")[1].includes("id")) {
            if (opener != null) {
                let id = this.location.href.split("?")[1].split("id=")[1]
                let con = confirm("하나의 글을 작성/수정 중에는\n다른글을 수정하지마세요\n* 중복 수정시 데이터 충돌이 발생합니다.\n\n계속 진행하시겠습니까?");
                if (con) {
                    get_post(id);
                } else {
                    history.back()
                }
            } else {
                alert("잘못된 경로로 접근을 시도하였습니다.")
                history.back();
            }
        }
    }
})

function setdate(date){
    const p_date = document.querySelector("#post_date");
    const week = ['일', '월', '화', '수', '목', '금', '토']
    var date = new Date(date);
    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);
  
    p_date.innerText = year + "년 " + month + "월 " + day +"일 " + week[date.getDay()]+"요일";
}


function get_post(post_id) {
    fetch(`/api/diary/detail/${post_id}`, {
        method: "GET",
        credentials: "include"
    }).then((response) => {
        if (response.status === 200) {
            document.getElementById("done").innerText = "수정하기"
            document.getElementById("done").attributes.onclick.value = `submit_edit(${post_id})`
            response.json().then((data) => {
                let imgs = ""
                setdate(data.created_at)
                //console.log(data)
                img_init(data.images.replace(/'/g, '"'))

                var eat_when = "";
                if (data.eat_when == "morning") {
                    eat_when = "아침"
                } else if (data.eat_when == "lunch") {
                    eat_when = "점심"
                } else if (data.eat_when == "night") {
                    eat_when = "저녁"
                } else if (data.eat_when == "free") {
                    eat_when = "간식"
                }

                document.querySelectorAll("#eat_when").forEach((ele) => {
                    if (ele.innerText == eat_when) {
                        ele.classList.add("on");
                    } else {
                        ele.classList.remove("on");
                    }
                })

                document.querySelector("#f_desc").value = data.desc

                document.querySelector("#f_title").value = data.title
                if (data.with != "alone") {
                    JSON.parse(data.friends.replace(/'/g, '"')).forEach(async (friend) => { 
                        Array.prototype.forEach.call(document.querySelector(".content_box").children,(ele) => {
                            let f_id = ele.children[2].children[1].attributes.for.value.split("-")[1]
                            if (friend === f_id) {
                                ele.children[2].children[0].checked = true
                                s_friends.push(friend) //오류 아님
                            }
                        })
                        
                    })
                }

                var to_kcal = 0

                JSON.parse(data.foods.replace(/'/g, '"')).forEach(async (food) => {
                    console.log(food)
                    let code = food.code
                    let amount = food.amount
                    let food_data = await get_food_info(code)
                    var per_kcal = food_data.kcal / food_data.per_gram;
                    let kcal = "해당 음식의 칼로리는 개당 "+food_data.kcal+" kcal 이며, 전체 칼로리는 "+(Math.round(food.gram * per_kcal)*amount)+" kcal 입니다."
                    let html = ''
                    if (amount === 1) {
                        html = `<div title="${kcal}" per="${food_data.kcal}" s_code="${code}" tokcal="${Math.round(food.gram * per_kcal)}" class="search_item">
                                <a onclick="editamount(this.parentElement)" href="javascript:"><span>${food_data.name}</span><span> / <span id="per_gram">${food.gram}</span><span id="default_gram" style="display:none">${food_data.per_gram}</span> g(ml)</span><span class="amount" style="display:none;"> X <span class="amount_num">${amount}</span></span></a>
                                <a onclick="remove_ele(this.parentElement)" href="javascript:">
                                <object data="/assets/images/close-icon.svg" type="image/svg+xml" aria-label="닫기아이콘"></object>
                                </a>
                            </div>`
                    } else {
                        html = `<div title="${kcal}" per="${food_data.kcal}" s_code="${code}" tokcal="${Math.round(food.gram * per_kcal)}" class="search_item">
                                <a onclick="editamount(this.parentElement)" href="javascript:"><span>${food_data.name}</span><span> / <span id="per_gram">${food.gram}</span><span id="default_gram" style="display:none">${food_data.per_gram}</span> g(ml)</span><span class="amount"> X <span class="amount_num">${amount}</span></span></a>
                                <a onclick="remove_ele(this.parentElement)" href="javascript:">
                                <object data="/assets/images/close-icon.svg" type="image/svg+xml" aria-label="닫기아이콘"></object>
                                </a>
                            </div>`
                    }

                    to_kcal = to_kcal + (Math.round(food.gram * per_kcal)*amount)
                    document.querySelector("#tokcal").innerText = to_kcal
                    document.querySelector(".search_box").insertAdjacentHTML("beforeend", html)
                })

                
            })
        } else {
            alert("비정상 접근으로 의심됩니다. 다시 시도해주세요.")
            history.back()
        }
    })
}

/** 음식의 세부정보를 가져오는 함수 
 * @promise (음식의 아이디)
*/
async function get_food_info(food_id) {
    return new Promise((resolve) => {
        //console.log(food_id)
        fetch(`/api/food/detail/${food_id}`, {
            method: 'GET'
        }).then((response) => {
            response.json().then((data) => {
                resolve(data)
            })
        })
    })
}

/** 유저의 세부정보를 가져오는 함수
 * @promise (유저의 아이디)
 */
async function get_user_info(user) {
    return new Promise((resolve, reject) => {
        let url = `/api/user/get_user?id=${user}`
        fetch(url, {
            headers: {
                Authorization: "Bearer cncztSAt9m4JYA9"
            }
        }).then((res) => {
            if (res.status != 200) {
                reject("오류.")
            }else{
                res.json().then(async (json) => {
                    let u_data = json[0]
                    resolve(u_data)
                })
            }
        })
    })
}

function img_init(images) {
    const imgItem = document.querySelector('.img_item');
    if (images != null) {
        let imglist = []
        let i = 0
        console.log(images)
        JSON.parse(images).forEach((image) => {
          //imgBox.appendChild(image);
          console.log(image);
          imglist.push(image);
          if (image != null) {
            let html = ` <li id="img-${image}">
                          <div class="img_box"> 
                            <img src="${image}" alt="이미지">
                            <a class="close_btn" id="${image}" href="javascript:">
                              <object data="/assets/images/close-icon.svg" type="image/svg+xml"
                                      aria-label="닫기아이콘"></object>
                            </a>
                          </div>
                        </li>
                        `
                        imgItem.insertAdjacentHTML("afterbegin", html); 
            }
            i++
            if(i === JSON.parse(images).length) {
                sessionStorage.setItem("da_u_files", imglist);
            }
        });
        
        remove_event()
    } else {
        sessionStorage.setItem("da_u_files", "[]");
    }
}

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
    const imgItem = document.querySelector('.img_item');
    Array.prototype.forEach.call(imgItem.children,(element) =>{
      if (!element.children[0].classList.contains('uoload_list')) {
        console.log(element.children[0].classList)
        element.children[0].children[1].removeEventListener("click", closeevent);
        element.children[0].children[1].addEventListener("click", closeevent)
      }
    }) 
}