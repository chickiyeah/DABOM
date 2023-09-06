document.addEventListener("DOMContentLoaded", function() {
    if (this.location.href.includes("?")) {
        if (this.location.href.split("?")[1].includes("id")) {
            const parameters = this.location.href.split("?")[1].split("&");
            parameters.forEach((param) => {
                let key = param.split("=")[0];
                let value = param.split("=")[1];
                if (key === "id") {
                    get_post(value);
                    get_comments(value);
                }
            })
        } else {
            history.back();
        }
    } else {
        history.back();
    }
})



const img_dev = document.querySelector(".swiper-wrapper")

function setdate(date){
    const p_date = document.querySelector("#post_date");
    const week = ['일', '월', '화', '수', '목', '금', '토']
    var date = new Date(date);
    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);
  
    p_date.innerText = year + "년 " + month + "월 " + day +"일 " + week[date.getDay()]+"요일";
}

function get_post(post_no) {
    const title = document.querySelector("#post_title");
    const desc = document.querySelector("#post_desc");
    console.log(post_no);

    fetch(`/api/diary/detail/${post_no}`, {
        method: "GET",
        credentials: "include"
    }).then((response) => {
        response.json().then((data) => {
            let imgs = ""
            //console.log(data)
            JSON.parse(data.images.replace(/'/g, '"')).forEach((image) => {
                let img_html = `
                <div class="swiper-slide">
                    <div class="img_box">
                        <img alt="이미지" src="${image}">
                    </div>
                </div>`
                imgs = imgs + img_html
            })
            setdate(data.created_at)
            document.querySelector(".swiper-wrapper").innerHTML = imgs

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
            document.querySelector(".y_txt").innerText = eat_when

            desc.innerText = data.desc
            document.querySelector(".kcal").innerText = data.total_kcal+" Kcal"

            document.querySelector("#eat_txt").querySelectorAll(".r_txt").forEach((ele) => ele.remove())
            title.innerText = data.title
            if (data.with != "alone") {
                JSON.parse(data.friends.replace(/'/g, '"')).forEach(async (friend) => { 
                    let friend_d = await get_user_info(friend)
                    let f_html  = `<span class="r_txt">${friend_d.Nickname}</span>`
                    //console.log(f_html)
                    document.querySelector("#eat_txt").insertAdjacentHTML("beforeend", f_html)
                })
            }
            document.querySelector("#post_foods").innerHTML=""
            JSON.parse(data.foods.replace(/'/g, '"')).forEach(async (food) => {
                let code = food.code
                let amount = food.amount
                let food_data = await get_food_info(code)
                let food_h = `<tr>
                    <td>${food_data.name}</td>
                    <td>${food_data.kcal} Kcal</td>
                    <td>${amount} 개</td>
                </tr>`
                document.querySelector("#post_foods").insertAdjacentHTML("beforeend", food_h)
            })
            document.querySelector("#p_like_count").innerText = data.likecount
        })
    })
}

function get_comments(post_no) {
    fetch(`/api/diary/detail/${post_no}/comments`,{
        method: "GET",
        credentials: "include"
    }).then((response) => {
        response.json().then((comments) => {
            document.querySelector("#p_comment_count").innerText = comments.length
            console.log(comments)
            comments.forEach((comment) => {
                console.log(comment)
            })
        })
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