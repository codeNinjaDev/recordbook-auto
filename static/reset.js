

function validate() {
    let oldPassword = document.querySelector("#oldPassword").value;
    let newPassword = document.querySelector("#newPassword").value;
    let confirm = document.querySelector("#confirmPassword").value;
    let submit = document.querySelector("#submit");

    let validated = true;
    if (username === "") {
        document.querySelector("#oldFail").hidden = false;
        validated = false;
    } else {
        document.querySelector("#oldFail").hidden = true;
    }

    if (password === "") {
        document.querySelector("#newFail").hidden = false;
        validated = false;
    } else {
        document.querySelector("#newFail").hidden = true;
    }

    if (password != confirm) {
        document.querySelector("#confirmPasswordFail").hidden = false;
        validated = false;
    } else {
        document.querySelector("#confirmPasswordFail").hidden = true;
    }

    return validated;

}