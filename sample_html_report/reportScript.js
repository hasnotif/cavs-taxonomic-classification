function changeRank() {
    var input, filter, table, tr, td, i;
    input = document.querySelector("#rankList");
    filter = input.value.charAt(0);
    table = document.querySelector("#taxonomyTable");
    tr = table.querySelectorAll("tr");
    for (i = 1; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        rank = td[2];
        if (rank.innerHTML.indexOf(filter) > -1 | filter == "A") {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}

// only comparing numbers for now
function compareValuesAsc(a, b) {
    let num_a = Number(a);
    let num_b = Number(b);
    return (num_a<num_b) ? -1 : (num_a>num_b) ? 1 : 0;
}

function compareValuesDesc(a, b) {
    let num_a = Number(a);
    let num_b = Number(b);
    return (num_a>num_b) ? -1 : (num_a<num_b) ? 1 : 0;
}

// 1st click: ascending order; 2nd click: descending order; subsequent clicks alternate the order
function sortTable(n) {
    let table = document.querySelector("#taxonomyTable");
    let rows = Array.from(table.querySelectorAll("tr"));
    rows = rows.slice(1);
    let header = document.querySelectorAll("th")[parseInt(n)];
    var order = header.getAttribute("data-order");
    let td;
    if (n === "0") {
        td = "#name";
    } else if (n === "1") {
        td = "#taxid";
    } else if (n === "2") {
        td = "#rank";
    } else if (n === "3") {
        td = "#percentage";
    } else if (n === "4") {
        td = "#num_cover";
    } else if (n === "5") {
        td = "#num_direct";
    }
    rows.sort((r1,r2) => {
        let t1 = r1.querySelector(td);
        let t2 = r2.querySelector(td);
        if (order === "asc") {
            return compareValuesDesc(t1.textContent, t2.textContent);
        } else {
            return compareValuesAsc(t1.textContent, t2.textContent);
        }
    });
    rows.forEach(row => table.appendChild(row));
    if (order === "asc") {
        header.setAttribute("data-order", "desc");
    } else {
        header.setAttribute("data-order", "asc");
    }
}

// EVENT LISTENERS
// 1) select rank
document.querySelector(`select.form-control`).addEventListener(`change`, evt => changeRank());
// 2) sort table
let table = document.querySelector("#taxonomyTable");
let rankable = table.querySelectorAll("th.rankable");
for (var i=0; i<rankable.length; i++) {
    let col = rankable[i].getAttribute("id");
    rankable[i].addEventListener(`click`, evt => sortTable(col));
}

