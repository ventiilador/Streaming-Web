// This module fetch all the profile data

const params = new URLSearchParams(window.location.search);
let profile_username = params.get("user");

fetch("/API/profile", {
    method: "POST",
    credentials: "include",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ username: profile_username })
})
.then(res => {
    if (!res.ok){
        throw new Error("Error trying to fetch profile data");
    }
    return res.json();
})
.then(data => {
    document.getElementById("user-image").style.backgroundImage = `url(media/profile_pictures/${data.user.id}.jpg)`;
    document.getElementById("username").innerText = data.user.username;
    data.videos.forEach((video) => {
        document.getElementById("videos-container").innerHTML += `
        <div class="video-card" data-id="${video.id}" style="background-image: url(media/miniatures/${video.id}.jpg)"><p class="video-card-title">${video.title}</p></div>
        `
    });
})
.catch(err => {
    document.getElementById("profile-container").innerHTML += "<center><h2>There arent videos available</h2></center>"
});

document.getElementById("videos-container").addEventListener("click", (e) => {
    if (e.target.classList.contains("video-card")) {
        window.location.href = `/video?id=${e.target.dataset.id}`;
    }
});