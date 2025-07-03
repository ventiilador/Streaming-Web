const params = new URLSearchParams(window.location.search);
const contactId = params.get("user");
let contactUsername;
const socket = new WebSocket("ws://localhost:8000/ws/chat");
const presenceSocket = new WebSocket("ws://localhost:8000/ws/presence");
const chat = document.getElementById("chat-messages");
let lastDistance = 0;
let offset = 0;

presenceSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.user_id == contactId) {
        const statusText = document.getElementById("active");
        if (!statusText) return;
        if (data.status) {
            statusText.innerText = "Online";
            statusText.style.color = "green";
        } else {
            statusText.style.color = "black";
            update_contact_data();
        }
    }
};

const update_contact_data = () => {
    fetch("/get_contact_data", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: contactId,
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching contact data");
        }
        return res.json();
    })
    .then(data => {
        contactUsername = data.username;
        document.getElementById("chat-header").innerHTML = `
        <div id="chat-pfp" style="background-image: url(/profile_picture/${contactId})"></div>
        <div id="chat-contact-info">
            <h3>${contactUsername}</h3>
            <p id="active">Last time active ${data.active}</p>
        </div>
        `;
    })
    .catch(err => console.log(err));
};

update_contact_data();

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.author == contactId) {
        chat.innerHTML += `
        <div class="message received">
            <div class="msg-pfp" style="background-image: url('/profile_picture/${contactId}')"></div>
            <div class="msg-content">
                <p>${data.content}</p>
                <span class="msg-time">${data.date}</span>
            </div>
        </div>
        `;
    } else {
        chat.innerHTML += `
        <div class="message sent">
            <div class="msg-content">
                <p>${data.content}</p>
                <span class="msg-time">${data.date}</span>
            </div>
        </div>
        `;
    }
    chat.scrollTop = chat.scrollHeight;
};


const get_chat = async () => {
    const res = await fetch("/API/chat", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            destination_id: contactId,
            offset: offset
        })
    });

    if (!res.ok) {
        throw new Error("Error fetching chat data");
    }

    const data = await res.json();

    if (data.messages) {
        let currentHTML = chat.innerHTML;
        data.messages.forEach((message) => {
            if (message.self) {
                currentHTML = `
                <div class="message sent">
                    <div class="msg-content">
                        <p>${message.content}</p>
                        <span class="msg-time">${message.date}</span>
                    </div>
                </div>
                ` + currentHTML;
            } else {
                currentHTML = `
                <div class="message received">
                    <div class="msg-pfp" style="background-image: url('/profile_picture/${contactId}')"></div>
                    <div class="msg-content">
                        <p>${message.content}</p>
                        <span class="msg-time">${message.date}</span>
                    </div>
                </div>
                ` + currentHTML;
            }
        });

        chat.innerHTML = currentHTML;
        offset += 30;
        return;
    }
};

get_chat().then(() => {
    chat.scrollTop = chat.scrollHeight;
});

chat.addEventListener('scroll', () => {
    const maxScrollTop = chat.scrollHeight - chat.clientHeight;
    const distanceScrolledUp = maxScrollTop - chat.scrollTop;

    if (lastDistance + 10 < distanceScrolledUp) {
        get_chat();
        lastDistance = distanceScrolledUp;
    }
});

const send_message = () => {
    chatInput = document.getElementById("chat-input");
    if (!chatInput.value.trim()) return;
    
    fetch("/API/send_message", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            destination_id: contactId,
            content: chatInput.value
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching chat data");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(err => alert(err));
    chatInput.value = "";
};

document.addEventListener("click", (e) => {
    const sendButton = e.target.closest("#send-button");
    if (sendButton) {
        send_message();
    }
    const pfpImage = e.target.closest("#chat-pfp");
    if (pfpImage) {
        window.location.href = `/profile?user=${contactUsername}`;
    }
})