const mailbox = document.getElementById("mails");
const contactsBox = document.getElementById("contacts");

fetch("/get_mail_data", {
    method: "GET",
    credentials: "include"
})
.then(res => {
    if (!res.ok) {
        throw new Error("error fetching mail data");
    }
    return res.json();
})
.then(data => {
    let mailContent = "";
    if (data.follow_ups) {
        const followups = data.follow_ups;
        followups.forEach((followup) => {
            mailContent += `
            <div class="mail">
                <div class="followup-pfp" data-id="${followup.follower_username}" style="background-image: url('/profile_picture/${followup.follower_id}')"></div>
                <div class="info-container">
                    <p>The user ${followup.follower_username} wants to follow you</p>
                    <p style="color: blueviolet;">${followup.date}</p>
                </div>
                <i class="bi bi-check accept" data-id="${followup.id}" data-follower_id="${followup.follower_id}"></i>
                <i class="bi bi-x deny" data-id="${followup.id}"></i>
            </div>
            `;
        });
        mailbox.innerHTML = mailContent;
    }
})
.catch(err => alert(err));

fetch("/get_chats", {
    method: "GET",
    credentials: "include"
})
.then(res => {
    if (!res.ok) {
        throw new Error("error fetching mail data");
    }
    return res.json();
})
.then(data => {
    let contactsContent = "";
    if (data.contacts) {
        const contacts = data.contacts;
        contacts.forEach((contact) => {
            contactsContent += `
            <div class="contact" data-id="${contact.id}">
                <div class="contact-pfp" style="background-image: url('/profile_picture/${contact.id}')"></div>
                <div class="contact-info">
                    <p class="contact-username">${contact.username}</p>
                    <p class="contact-last-message">Último mensaje aquí...</p>
                </div>
            </div>
            `;
        });
        contactsBox.innerHTML = contactsContent;
    }
})
.catch(err => alert(err));

const acceptFollowUp = (follow_id, follower_id) => {
    fetch("/accept_follow", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: follow_id,
            follower_id: follower_id
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error accepting follower");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(err => console.log(err));
    window.location.reload();
};

const denyFollowUp = (follow_id) => {
    fetch("/deny_follow", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: follow_id,
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error deny follower");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(err => console.log(err));
    window.location.reload();
};

document.addEventListener("click", (e) => {
    if (e.target.classList.contains("followup-pfp")) {
        window.location.href = `/profile?user=${e.target.dataset.id}`;
    } else if (e.target.classList.contains("accept")) {
        acceptFollowUp(e.target.dataset.id, e.target.dataset.follower_id);
    } else if (e.target.classList.contains("deny")) {
        denyFollowUp(e.target.dataset.id);
    } else if (e.target.closest(".contact")) {
        const contactElement = e.target.closest(".contact");
        const contactId = contactElement.dataset.id;
        window.location.href = `/chat?user=${contactId}`;
    }
})