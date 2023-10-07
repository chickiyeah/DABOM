window.addEventListener('DOMContentLoaded', async function() {
    eat_avg(0)
    get_bmi()
})

function eat_avg(cal_date) {
    let sel_ele = document.getElementsByName("date")
    sel_ele.forEach((ele) => {
        if (ele.id == `avg_${cal_date}`) {
            ele.classList.add("on")
        } else {
            ele.classList.remove("on")
        }
    })

    var date = new Date();
    var cyoil = date.getDay()+1
    date.setDate(date.getDate() - cal_date)
    var pyoil = date.getDay()+1
    
    if (cyoil != pyoil) {
        let deff = 0;
        let sum = "plus"
        if (cyoil > pyoil) {
            deff = cyoil - pyoil
            sum = "plus"
        }

        if (cyoil < pyoil) {
            deff = pyoil - cyoil
            sum = "minus"
        }

        if (sum === "plus") {
            date.setDate(date.getDate() + deff)
        }

        if (sum === "minus") {
            date.setDate(date.getDate() - deff)
        }
    }

    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);

    let s_date = `${year}-${month}-${day}`;

    fetch(`/api/user/eat_avg/${s_date}`, {
        method: 'GET'
    }).then((response) => {
        response.json().then((data) => {
            console.log(data)
            let base_kcal = 0
            if (data.base_kcal === 0) {
                if (data.p_gender === 'male') {
                    base_kcal = 2700
                }

                if (data.p_gender === 'female') {
                    base_kcal = 2000
                }
            } else {
                base_kcal = data.base_kcal
            }

            let cur_kcal = data.total_kcal

            if (cur_kcal === undefined) {
                
                //document.getElementById('cur_per_bar').style.width = "??? %"

                document.getElementById('cur_kcal').innerHTML = "?????"
                document.getElementById('cur_kcal_bar').innerHTML =  "?????"
                document.getElementById("to_kcal").innerHTML =  "?????"
                document.getElementById("to_kcal_bar").innerHTML =  "?????"
                document.getElementById('cur_per').innerHTML = "??"

                document.querySelector(".food_list").innerHTML = "<div class='desc'>자주 먹은 음식이 존재하지 않습니다.\n지금 바로 작성해 보세요.</div>"
            } else {
                document.getElementById("login").style.display = "none"
                document.getElementById("logout").style.display = ""
                
                let per_cal_day = cal_date

                if (cal_date == 0) {
                    per_cal_day = 1
                }

                let per = (cur_kcal / (base_kcal * per_cal_day)) * 100
                
                document.getElementById('cur_per').innerHTML = per.toFixed(2)

                if (per < 31) {
                    per = 30
                }

                if (per > 100) {
                    per = 100
                }

                document.getElementById('cur_per_bar').style.width = per +"%"

                document.getElementById('cur_kcal').innerHTML = cur_kcal
                document.getElementById('cur_kcal_bar').innerHTML = cur_kcal
                document.getElementById("to_kcal").innerHTML = base_kcal * per_cal_day
                document.getElementById("to_kcal_bar").innerHTML = base_kcal * per_cal_day


                let foods = data.sort_foods
                let max = foods.length
                
                if (max > 6) {
                    max = 6
                }
                
                let to_html = ""

                for (i=0; i<max; i++) {
                    let food = foods[i]
                    let html = `<li>
                        <i class="circle">${i+1}</i>
                        <p>${food[0]}</p>
                        <div class="number">${food[1]}회</div>
                    </li>`

                    to_html = to_html + html
                }
                if (to_html === "") {
                    document.querySelector(".food_list").innerHTML = "<div class='desc'>자주 먹은 음식이 존재하지 않습니다.\n지금 바로 작성해 보세요.</div>"
                } else {
                    document.querySelector(".food_list").innerHTML = to_html
                }
                
            }
        })
    })
}

function get_bmi() {
    fetch(`/api/nutrient/calculate/bmi`, {
        method: 'GET'
    }).then(function (response) {
        response.json().then(function (data) {
            let h_weight = document.getElementsByName("weight")
            let weight_status = "normal"
            
            if (data.status == "저체중") {
                weight_status = "low"
            }

            if (data.status == "정상") {
                weight_status = "normal"
            }

            if (data.status == "과체중") {
                weight_status = "big"
            }

            if (data.status == "비만") {
                weight_status = "fat"
            }

            if (data.status == "고도비만") {
                weight_status = "super_fat"
            }

            h_weight.forEach((ele) => {
                if (ele.id === weight_status) {
                    ele.classList.add("on")
                } else {
                    ele.classList.remove("on")
                }
            })

            if (data.nickname === undefined) {
                document.getElementById("b_nick").innerText = "?????"
                document.getElementById("b_bmi").innerText = "?????"
                document.getElementById("b_status").innerText = "정상"
            }else{
                document.getElementById("b_nick").innerText = data.nickname
                document.getElementById("b_bmi").innerText = data.bmi
                document.getElementById("b_status").innerText = data.status
            }

            
        })
    })
}

async function logout() {
    fetch("/api/user/logout", {
      method: "GET"
    }).then((response) => {
      if (response.status === 200) {
        localStorage.clear();
        location.href = "/";
      } else {
        alert("로그아웃중 서버 오류가 발생했습니다.\n콘솔의 오류사항을 고객센터로 제보해주시기 바랍니다.")
        response.json().then((response) => { console.error(response)})
      }
    })
  }