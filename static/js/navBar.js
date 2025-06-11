// we call this module to load the nav data

let username;
fetch("/API/home", {
    method: "GET",
    credentials: "include"
})
.then(res => {
    if (!res.ok) {
        throw new Error("Error fetching home data");
    }
    return res.json();
})
.then(data => {
    document.getElementById("profile-picture").style.backgroundImage = `url(/profile_picture/${data.user_id})`;
    username = data.username
})
.catch(err => alert(err));

const dropdown = document.getElementById("profile-dropdown");

document.addEventListener("click", (e) => {
    switch(e.target.id) {
        case "web-title":
            window.location.href = "/home";
            break;
        case "profile-picture":
            dropdown.classList.toggle("dropdown-active");
            break;
        case "dashboard":
            window.location.href = "/dashboard";
        case "my-profile":
            window.location.href = `/profile?user=${username}`;
            break;
        case "settings":
            window.location.href = "/settings";
            break;
        case "log-out":
            window.location.href = "/logout";
            break;
        default:
            dropdown.classList.remove("dropdown-active");
    };
});
