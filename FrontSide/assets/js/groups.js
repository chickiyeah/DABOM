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
                            if (type === "public" || type === "owned") {
                                if (type === "public") {
                                    await list_public(page)
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
                console.log(data);
            })
        })
    }
}