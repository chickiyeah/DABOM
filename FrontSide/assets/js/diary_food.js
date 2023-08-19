//다이어리 음식 DB추가 관련 js

const barcode = document.querySelector('#f_d_barcode');
const name = document.querySelector('#f_d_name');
const f_type = document.querySelector('#f_d_type');
const kcal = document.querySelector('#f_d_kcal');
const f_submit = document.querySelector('#f_d_submit')
const weight = document.querySelector('#f_d_weight');

f_submit.addEventListener('click', (event) => {
    event.preventDefault();
    food_add();
})

import { toast } from "./toast.js";

function food_add() {
    
    let bar_ok = false;
    let barcode_v = barcode.value.trim()
    let name_v = name.value
    let f_type_v = f_type.value
    let kcal_v = kcal.value.trim()
    let weight_v = weight.value.trim()

    if (barcode_v === "") {
        if (!location.href.includes('manualy')) {
            toast("바코드를 입력해주세요");
        } else {
            if (isNaN(kcal_v)) {
                toast("칼로리는 숫자만 입력해야합니다.")
            } else if (kcal_v === "") {
                toast("칼로리를 입력해주세요.")
            } else {
                kcal_v = parseInt(kcal_v);
                if(weight_v === ""){
                    toast("음식의 무게를 입력해주세요.")
                } else if (isNaN(weight_v) ) {
                    toast("무게는 숫자만 입력해야합니다.")
                } else {
                    weight_v = parseInt(weight_v);
                    if (name_v.trim() === "") {
                        toast("음식의 이름을 입력해주세요.");
                    } else {
                        fetch("/api/food/add", {
                            method: "POST",
                            credentials: "include",
                            body: JSON.stringify({
                                "barcode": 0,
                                "name": name_v,
                                "category": f_type_v,
                                "kcal": kcal_v,
                                "weight": weight_v
                            })
                        }).then((response) => {
                            if (response.status === 200) {
                                response.json().then((json) => {
                                    let kcal_s = "해당 음식의 칼로리는 개당 "+kcal_v+" kcal 이며, 전체 칼로리는 "+kcal_v+" kcal 입니다."
                                    let html = `<div title="${kcal_s}" per="${kcal_v}" s_code="${json}" class="search_item">
                                        <a onclick="editamount(this.parentElement)" href="javascript:"><span>${name_v}</span><span class="amount" style="display:none;"> X <span class="amount_num">2</span></span></a>
                                        <a onclick="remove_ele(this.parentElement)" href="javascript:">
                                            <object data="/assets/images/close-icon.svg" type="image/svg+xml" aria-label="닫기아이콘"></object>
                                        </a>
                                    </div>`
                                    opener.opener.document.querySelector(".search_box").insertAdjacentHTML("beforeend", html)
                                    var q_tokcal = parseInt(opener.opener.document.querySelector("#tokcal").innerText) + parseInt(kcal_v);
                                    opener.opener.document.querySelector("#tokcal").innerText = q_tokcal;
                                    opener.close();
                                    window.close();
                                })
                            }
                        })
                    }
                }
            }
        }
    } else if (isNaN(barcode_v)) {
        toast("바코드는 숫자만 입력해야합니다.")
    } else {
        
        if (barcode_v.length != 13) {
            toast("바코드는 13글자 이어야만합니다.\n현재 길이 "+barcode_v.length)
        } else {
            barcode_v = parseInt(barcode_v);
            if (isNaN(kcal_v)) {
                toast("칼로리는 숫자만 입력해야합니다.")
            } else if (kcal_v === "") {
                toast("칼로리를 입력해주세요.")
            } else {
                kcal_v = parseInt(kcal_v);
                if(weight_v === ""){
                    toast("음식의 무게를 입력해주세요.")
                } else if (isNaN(weight_v) ) {
                    toast("무게는 숫자만 입력해야합니다.")
                } else {
                    weight_v = parseInt(weight_v);
                    if (name_v === "") {
                        toast("음식의 이름을 입력해주세요.");
                    } else {
                        fetch("/api/food/add", {
                            method: "POST",
                            credentials: "include",
                            body: JSON.stringify({
                                "barcode": barcode_v,
                                "name": name_v,
                                "category": f_type_v,
                                "kcal": kcal_v,
                                "weight": weight_v
                            })
                        }).then((response) => {
                            if (response.status === 200) {
                                response.json().then((json) => {
                                    let kcal_s = "해당 음식의 칼로리는 개당 "+kcal_v+" kcal 이며, 전체 칼로리는 "+kcal_v+" kcal 입니다."
                                    let html = `<div title="${kcal_s}" per="${kcal_v}" s_code="${json}" class="search_item">
                                        <a onclick="editamount(this.parentElement)" href="javascript:"><span>${name_v}</span><span class="amount" style="display:none;"> X <span class="amount_num">2</span></span></a>
                                        <a onclick="remove_ele(this.parentElement)" href="javascript:">
                                            <object data="/assets/images/close-icon.svg" type="image/svg+xml" aria-label="닫기아이콘"></object>
                                        </a>
                                    </div>`
                                    opener.opener.document.querySelector(".search_box").insertAdjacentHTML("beforeend", html)
                                    var q_tokcal = parseInt(opener.opener.document.querySelector("#tokcal").innerText) + parseInt(kcal_v);
                                    opener.opener.document.querySelector("#tokcal").innerText = q_tokcal;
                                    opener.close();
                                    window.close();
                                })
                            }
                        })
                    }
                }
            }
        }
    } 
}
