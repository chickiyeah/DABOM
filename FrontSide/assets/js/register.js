const loading = document.querySelector(".loading");

// 회원가입
const nickname = document.querySelector("#join_name");
const joinGender = document.querySelector("#join_gender");
const height = document.querySelector("#join_tail");
const weight = document.querySelector("#join_weight");
const year = document.querySelector("#join_bir_mon");
const day = document.querySelector("#join_bir_day");
const month = document.querySelector("#join_bir_col");

const male_radio = document.querySelector("#male_radio");
const female_radio = document.querySelector("#female_radio");
const private_radio = document.querySelector("#private_radio");

loading.style.display = "none";

if (location.href.includes("register")) {
    male_radio.addEventListener("click", (e) => {
      e.preventDefault()
      male_radio.children[0].checked = true
      joinGender.attributes.value.value = "male"
      gender = "male"
      console.log("남성 클릭 감지")
    })
  
    female_radio.addEventListener("click", (e) => {
      e.preventDefault()
      female_radio.children[0].checked = true
      joinGender.attributes.value.value = "female"
      gender = "female"
      console.log("여성 클릭 감지")
    })
  
    private_radio.addEventListener("click", (e) => {
      e.preventDefault()
      private_radio.children[0].checked = true
      joinGender.attributes.value.value = "private"
      gender = "private"
      console.log("비공개 클릭 감지")
    })
}

/** 회원가입
 */
function register() {
    const email = document.querySelector("#login_email");
    const password = document.querySelector("#login_pw");

    loading.style.display = 'flex';
    fetch("/api/user/register", {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        "email": email.value,
        "password": password.value,
        "nickname": nickname.value,
        "gender": gender,
        "birthday": `${year.value}/${month.value}/${day.value}`,
        "height": height.value,
        "weight": weight.value,
        "profile_image": document.querySelector("#pf_pro_image").src
      }),
    })
    .then(async (res) => {
      if (res.status == 201) {
        location.href = "/login?t=r"
      } else if (res.status == 422) {
        alert("입력 혹은 선택되지 않은 곳이 존재합니다.")
        loading.style.display = 'none';
      } else {
        res.json().then(async (json) => {
          let detail = json.detail
          if (detail.code == "ER010") {
            alert("이미 사용중인 이메일입니다. 다른 이메일을 사용해주세요.")
            loading.style.display = 'none';
          }

          if (detail.code == "ER020") {
            alert("성별 선택 오류입니다. 성별을 다시 선택해주세요.")
            loading.style.display = 'none';
          }
        })
      }
    })
}