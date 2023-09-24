window.addEventListener('DOMContentLoaded', async function() {
    eat_avg(7)
})

function eat_avg(day) {
    var date = new Date();
    var cyoil = date.getDay()+1
    date.setDate(date.getDate() - day)
    var pyoil = date.getDay()+1
    
    if (cyoil != pyoil) {
        let deff = 0;
        let sum = "plus"
        if (cyoil > pyoil) {
            deff = cyoil - pyoil
            sum = "plus"
        }

        if (cyoil < pyoil) {
            deff = pyoil - cyoil
            sum = "minus"
        }

        if (sum === "plus") {
            date.setDate(date.getDate() + deff)
        }

        if (sum === "minus") {
            date.setDate(date.getDate() - deff)
        }
    }

    var year = date.getFullYear();
    var month = ("0" + (1 + date.getMonth())).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);

    let s_date = `${year}-${month}-${day}`;

    fetch(`/api/user/eat_avg/${s_date}`, {
        method: 'GET'
    }).then((response) => {
        response.json().then((data) => {
            console.log(data)
            let base_kcal = data.base_kcal
        })
    })
}