// This module manages the login field requierements
const params = new URLSearchParams(window.location.search);
const error = params.get("error");
const errorText = document.getElementById("error");
if (error){
    errorText.style.display = "block";
    switch(error) {
        case "1":
            errorText.innerText = `
            Username max length: 20char
            Password max length: 64char
            The fields cannot be empty
            `;
            break;
        case "2":
            errorText.innerText = `
            Incorrect credentials
            `
            break;
    }
}