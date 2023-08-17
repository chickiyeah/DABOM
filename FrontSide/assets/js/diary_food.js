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
                            console.log(response);
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
                            console.log(response);
                        })
                    }
                }
            }
        }
    } 
}
