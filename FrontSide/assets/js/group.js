window.addEventListener('DOMContentLoaded', async function() {
    if(this.location.href.includes('group')){
        if(location.href.includes('?')){
            let param = this.location.href.split('?')[1];
            let params = param.split('&');
            var keys = [];
            params.forEach(async (data) => {       
                let key = data.split('=')[0]
                let value = data.split('=')[1]
                keys.push(key)
                if (key == "page") {
                    if (!isNaN(value)) {
                        if (value < 1) {
                            location.href = "/group?page=1"
                        }else{
                            await list_no_private_no_joined_group(value)
                        }
                    } else {
                        this.location.href = "/group?page=1"
                    }
                }
            })

            if (!keys.includes("page")){
                this.location.href = "/group?page=1"
            }
        }else{
            this.location.href = "/group?page=1"
        }
    }
})

import { clickEnter } from "./enterEvent.js";
import { send_alert } from "./alert.js";

const reg_email = /[a-zA-Z0-9]+@[a-z]+\.[a-z]{2,3}$/i;

var element_invite_group_button = document.createElement("button");
var element_invite_group_email_input = document.createElement("input");

clickEnter(element_invite_group_email_input, element_invite_group_button);

async function list(page) {

}