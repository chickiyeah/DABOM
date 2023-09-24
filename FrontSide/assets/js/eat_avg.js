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

            let per_cal_day = cal_date

            if (cal_date == 0) {
                per_cal_day = 1
            }

            let per = (cur_kcal / (base_kcal * per_cal_day)) * 100
            
            document.getElementById('cur_per').innerHTML = per.toFixed(2)

            if (per < 20) {
                per = 25
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

            document.querySelector(".food_list").innerHTML = to_html
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

            document.getElementById("b_nick").innerText = data.nickname
            document.getElementById("b_bmi").innerText = data.bmi
            document.getElementById("b_status").innerText = data.status
        })
    })
}