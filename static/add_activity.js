
function changeForm() {
    let currForm = document.querySelector("#forms").value;

    let entryForms = document.getElementsByClassName("entry_form");

    for (let i = 0; i < entryForms.length; i++) {
        if (entryForms[i].id == currForm) {
            entryForms[i].hidden = false;
            continue;
        }
        entryForms[i].hidden = true;

    }

    let checkboxes = document.getElementsByClassName("checkbox");
    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].setAttribute("form", currForm + "_form");
    }

    let leader = document.getElementById("leader");
    let leaderDiv = document.getElementById("leaderDiv");

    leader.setAttribute("form", currForm + "_form");
    if (currForm != "leadership") {
        console.log("hide leadership");
        leaderDiv.hidden = false;
        leader.disabled = false;
    } else {
        leaderDiv.hidden = true;
        leader.disabled = true;
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

function submitProject() {
    let activity = document.querySelector("#p-activity").value;
    if (activity === "") {
        return false;
    }

    return true;

}