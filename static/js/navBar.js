// we call this module to load the nav data
let query = "";
let searchOffset = 0;
let isLoadingSearch = false;
let searchEnded = false
const mainContainer = document.getElementById("main-container");

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

const search = () => {
    isLoadingSearch = true;
    let formData = new FormData();
    formData.append("search", query);
    formData.append("filter", document.getElementById("content-filter").value);
    formData.append("type", document.getElementById("content-type").value);
    formData.append("offset", searchOffset);

    fetch("/search", {
        method: "POST",
        credentials: "include",
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error searching");
        }
        return res.json();
    })
    .then(data => {
        let html = "";
        if (data.videos) {
            if (!data.videos.length) {
                searchEnded = true;
            }
            data.videos.forEach((video) => {
                html += `
                <div class="video-card" data-id="${video.id}">
                    <img src="/video_miniature/${video.id}" alt="Video Title" class="thumbnail">
                    <div class="video-info">
                        <h3 class="video-title">${video.title}</h3>
                        <p class="video-channel">${video.owner}</p>
                        <p class="video-meta">${video.views} views | uploaded ${video.upload_date}</p>
                    </div>
                </div>`;
            });
        }

        if (data.channels) {
            if (!data.channels.length) {
                searchEnded = true;
            }
            data.channels.forEach((channel) => {
                html += `
                <div class="channel-card" data-username="${channel.username}">
                    <img src="/profile_picture/${channel.id}" alt="${channel.username}" class="channel-picture">
                    <div class="channel-info">
                        <h3 class="channel-name">${channel.username}</h3>
                        <p class="channel-subs">${channel.subscribers_count} subscribers</p>
                        <p class="channel-description">${channel.biography || ""}</p>
                    </div>
                </div>`;
            });
        }

        mainContainer.innerHTML += html;
        searchOffset += 30;
    })
    .catch(err => console.log(err))
    .finally(() => {
        isLoadingSearch = false;
    });
};


document.addEventListener("click", (e) => {
    switch(e.target.id) {
        case "web-title":
            window.location.href = "/home";
            break;
        case "search-button":
            query = document.getElementById("search-input").value;
            mainContainer.innerHTML = "";
            Object.assign(mainContainer.style, {
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
                gap: "20px",
                padding: "20px",
            });
            search();
            break;
        case "profile-picture":
            dropdown.classList.toggle("dropdown-active");
            break;
        case "dashboard":
            window.location.href = "/dashboard";
            break;
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
            break;
    };
    const videoCard = e.target.closest(".video-card");
    if (videoCard) {
        window.location.href = `/video?id=${videoCard.dataset.id}`;
    }
    const channelCard = e.target.closest(".channel-card");
    if (channelCard) {
        window.location.href = `/profile?user=${channelCard.dataset.username}`;
    }
});

document.getElementById("content-filter").addEventListener("change", () => {
    mainContainer.innerHTML = "";
    searchOffset = 0;
    searchEnded = false;
    search();
});

document.getElementById("content-type").addEventListener("change", () => {
    mainContainer.innerHTML = "";
    searchOffset = 0;
    searchEnded = false;
    search();
});

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const pageHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;

    if (scrollTop + windowHeight >= pageHeight - 100 && !isLoadingSearch && !searchEnded) {
        search();
    }
});