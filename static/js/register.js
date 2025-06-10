// This module manages the register field requierements

const params = new URLSearchParams(window.location.search);
const error = params.get("error");
const errorText = document.getElementById("error");
if (error){
    errorText.style.display = "block";
    switch(error) {
        case "1":
            errorText.innerText = `
            Username must be between 4 and 20 char
            Email must be between 6 and 254 char
            Password must be between 8 and 64 char
            The fields cannot be empty
            `;
            break;
        case "2":
            errorText.innerText = `
            There is already an user with that username / email
            `
            break;
        case "3":
            errorText.innerText = `
            Passwords must be the same
            `
            break;
    }
}

document.querySelector("form").addEventListener("submit", (event) => {
    const password1 = document.getElementById("password-input").value;
    const password2 = document.getElementById("password-repeat-input").value;

    if (password1 != password2) {
        event.preventDefault();
        window.location.href = "/register?error=3";
    }
});