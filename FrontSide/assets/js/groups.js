window.addEventListener('DOMContentLoaded', async function() {
    if(this.location.href.includes('groups')){
        if(location.href.includes('?')){
            let param = this.location.href.split('?')[1];
            let params = param.split('&');
            let keys = [];
            let values = []
            if (params.length != 2) {this.location.href = "/groups?page=1&type=public"}else{
                params.forEach(async (data) => {
                    let key = data.split('=')[0]
                    let value = data.split('=')[1]
                    keys.push(key)
                    values.push(value)
                })

                var q_data = {page: 0, type: "none"}

                for (let i = 0; i < keys.length; i++) {
                    q_data[keys[i]] = values[i]
                }

                if (keys.includes("page") && keys.includes("type")) {
                    if (!isNaN(q_data['page'])) {
                        console.log("page numm")
                        let page = q_data['page']
                        if (page < 1) {
                            location.href = "/groups?page=1&type=public"
                        }else{
                            document.querySelector(".loading").style.display = "flex"
                            let type = q_data['type']
                            if (type === "public" || type === "owned" || type === "joined") {
                                if (type === "public") {
                                    document.querySelector("#public").style.display = "flex"
                                    document.querySelector("#joined").remove()
                                    document.querySelector("#owned").remove()
                                    document.querySelector("#public_btn").classList.add("on")
                                    document.querySelector("#public_btn").children[0].href = "javascript:"
                                    await list_public(page)   
                                }

                                if (type === "joined") {
                                    document.querySelector("#joined").style.display = "flex"
                                    document.querySelector("#public").remove()
                                    document.querySelector("#owned").remove()
                                    document.querySelector("#joined_btn").classList.add("on")
                                    document.querySelector("#joined_btn").children[0].href = "javascript:"
                                    await mygroups(page)
                                }

                                if (type === "owned") {
                                    document.querySelector("#owned").style.display = "flex"
                                    document.querySelector("#joined").remove()
                                    document.querySelector("#public").remove()
                                    document.querySelector("#owned_btn").classList.add("on")
                                    document.querySelector("#owned_btn").children[0].href = "javascript:"
                                    await list_owned(page)
                                }
                            } else {
                                this.location.href = "/groups?page=1&type=public"
                            }
                                
                        }
                    } else {
                        this.location.href = "/groups?page=1&type=public"
                    }
                    
                } else {
                    this.location.href = "/groups?page=1&type=public"
                }
            }
        }else{
            this.location.href = "/groups?page=1&type=public"
        }
    }
})

import { clickEnter } from "./enterEvent.js";
import { send_alert } from "./alert.js";

const pagediv = document.querySelector("#page_div")

const public_ul = document.querySelector("#public")
const joined_ul = document.querySelector("#joined")
const onwed_ul = document.querySelector("#owned")

const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;

var element_invite_group_button = document.createElement("button");
var element_invite_group_email_input = document.createElement("input");

clickEnter(element_invite_group_email_input, element_invite_group_button);

var joined

async function list_public(page) {
    if (page <= 0) {
        return new Error("wrong page")
    }else{
        let access_token = sessionStorage.getItem("access_token")
        fetch(`/api/group/list/${page}`, {
            method: 'GET'
        }).then((res) => {
            res.json().then((data) => {
                let groups = data.groups
                let count = data.count
                
                // 가입중인거
                fetch(`/api/group/p_groups`, {
                    method: 'GET',
                    headers: {
                        Authorization: access_token
                    }
                }).then((res) => {
                    res.json().then((data) => {
                        joined = JSON.parse(data.groups)
                        
                        console.log(joined)

                        // 페이징
                        let to_page = count / 9
                        var maxpage
                        if (Number.isInteger(to_page)) {
                            maxpage = to_page
                        } else {
                            maxpage = Math.floor(to_page) + 1
                        }

                        console.log(page)
                        console.log(maxpage)
                        var startpage
                        var endpage
                        if (page / 10 > 1) {
                            startpage = Math.floor((page/10))*10
                            endpage = Math.floor((page/10))*10 + 1 + 10
                        }else{
                            startpage = 1
                            endpage = 11
                        }
                        document.querySelector(".prev").href = `javascript:location.href='/groups?page=${page-1}&type=public'`
                        document.querySelector(".next").href = `javascript:location.href='/groups?page=${page+1}&type=public'`

                        if (page > maxpage) {
                            location.href = "/groups?page="+maxpage+"&type=public"
                        }else{
                            for (let i = startpage; i < maxpage+1; i++) {
                                if (i == page) {
                                    pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:location.href='/groups?page=${i}&type=public'">${i}</a>`)
                                }else{
                                    pagediv.insertAdjacentHTML("beforeend", `<a class="num" href="javascript:location.href='/groups?page=${i}&type=public'">${i}</a>`)
                                }
                            }
                        }

                        console.log("all public groups: "+count)
                        groups.forEach((group) => {
                            var html
                            let mem = JSON.parse(group.members).length
                            let name = group.name
                            let img = group.groupimg
                            if (joined.includes(group.no)){
                                html = `<li>
                                            <div class="img_box">
                                                <img alt="게시글 이미지" src="${img}">
                                            </div>
                                            <div class="info_box">
                                                <p class="title">${name}</p>
                                                <p class="sub_txt">맴버: ${mem}명</p>
                                                <a href="javascript:">상세보기</a>
                                            </div>
                                        </li>`
                            } else {
                                html = `<li>
                                            <div class="img_box">
                                                <img alt="게시글 이미지" src="${img}">
                                            </div>
                                            <div class="info_box">
                                                <p class="title">${name}</p>
                                                <p class="sub_txt">맴버: ${mem}명</p>
                                                <a href="javascript:">가입하기</a>
                                            </div>
                                        </li>`
                            }

                            public_ul.insertAdjacentHTML("beforeend", html)
                        })
                        document.querySelector(".loading").style.display = "none"
                    })
                })
            })
        })
    }
}

async function mygroups(page) {
    let access_token = sessionStorage.getItem("access_token")
    if (page <= 0) {
        return new Error("wrong page")
    }else{
        fetch(`/api/group/mygroups/${page}`, {
            method: 'GET',
            headers: {
                Authorization: access_token
            }
        }).then((res) => {
            res.json().then((data) => {
                let groups = data.groups
                let count = data.count
                
                // 페이징
                let to_page = count / 9
                var maxpage
                if (Number.isInteger(to_page)) {
                    maxpage = to_page
                } else {
                    maxpage = Math.floor(to_page) + 1
                }

                console.log(page)
                console.log(maxpage)
                var startpage
                var endpage
                if (page / 10 > 1) {
                    startpage = Math.floor((page/10))*10
                    endpage = Math.floor((page/10))*10 + 1 + 10
                }else{
                    startpage = 1
                    endpage = 11
                }
                document.querySelector(".prev").href = `javascript:location.href='/groups?page=${page-1}&type=joined'`
                document.querySelector(".next").href = `javascript:location.href='/groups?page=${page+1}&type=joined'`

                if (page > maxpage) {
                    location.href = "/groups?page="+maxpage+"&type=joined"
                }else{
                    for (let i = startpage; i < maxpage+1; i++) {
                        if (i == page) {
                            pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:location.href='/groups?page=${i}&type=joined'">${i}</a>`)
                        }else{
                            pagediv.insertAdjacentHTML("beforeend", `<a class="num" href="javascript:location.href='/groups?page=${i}&type=joined'">${i}</a>`)
                        }
                    }
                }

                console.log("total joined groups: "+ count)
                groups.forEach((group) => {
                    let mem = JSON.parse(group.members).length
                    let name = group.name
                    let img = group.groupimg
                    let html = `<li>
                                    <div class="img_box">
                                        <img alt="게시글 이미지" src="${img}">
                                    </div>
                                    <div class="info_box">
                                        <p class="title">${name}</p>
                                        <p class="sub_txt">맴버: ${mem}명</p>
                                        <a class="black_btn" href="javascript:">탈퇴하기</a>
                                    </div>
                                </li>`
                    
                                
                    joined_ul.insertAdjacentHTML("beforeend", html)
                })
                document.querySelector(".loading").style.display = "none"
            })
        })
    }
}

async function list_owned(page) {
    let access_token = sessionStorage.getItem("access_token")
    if (page <= 0) {
        return new Error("wrong page")
    }else{
        fetch(`/api/group/owned_groups/${page}`, {
            method: 'GET',
            headers: {
                Authorization: access_token
            }
        }).then((res) => {
            res.json().then((data) => {
                let groups = data.groups
                let count = data.count
                
                // 페이징
                let to_page = count / 9
                var maxpage
                if (Number.isInteger(to_page)) {
                    maxpage = to_page
                } else {
                    maxpage = Math.floor(to_page) + 1
                }

                console.log(page)
                console.log(maxpage)
                var startpage
                var endpage
                if (page / 10 > 1) {
                    startpage = Math.floor((page/10))*10
                    endpage = Math.floor((page/10))*10 + 1 + 10
                }else{
                    startpage = 1
                    endpage = 11
                }
                document.querySelector(".prev").href = `javascript:location.href='/groups?page=${page-1}&type=joined'`
                document.querySelector(".next").href = `javascript:location.href='/groups?page=${page+1}&type=joined'`

                if (page > maxpage) {
                    location.href = "/groups?page="+maxpage+"&type=joined"
                }else{
                    for (let i = startpage; i < maxpage+1; i++) {
                        if (i == page) {
                            pagediv.insertAdjacentHTML("beforeend", `<a class="selected" href="javascript:location.href='/groups?page=${i}&type=joined'">${i}</a>`)
                        }else{
                            pagediv.insertAdjacentHTML("beforeend", `<a class="num" href="javascript:location.href='/groups?page=${i}&type=joined'">${i}</a>`)
                        }
                    }
                }

                console.log("total owned groups: "+ count)
                groups.forEach((group) => {
                    let mem = JSON.parse(group.members).length
                    let name = group.name
                    let img = group.groupimg
                    let html = `<li>
                                    <div class="img_box">
                                        <img alt="게시글 이미지" src="${img}">
                                    </div>
                                    <div class="info_box">
                                        <p class="title">${name}</p>
                                        <p class="sub_txt">맴버: ${mem}명</p>
                                        <div class="btn_box">
                                            <a class="gray_btn" href="javascript:">수정</a>
                                            <a class="black_btn" href="javascript:">삭제</a>
                                        </div>
                                    </div>
                                </li>`
                    console.log(group)

                    onwed_ul.insertAdjacentHTML('beforeend', html)
                })
                document.querySelector(".loading").style.display = "none"
            })
        })
    }
}