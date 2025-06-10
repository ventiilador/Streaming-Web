// This module manages the video page

const params = new URLSearchParams(window.location.search);
const videoId = params.get("id");
const commentsBox = document.getElementById("comments-box");
const filterCombobox = document.getElementById("filter-combobox");
const video_like_button = document.getElementById("video-like-button");
const video_dislike_button = document.getElementById("video-dislike-button");
let channel_name;

// state variables
let offset = 0;
let isLoading = false;
let commentsEnded = false;

// We load the video from local storage (simulation)
document.getElementById("video").src = `media/videos/${videoId}.mp4`;

// This function renders the comments
function renderCommentForm() {
    return `
        <p id="comments-title">Comments</p>
        <div id="comment-input-box">
            <div id="comment-input-profile-image"></div>
            <input type="text" name="comment" id="comment-input" placeholder="Give your opinion">
            <button id="comment-send">Send</button>
        </div>
    `;
}

// Security
const escapeHTML = (str) => str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

// Here we fetch basic data
const get_video_data = () => {
    fetch("/API/video", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: videoId })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching data!");
        }
        return res.json();
    })
    .then(data => {
        document.getElementById("video-title").innerText = data.title;
        document.getElementById("channel-image").style.backgroundImage = `url(media/profile_pictures/${data.owner_id}.jpg)`;
        channel_name = data.owner_username;
        document.getElementById("channel-name").innerText = channel_name;
        document.getElementById("description").innerText = data.description;
        const subscribe_button = document.getElementById("subscribe-button");
        if (data.subscribed) {
            subscribe_button.innerText = "Subscribed";
            subscribe_button.style.backgroundColor = "#A9B0B3";
        } else {
            subscribe_button.innerText = "Subscribe";
            subscribe_button.style.backgroundColor = "#791F1F";
        }

        video_like_button.innerText = data.likes
        video_dislike_button.innerText = data.dislikes
        if (data.liked) {
            video_like_button.classList.add("like");
        } else {
            video_like_button.classList.remove("like");
        }
        
        if (data.disliked) {
            video_dislike_button.classList.add("dislike");
        } else {
            video_dislike_button.classList.remove("dislike");
        }
    })
    .catch(err => alert(err));
};

get_video_data();

// Here we manage like/dislike click events
video_like_button.addEventListener("click", () => {
    fetch("/API/like_video", {
        method: "POST",
        credentials: "include",
        headers: {
            "content-Type": "application/json"
        },
        body: JSON.stringify({
            id: videoId
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error like fetch");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
        get_video_data();
    })
    .catch(err => alert(err));
});

video_dislike_button.addEventListener("click", () => {
    fetch("/API/dislike_video", {
        method: "POST",
        credentials: "include",
        headers: {
            "content-Type": "application/json"
        },
        body: JSON.stringify({
            id: videoId
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error dislike fetch");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
        get_video_data();
    })
    .catch(err => alert(err));
});

// Here we manage the profile button
document.getElementById("channel-image").addEventListener("click", () => {
    window.location.href = `/profile?user=${channel_name}`;
});

// Here we manage the subscribe button
document.getElementById("subscribe-button").addEventListener("click", () => {
    fetch("/API/subscribe", {
        method: "POST",
        credentials: "include",
        headers: {
            "content-Type": "application/json"
        },
        body: JSON.stringify({
            id: videoId
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
        get_video_data();
    })
    .catch(err => alert(err));
});

// Here we manage the different click events in the comments box
commentsBox.addEventListener("click", (e) => {
    // Like event
    if (e.target.classList.contains("comment-like-button")){
        fetch("/API/like_comment", {
            method: "POST",
            credentials: "include",
            headers: {
                "content-Type": "application/json"
            },
            body: JSON.stringify({
                comment_id: e.target.dataset.id
            })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Error trying to like the comment");
            }
            return res.json();
        })
        .then(data => {
            if (data.like) {
                e.target.classList.add("like");
            } else {
                e.target.classList.remove("like");
            }
            reload_comments_section();
        })
        .catch(err => console.log(err))
    
    // Dislike event
    } else if (e.target.classList.contains("comment-dislike-button")) {
        fetch("/API/dislike_comment", {
            method: "POST",
            credentials: "include",
            headers: {
                "content-Type": "application/json"
            },
            body: JSON.stringify({
                comment_id: e.target.dataset.id
            })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Error dislike fetch");
            }
            return res.json();
        })
        .then(data => {
            if (data.dislike) {
                e.target.classList.add("dislike");
            } else {
                e.target.classList.remove("dislike");
            }
            reload_comments_section();
        })
        .catch(err => console.log(err));
    
    // Comment event
    } else if (e.target.id == "comment-send") {
        fetch("/API/comment", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                video_id: videoId,
                content: document.getElementById("comment-input").value
            })
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Error sending comment");
            }
            return res.json()
        })
        .then(data => {
            console.log(data);
            reload_comments_section();
        })
        .catch(err => console.log(err));

    } else if (e.target.classList.contains("user-image")) {
        window.location.href = `/profile?user=${e.target.dataset.username}`;
    }
})

// We reload the comments when the filter is changed
document.getElementById("comment-filter-container").addEventListener("change", (e) => {
    if (e.target.id === "filter-combobox") {
        reload_comments_section();
    }
});

// This function resets the state variables and reload all the comments
const reload_comments_section = () => {
    offset = 0;
    commentsEnded = false;
    commentsBox.innerHTML = renderCommentForm();
    get_comments(e.target.value);
};

// This function fetch the comments 30 by 30
const get_comments = (order) => {

    if (isLoading || commentsEnded) return;
    isLoading = true;

    fetch("/API/get_comments", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            video_id: videoId,
            offset: offset,
            order_by: order
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching comments");
        }
        return res.json()
    })
    .then(data => {
        let html = "";
        data.comments.forEach((comment) => {
            const safeContent = escapeHTML(comment.content);
            console.log(comment.liked);
            if (comment.liked) {
                html += `
                <div class="comment-container">
                    <div class="user-image" style="background-image: url(media/profile_pictures/${comment.owner_id}.jpg)" data-username="${comment.owner_username}"></div>
                    <p class="user-username">${comment.owner_username}</p>
                    <p class="comment-text">${safeContent}</p>
                    <i class="bi bi-hand-thumbs-up comment-like-button like" data-id="${comment.id}">${comment.likes}</i>
                    <i class="bi bi-hand-thumbs-down comment-dislike-button" data-id="${comment.id}">${comment.dislikes}</i>
                </div>
                `;
            } else if (comment.disliked) {
                html += `
                <div class="comment-container">
                    <div class="user-image" style="background-image: url(media/profile_pictures/${comment.owner_id}.jpg)" data-username="${comment.owner_username}"></div>
                    <p class="user-username">${comment.owner_username}</p>
                    <p class="comment-text">${safeContent}</p>
                    <i class="bi bi-hand-thumbs-up comment-like-button" data-id="${comment.id}">${comment.likes}</i>
                    <i class="bi bi-hand-thumbs-down comment-dislike-button dislike" data-id="${comment.id}">${comment.dislikes}</i>
                </div>
                `;
            }
            
            else {
                html += `
                <div class="comment-container">
                    <div class="user-image" style="background-image: url(media/profile_pictures/${comment.owner_id}.jpg)" data-username="${comment.owner_username}"></div>
                    <p class="user-username">${comment.owner_username}</p>
                    <p class="comment-text">${safeContent}</p>
                    <i class="bi bi-hand-thumbs-up comment-like-button" data-id="${comment.id}">${comment.likes}</i>
                    <i class="bi bi-hand-thumbs-down comment-dislike-button" data-id="${comment.id}">${comment.dislikes}</i>
                </div>
                `;
            }

        });
        commentsBox.innerHTML += html;
        if (!data.comments.length) {
            if (offset === 0) {
                commentsBox.innerHTML += "<p>No comments yet. Be the first!</p>";
            }
            commentsEnded = true;
        }
        offset += 30;
    })
    .catch(err => console.log(err))
    .finally(() => {
        isLoading = false;
    });
};


// When we arrive to de bottom we fetch the next offset comments once
window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const pageHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;

    if (scrollTop + windowHeight >= pageHeight - 100 && !isLoading) {
        get_comments(filterCombobox.value);
    }
});