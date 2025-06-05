const params = new URLSearchParams(window.location.search);
const videoId = params.get("id");
const commentsBox = document.getElementById("comments-box");
const filterCombobox = document.getElementById("filter-combobox");

let offset = 0;
let isLoading = false;
let commentsEnded = false;

document.getElementById("video").src = `media/videos/${videoId}.mp4`;

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

const escapeHTML = (str) => str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");


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
    document.getElementById("channel-name").innerText = data.owner_username;
    document.getElementById("description").innerText = data.description;
})
.catch(err => alert(err));

commentsBox.addEventListener("click", (e) => {
    if (e.target.classList.contains("comment-like-button")){
        console.log(e.target.dataset.id);
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
        
    } else if (e.target.classList.contains("comment-dislike-button")) {
        console.log("Boton de dislike");
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
    }
})

document.getElementById("comment-filter-container").addEventListener("change", (e) => {
    if (e.target.id === "filter-combobox") {
        reload_comments_section();
    }
});

const reload_comments_section = () => {
    offset = 0;
    commentsEnded = false;
    commentsBox.innerHTML = renderCommentForm();
    get_comments(e.target.value);
};

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
                        <div class="user-image" style="background-image: url(media/profile_pictures/${comment.owner_id}.jpg)"></div>
                        <p class="user-username">${comment.owner_username}</p>
                        <p class="comment-text">${safeContent}</p>
                        <i class="bi bi-hand-thumbs-up comment-like-button like" data-id="${comment.id}">${comment.likes}</i>
                        <i class="bi bi-hand-thumbs-down comment-dislike-button" data-id="${comment.id}">${comment.dislikes}</i>
                    </div>
                `;
            } else {
                html += `
                <div class="comment-container">
                    <div class="user-image" style="background-image: url(media/profile_pictures/${comment.owner_id}.jpg)"></div>
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

window.addEventListener("scroll", () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const pageHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;

    if (scrollTop + windowHeight >= pageHeight - 100 && !isLoading) {
        get_comments(filterCombobox.value);
    }
});