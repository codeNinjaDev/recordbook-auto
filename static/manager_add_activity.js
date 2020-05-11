
function changeForm() {
    let currForm = document.querySelector("#forms").value;

    var entryForms = document.getElementsByClassName("entry_form");
    var checkboxes = document.getElementsByClassName("checkbox");


    for (let i = 0; i < entryForms.length; i++) {
        if (entryForms[i].id == currForm) {
            entryForms[i].hidden = false;
            continue;
        }
        entryForms[i].hidden = true;
    }

    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].form = currForm + "_form";
    }



}

function submitLeadership() {
    let activity = document.querySelector("#l-activity").value;
    if (activity === "") {
        return false;
    }

    return true;

}

function submitService() {
    let activity = document.querySelector("#s-activity").value;
    if (activity === "") {
        return false;
    }

    return true;

}

function submitAward() {
    let activity = document.querySelector("#a-recognition").value;
    if (activity === "") {
        return false;
    }

    return true;

}

function submitCareer() {
    let activity = document.querySelector("#c-activity").value;
    if (activity === "") {
        return false;
    }

    return true;

}