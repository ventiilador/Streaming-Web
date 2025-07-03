// This module fetch all the profile data
const params = new URLSearchParams(window.location.search);
let profile_username = params.get("user");
const subscribe_button = document.getElementById("subscribe-button");
const message = document.getElementById("no-videos-found");

const get_profile_data = () => {
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
        document.getElementById("user-image").style.backgroundImage = `url(profile_picture/${data.user.id})`;
        document.getElementById("username").innerText = data.user.username;
        document.getElementById("subscribers").innerText = `${data.user.subscribers} Subs`;
        document.getElementById("videos-container").innerHTML = "";
        console.log(data)
        try{
            data.videos.forEach((video) => {
                document.getElementById("videos-container").innerHTML += `
                <div class="video-card" data-id="${video.id}" style="background-image: url(/video_miniature/${video.id})"><p class="video-card-title">${video.title}</p></div>
                `
            });
        } catch (error) {
            console.log(error, "There are no videos");
        }
        if (data.user.subscribed) {
            subscribe_button.innerText = "Subscribed";
            subscribe_button.style.backgroundColor = "#A9B0B3";
        } else {
            subscribe_button.innerText = "Subscribe";
            subscribe_button.style.backgroundColor = "#791F1F";
        }
        if (data.user.followup) {
            console.log("DADWADWDADAW")
            subscribe_button.innerText = "Waiting...";
            subscribe_button.style.backgroundColor = "blueviolet";
        }
    })
    .catch(err => {
        
        message.style.display = "block";
        message.innerHTML = "<center><h2>There arent videos available</h2></center>";
    });
}

get_profile_data();

document.addEventListener("click", (e) => {
    if (e.target.id == "subscribe-button") {
        fetch("/API/subscribe_by_user", {
            method: "POST",
            credentials: "include",
            headers: {
                "content-Type": "application/json"
            },
            body: JSON.stringify({
                username: profile_username
            })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Error subscribing");
            }
            return res.json();
        })
        .then(data => {
            console.log(data);
            get_profile_data();
        })
        .catch(err => alert(err));
    } else if (e.target.classList.contains("video-card")){
        window.location.href = `/video?id=${e.target.dataset.id}`;
    }
});