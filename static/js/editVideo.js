const params = new URLSearchParams(window.location.search);
videoId = params.get("id");
errorMessage = document.getElementById("error-message");
error = params.get("error");
if (error) {
    errorMessage.style.display = "block";
    switch(error){
        case "1":
            errorMessage.innerText = "The Title must be between 4 and 24 chars";
            break;
        case "2":
            errorMessage.innerText = "The Description must be between 5 and 400 chars";
            break;
        case "3":
            errorMessage.innerText = "The miniature format is incorrect";
            break;
        case "4":
            errorMessage.innerText = "The miniature cannot weigh more than 200MB";
            break;
        default:
            errorMessage.innerText = "An unknown error occurred";
    }
}

fetch("/API/get_video_edit_form", {
    method: "POST",
    credentials: "include",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        id: videoId
    })
})
.then(res => {
    if (!res.ok) {
        throw new Error("Error fetching form data");
    }
    return res.json();
})
.then(data => {
    document.getElementById("title-input").value = data.title;
    document.getElementById("description-input").value = data.description;
    document.getElementById("miniature-input-label").style.backgroundImage = `url("/video_miniature/${videoId}")`;
    document.getElementById("id-input").value = videoId;
})
.catch(err => console.log(err));