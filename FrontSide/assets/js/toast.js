let removeToast;

export function toast(string) {
    const toast = document.getElementById("toast");

    toast.classList.contains("reveal") ?
        (clearTimeout(removeToast), removeToast = setTimeout(function () {
            document.getElementById("toast").classList.remove("reveal")
        }, 1000)) :
        removeToast = setTimeout(function () {
            document.getElementById("toast").classList.remove("reveal")
        }, 2500)
    toast.classList.add("reveal"),
        toast.innerText = string
}

/** 상대 위치 조정 */

/*
const toast_s = document.getElementById("toast")

window.onresize = function() {
    const height = window.innerHeight;	
    
    let dh = height - 100
    toast_s.style.bottom = "auto"
    toast_s.style.top = dh + "px"
}
*/
