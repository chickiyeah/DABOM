window.addEventListener('DOMContentLoaded', async function() {
    document.querySelector(".loading").style.display = 'none';
})


const public_d = document.querySelector('.btn_box').children[0]
const private_d = document.querySelector('.btn_box').children[1]
const title_input = document.querySelector('#title')
const img = document.querySelector('.upload_img').children[0]
const add_button = document.querySelector('#submit')

var type = 'public'
public_d.addEventListener('click', () => {
    public_d.classList.remove("red_line_btn")
    public_d.classList.add("red_btn")
    private_d.classList.remove("red_btn")
    private_d.classList.add("red_line_btn")
    type = 'public'
    console.log(type, title_input.value, img.src)
})

private_d.addEventListener('click', () => {
    private_d.classList.remove("red_line_btn")
    private_d.classList.add("red_btn")
    public_d.classList.remove("red_btn")
    public_d.classList.add("red_line_btn")
    type = 'private'
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
                'Authorization': access_token
            },
            body: JSON.stringify({
                'name': title_input.value,
                'description': '소개글을 수정해보세요!',
                'type': type,
                'image': img.src
            })
        }).then(response => {
            if (response.status === 200) {
                location.href = "/groups?page=1&type=owned"
            } else {
                //생성 실패 오류 핸들 만들어야함
            }
        })
    }
}