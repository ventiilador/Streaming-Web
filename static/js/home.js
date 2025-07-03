const homeContainer = document.getElementById("main-container");

let homeOffset = 0;
let homeIsLoading = false;
let homeEnded = false;

function loadHomeVideos() {
    if (homeIsLoading || homeEnded) return;
    homeIsLoading = true;

    fetch(`/API/home_varied_search?offset=${homeOffset}&limit=30`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (!res.ok) throw new Error("Error loading videos");
        return res.json();
    })
    .then(data => {
        const videos = data.videos;
        if (!videos || videos.length === 0) {
            homeEnded = true;
            return;
        }

        let html = "";
        videos.forEach(video => {
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
        homeContainer.innerHTML += html;
        homeOffset += videos.length;
    })
    .catch(err => {
        console.error(err);
    })
    .finally(() => {
        homeIsLoading = false;
    });
}

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const pageHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;

    if (scrollTop + windowHeight >= pageHeight - 100 && !homeIsLoading) {
        loadHomeVideos();
    }
});

// Primera carga
loadHomeVideos();
