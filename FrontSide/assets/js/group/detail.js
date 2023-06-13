window.addEventListener('DOMContentLoaded', async function() {
    if(this.location.href.includes('?')) {
        let parameters = this.location.href.split('?')[1].split('&');
        parameters.forEach((param) => {
            let key = param.split('=')[0];
            let value = param.split('=')[1];
            if (key === 'id') {
                let access_token = sessionStorage.getItem("access_token")
                // 가입중인거
                fetch(`/api/group/p_groups`, {
                method: 'GET',
                headers: {
                    Authorization: access_token
                }
                }).then((res) => {
                    res.json().then((data) => {
                        let joined = JSON.parse(data.groups)
                        if (joined.includes(parseInt(value))) {
                            get_group_data(value)
                        } else {
                            this.alert("올바르지 않은 접근입니다.")
                            this.location.href = "/groups?page=1&type=public"
                        }
                    })
                })
            }
        })
    }
})

const banner_img = document.querySelector(".banner_img").children[0]
const title = document.querySelector(".top_txt").children[0]
const members = document.querySelector(".top_txt").children[1]

function get_group_data(id) {
    fetch(`/api/group/detail/${id}`,{
        method: 'GET'
    }).then((res) => {
        res.json().then((group) => {
            let mem = JSON.parse(group.members).length
            let name = group.name
            let img = group.groupimg
            let no = group.id
            banner_img.src = img
            title.innerText = name
            members.innerText = "멤버 : "+mem+" 명"
            document.querySelector(".red_btn").style.display = "block"
            document.querySelector(".red_btn").href = `javascript:sessionStorage.setItem('chat_room', ${no});sessionStorage.setItem('chat_title', '${name} 모임의 채팅방');window.open('/chat', '채팅')`
        })
    })
}