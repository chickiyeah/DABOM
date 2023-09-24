window.addEventListener('DOMContentLoaded', async function() {
    verify_token()
})

function unregister() {
    fetch(`/api/user/unregister`, {
        method: 'POST'
    }).then(function(response) {
        if (response.status === 200) {
            localStorage.clear();
            location.href = "/"
        }
    })
}

async function verify_token() {
    return new Promise(async function(resolve, reject) {
        //토큰 검증
        fetch("/api/user/cookie/verify",{
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        }).then(async function(response) {
            if (response.status !== 200) {
                if (response.status === 422) {                   
                    await LoadCookie();
                    loading.style.display = 'none';
                }else if (response.status === 307) {
                    location.href = "/login";
                }else{
                    response.json().then(async (json) => {
                        let detail_error = json.detail;
                        console.log(detail_error)
                        if (detail_error.code == "ER998") {
                          await LoadCookie();
                        }
                    });
                }
            } else {
              response.json().then(async (json) => {
                loading.style.display = "none"
                resolve(json[1])
              })
            }
        })
    })
}