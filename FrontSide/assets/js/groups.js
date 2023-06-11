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
                            let type = q_data['type']
                            if (type === "public" || type === "owned" || type === "joined") {
                                if (type === "public") {
                                    await list_public(page)   
                                }

                                if (type === "joined") {
                                    await mygroups(page)
                                }

                                if (type === "owned") {
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

const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;

var element_invite_group_button = document.createElement("button");
var element_invite_group_email_input = document.createElement("input");

clickEnter(element_invite_group_email_input, element_invite_group_button);

async function list_public(page) {
    if (page <= 0) {
        return new Error("wrong page")
    }else{
        fetch(`/api/group/list/${page}`, {
            method: 'GET'
        }).then((res) => {
            res.json().then((data) => {
                let groups = data.groups
                let count = data.count

                // 페이징
                document.querySelector("#group_amount").innerText = `공개 그룹 (${count} 개)`
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
                    console.log(group)
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
                document.querySelector("#group_amount").innerText = `공개 그룹 (${count} 개)`
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
                    console.log(group)
                })
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
                
                /*// 페이징
                document.querySelector("#group_amount").innerText = `공개 그룹 (${count} 개)`
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
                }*/

                console.log("total owned groups: "+ count)
                groups.forEach((group) => {
                    console.log(group)
                })
            })
        })
    }
}