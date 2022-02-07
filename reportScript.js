function changeRank() {
    var input, filter, table, tr, td, i;
    input = document.getElementById("rankList");
    filter = input.value.charAt(0);
    table = document.getElementById("taxonomyTable");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
        td = tr[i].getElementsByClassName("rank");
        if (td) {
            if (td[0].innerHTML.toUpperCase().indexOf(filter) > -1 | filter == "A") {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}