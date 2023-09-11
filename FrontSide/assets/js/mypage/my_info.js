
const loading = document.querySelector(".loading");
document.addEventListener("DOMContentLoaded", async () => {
    await verify_token()
    set_default_data()
})

var onloadCallback = function() {
    console.log(grecaptcha.getResponse())
};


function onSubmit(token) {
    console.log(token)
}

function check_captcha() {
    var v = grecaptcha.getResponse();
    if(v.length == 0)
    {
        return false;
    } else {
        return true;
    }
}

async function edit_personal_info(token) {
    if (!check_captcha()) {
        alert("먼저 로봇 인증을 진행해주세요.")
    } else {
    

      

        var sub_edit = confirm("개인정보를 수정하시겠습니까?");
        if(sub_edit) {
          //요소 지정
      const h_imsg = document.querySelector("#imsg");
      const h_Nickname = document.querySelector("#Nickname");
      const h_genders = document.getElementsByName("gender");
      const h_weight = document.querySelector("#weight");
      const h_height = document.querySelector("#height");
      const h_year = document.querySelector("#year");
      const h_month_sel = document.querySelector("#month");
      const h_date = document.querySelector("#date");
      const h_pf_image = document.querySelector("#pf_image");
      
      let new_pf = {
        "g_captcha": token,
        "imsg": h_imsg.value,
        "Nickname": h_Nickname.value,
        "weight": h_weight.value,
        "height": h_height.value,
        "profile_image": h_pf_image.src
      }

      h_genders.forEach((gender) => {
          if (gender.checked) {
              new_pf.gender = gender.id
          }
      })

      new_pf.birthday = `${h_year.value}-${h_month_sel.selectedIndex}-${h_date.value}`;
            fetch("/api/user/edit_profile", {
                method: "POST",
                credentials: "include",
                body: JSON.stringify(
                    new_pf
                )
            }).then(function(response) {
                if (response.status === 200) {
                  location.reload();
                }
            })
        }
    }
}

async function set_default_data() {
    fetch(`/api/user/cookie/me`, {
        method: "GET"
    }).then((response) => {
        response.json().then((data) => {
            //요소 지정
            const h_imsg = document.querySelector("#imsg");
            const h_email = document.querySelector("#email");
            const h_Nickname = document.querySelector("#Nickname");
            const h_genders = document.getElementsByName("gender");
            const h_weight = document.querySelector("#weight");
            const h_height = document.querySelector("#height");
            const h_year = document.querySelector("#year");
            const h_month_sel = document.querySelector("#month");
            const h_date = document.querySelector("#date");
            const h_pf_image = document.querySelector("#pf_image");
            const birthday = data.birthday.split("-");

            //요소 변수 지정
            h_imsg.value = data.imsg;
            h_email.value = data.email;
            h_Nickname.value = data.Nickname;
            h_weight.value = data.weight;
            h_height.value = data.height;
            h_pf_image.src = data.profile_image;
            
            h_genders.forEach((gender) => {
                if (gender.id == data.gender) {
                    gender.checked = true
                    console.log("gender changed")
                }
            })

            h_year.value = birthday[0];
            h_date.value = birthday[2];
            
            h_month_sel.selectedIndex = parseInt(birthday[1])

            console.log(data)
        })
    })
}

async function LoadCookie(){
    let lo_access_token = localStorage.getItem("access_token")
    let lo_refresh_token = localStorage.getItem("refresh_token")
    if (location.href.includes("login") == false && location.href.includes("register") == false && this.location.href.includes("findaccount") == false && this.location.href != this.location.origin+"/") {
      if(lo_access_token == null || lo_refresh_token == null || lo_access_token.length < 22 || lo_refresh_token.length < 22) {
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

              if (detail.code === "ER011") {
                localStorage.clear();
                location.href = "/login";
              }
            })
          }
        })  
      }
    }
}

async function verify_token() {
  return new Promise(async function(resolve, reject) {
    const loading = document.querySelector(".loading");
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
              }else if (response.status === 307 || response.status === 401) {
                localStorage.clear();
                document.querySelector(".loading").style.display = "none"
                if (location.href != location.origin+"/" && location.href.includes("login") == false && location.href.includes("register") == false && location.href.includes("findaccount") == false) {
                  location.href = "/login";
                }
                
              }else{
                  response.json().then(async (json) => {
                      let detail_error = json.detail;
                      console.log(detail_error)
                      if (detail_error.code == "ER015") {
                        await LoadCookie();
                      }

                      if (detail_error.code == "ER998") {
                        await LoadCookie();
                      }
                  });
              }
          } else {
            response.json().then(async (json) => {
              loading.style.display = "none"
              resolve(json[2])
            })
          }
      })
  })
}