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
    document.getElementById("profile-picture").style.backgroundImage = `url(media/profile_pictures/${data.user_id}.jpg)`;
    username = data.username
})
.catch(err => alert(err));

document.getElementById("profile-picture").addEventListener("click", () => {
    window.location.href = `/profile?user=${username}`;
});

document.getElementById("web-title").addEventListener("click", () => {
    window.location.href = "/home";
});