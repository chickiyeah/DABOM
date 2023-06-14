window.addEventListener('DOMContentLoaded', async function() {
    document.querySelector(".loading").style.display = 'none';
})


const public_d = document.querySelector('.btn_box').children[0]
const private_d = document.querySelector('.btn_box').children[1]
const title_input = document.querySelector('#title')
const img = document.querySelector('.upload_img').children[0]
const add_button = document.querySelector('#submit')

var type = 'Public'
public_d.addEventListener('click', () => {
    public_d.classList.remove("red_line_btn")
    public_d.classList.add("red_btn")
    private_d.classList.remove("red_btn")
    private_d.classList.add("red_line_btn")
    type = 'Public'
    console.log(type, title_input.value, img.src)
})

private_d.addEventListener('click', () => {
    private_d.classList.remove("red_line_btn")
    private_d.classList.add("red_btn")
    public_d.classList.remove("red_btn")
    public_d.classList.add("red_line_btn")
    type = 'Private'
    console.log(type, title_input.value, img.src)
})

add_button.onclick = () => {
    if (title_input.value === "") {
        alert("모임의 이름을 입력해주세요.")
    } else {
        document.querySelector(".loading").style.display = 'flex';
        let access_token = sessionStorage.getItem("access_token")
        fetch("/api/group/create",{
            method: "POST",
            headers:{
                'Authorization': access_token,
                "content-type": "application/json"
            },
            body: JSON.stringify({
                'name': title_input.value,
                'description': '소개글을 수정해보세요!',
                'type': type,
                'image': img.src
            })
        }).then(response => {
            if (response.status === 200) {
                alert("그룹 생성을 요청했습니다.\n브라우저의 인터넷 속도와 서버 상태에 따라 최장 5분이 소요될 수 있습니다.")
                location.href = "/groups?page=1&type=owned"
            } else if (response.status === 500) {
                alert("이름을 확인해주세요 특수문자 오류가 발생하였습니다.")
                document.querySelector(".loading").style.display = 'none';
            }else{
                response.json().then((err) => {
                    let detail_error = err.detail;
                    if (detail_error.code == "ER022") {
                        alert("그룹 생성이 차단된 계정입니다.")
                        location.href = "/groups?page=1&type=owned"
                    }
                })
            }
        })
    }
}