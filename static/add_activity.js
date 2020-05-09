
function changeForm() {
    let currForm = document.querySelector("#forms").value;

    var entryForms = document.getElementsByClassName("entry_form");

    for (let i = 0; i < entryForms.length; i++) {
        if (entryForms[i].id == currForm) {
            entryForms[i].hidden = false;
            continue;
        }
        entryForms[i].hidden = true;

    }

}

function submitLeadership() {
    let activity = document.querySelector("#l-activity").value;
    if (activity === "") {
        return false;
    }
    
    return true;

}