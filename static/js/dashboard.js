// Main container declaration
const currentOptionContainer = document.getElementById("current-option-container");

// This function shows and manages all the events in the upload video form
const showSubmitVideoOption = () => {
    // Shows the form
    currentOptionContainer.style.gridTemplateColumns = "1fr 2fr";
    currentOptionContainer.innerHTML = `
        <form method="post" id="video-form">
            <h2 class="section-titles">Submit a Video</h2>
            <div id="video-form-container">
                <label for="title">Title</label>
                <input class="section-inputs" type="text" name="title" id="title-input" required>
                <label for="description">Description</label>
                <textarea class="section-inputs" name="description" id="description-input" required></textarea>
                <button type="submit" id="submit-video-button">Submit</button>
            </div>
        </form>
        <div id="files-container">
            <h3>Video</h3>
            <label for="video-input" class="custom-file-upload" id="video-input-label">
                📁 Upload Video
            </label>
            <input type="file" name="video" id="video-input" class="file-input" accept="video/mp4, video/quicktime, video/x-matroska, video/x-msvideo, video/webm" style="display:none;" required />
            <h3>Optional Miniature</h3>
            <label for="miniature-input" class="custom-file-upload" id="miniature-input-label">
                📁 Upload Miniature
            </label>
            <input type="file" name="miniature" id="miniature-input" class="file-input" accept="image/jpeg, image/png, image/webp" />
        </div>
        <div id="error-message" style="color:red;display:none;"></div>
    `;

    // Declarates all the form components
    const videoInput = document.getElementById("video-input");
    const miniatureInput = document.getElementById("miniature-input");
    const videoLabel = document.getElementById("video-input-label");
    const miniatureLabel = document.getElementById("miniature-input-label");
    const form = document.getElementById("video-form");
    const errorMessage = document.getElementById("error-message");

    // We associate the click of the labels with the ugly input tags
    videoLabel.addEventListener("click", () => videoInput.click());
    miniatureLabel.addEventListener("click", () => miniatureInput.click());

    // When we select a video file
    videoInput.addEventListener("change", () => {
        // We check if it exists
        const file = videoInput.files[0];
        if (!file) return;

        // We check if it is less than 10GB
        const maxSize = 10 * 1024 * 1024 * 1024;
        if (file.size > maxSize) {
            alert("Video max weight is 10 GB");
            videoInput.value = "";
            videoLabel.style.backgroundImage = "";
            videoLabel.textContent = "📁 Upload Video";
            return;
        }

        // Here we convert the video to make an automatic miniature + put the image on the label
        const url = URL.createObjectURL(file);
        const video = document.createElement("video");
        video.src = url;
        video.muted = true;
        video.playsInline = true;
        video.addEventListener("loadeddata", () => {
            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imgDataUrl = canvas.toDataURL("image/jpeg");
            window.generatedTh = imgDataUrl;
            videoLabel.style.backgroundImage = `url(${imgDataUrl})`;
            videoLabel.textContent = "";
            URL.revokeObjectURL(url);
        });
        video.load();
        video.play().catch(() => {});
    });

    //When we chose a miniature image
    miniatureInput.addEventListener("change", () => {
        // We check if it exists
        const file = miniatureInput.files[0];
        if (!file) return;
        
        // We check if its less than 200MB
        const maxSize = 200 * 1024 * 1024;
        if (file.size > maxSize) {
            alert("Miniature max size is 200MB");
            miniatureInput.value = "";
            miniatureLabel.style.backgroundImage = "";
            miniatureLabel.textContent = "📁 Upload Miniature";
            return;
        }

        // We put the image in the label
        const reader = new FileReader();
        reader.onload = (e) => {
            miniatureLabel.style.backgroundImage = `url(${e.target.result})`;
            miniatureLabel.textContent = "";
        };
        reader.readAsDataURL(file);
    });

    // When we click at the submit button
    form.addEventListener("submit", async (e) => {
        // We dont send the form
        e.preventDefault();

        // We create an formData
        const formData = new FormData();
        const title = document.getElementById("title-input").value;
        const description = document.getElementById("description-input").value;
        const video = videoInput.files[0];
        const miniature = miniatureInput.files[0];

        // We check if there is a video
        if (!video) {
            alert("You must upload a video.");
            return;
        }
        
        // we add our fields values
        formData.append("title", title);
        formData.append("description", description);
        formData.append("video", video);

        // We user the custom miniature if there is one
        if (miniature) {
            formData.append("miniature", miniature);
        } else if (window.generatedTh) {
            const blob = dataURLtoBlob(window.generatedTh);
            formData.append("miniature", blob, "autogenerated-thumbnail.jpg");
        }

        // We send the data to de Backend
        const res = await fetch("/API/upload_video", {
            method: "POST",
            credentials: "include",
            body: formData,
        });

        // We convert the response to a JSON and check if there is an error to show it
        const result = await res.json();
        if (result.error) {
            const error = result.error;
            // All the errors
            switch(error) {
                case 1:
                    errorMessage.innerText = "The Title must be between 4 and 24 chars";
                    break;
                case 2:
                    errorMessage.innerText = "The Description must be between 5 and 400 chars";
                    break;
                case 3:
                    errorMessage.innerText = "The video format is incorrect";
                    break;
                case 4:
                    errorMessage.innerText = "The video cannot weigh more than 10GB";
                    break;
                case 5:
                    errorMessage.innerText = "The miniature format is incorrect";
                    break;
                case 6:
                    errorMessage.innerText = "The miniature cannot weigh more than 200MB";
                    break;
                default:
                    errorMessage.innerText = "An unknown error occurred";
            }
            errorMessage.style.display = "block";
            if (error < 5) showSubmitVideoOption();
        } else {
            errorMessage.style.display = "none";
            alert(result.success);
            window.location.href = "/home";
        }
    });
};

const showManageVideosOption = () => {
    currentOptionContainer.style.gridTemplateColumns = "1fr";
    let html = `
    <h2>My videos</h2>
    `;
    
    fetch("/API/my_videos", {
        method: "GET",
        credentials: "include",
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching my videos");
        }
        return res.json();
    })
    .then(data => {
        if (data.error) {
            html += "<h3>You dont have videos yet.</h3>";
        } else {
            data.videos.forEach((video) => {
                html += `
                <div class="video-card">
                    <div class="miniature" style="background-image: url('/video_miniature/${video.id}');"></div>

                    <div class="video-info">
                    <p class="video-title">${video.title}</p>
                    <p class="video-description">${video.description}</p>
                    </div>

                    <div class="video-stats">
                    <p>👍 ${video.likes}</p>
                    <p>👎 ${video.dislikes}</p>
                    <p>👁️ ${video.views ?? 0}</p>
                    </div>

                    <i class="bi bi-pencil edit-icon" data-id="${video.id}" title="Editar video"></i>
                </div>
                `;
            });
        }
        currentOptionContainer.innerHTML = html;
    })
    .catch(err => console.log(err));
};

// Here we manage the different clicks in the options dial
document.getElementById("options-dial").addEventListener("click", (e) => {
    switch(e.target.id){
        case "submit-video-option":
            showSubmitVideoOption();
            break;
        case "manage-video-option":
            showManageVideosOption();
            break;
    }

});

document.addEventListener("click", (e) => {
    if (e.target.classList.contains("edit-icon")) {
        window.location.href = `/edit_video?id=${e.target.dataset.id}`;
    }
})


// This function transform the urlimage to an normal image
function dataURLtoBlob(dataURL) {
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

showSubmitVideoOption();