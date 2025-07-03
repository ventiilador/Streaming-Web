const settingsContainer = document.getElementById("settings-container");

const showSettingsOptions = () => {
    settingsContainer.innerHTML = `
    <h2>Settings</h2>
    <button id="profile">Profile</button>
    <button id="security">Security</button>
    <button id="privacity">Privacity</button>
    <button id="delete-account">Delete account</button>
    `;
};

showSettingsOptions();


const showAndManageProfileSettings = () => {
    settingsContainer.innerHTML = `
    <h2>Profile</h2>
    <div id="profile-image">
    </div>
    <input type="file" id="file-input" name="profile-image" accept=".jpg, .jpeg, .png">
    <label for="username">Username</label>
    <input type="text" name="username" id="username-input">
    <label for="biography">Biography</label>
    <input type="text" name="biography" id="biography-input">
    <button id="save-button">Save</button>
    <button id="cancel-button">Cancel</button>
    `;
    fetch("/profile_data", {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching profile data");
        }
        return res.json();
    })
    .then(data => {
        document.getElementById("username-input").value = data.username;
        document.getElementById("biography-input").value = data.biography;
        document.getElementById("profile-image").style.backgroundImage = `url("/profile_picture/${data.user_id}")`;
        document.getElementById("profile-image").addEventListener("click", () => {
            document.getElementById("file-input").click();
        });
        document.getElementById("file-input").addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            const imageUrl = URL.createObjectURL(file);
            document.getElementById("profile-image").style.backgroundImage = `url("${imageUrl}")`;
            document.getElementById("profile-image").style.backgroundSize = "cover";
            document.getElementById("profile-image").style.backgroundPosition = "center";
        }
});

    })
    .catch(err => console.log(err));
};

const sendNewProfile = () => {
    const formData = new FormData();
    formData.append("username", document.getElementById("username-input").value);
    formData.append("biography", document.getElementById("biography-input").value);
    formData.append("profile_picture", document.getElementById("file-input").files[0]);
    fetch("/update_profile", {
        method: "POST",
        credentials: "include",
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error trying to post new profile");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(err => console.log(err));
};

const showAndManageSecuritySettings = () => {
    settingsContainer.innerHTML = `
    <h2>Security</h2>
    <label>Current Password</label>
    <input type="password" name="current-password" id="current-password-input">
    <label>New Password</label>
    <input type="password" name="new-password" id="new-password-input">
    <label>Repeat New Password</label>
    <input type="password" name="repeat-new-password" id="repeat-new-password-input">
    <button id="change-password-button">Change</button>
    <button id="cancel-button">Cancel</button>
    <p id="error">Error</p>
    `;
};

const changePassword = () => {
    const current_password = document.getElementById("current-password-input").value;
    const new_password = document.getElementById("new-password-input").value;
    const repeat_new_password = document.getElementById("repeat-new-password-input").value;

    const errorMessage = document.getElementById("error");
    if (new_password !== repeat_new_password) {
        errorMessage.style.display = "block";
        errorMessage.innerText = "Passwords must be the same";
        return;
    }

    const formData = new FormData();
    formData.append("current_password", current_password);
    formData.append("new_password", new_password);

    fetch("/change_password", {
        method: "POST",
        credentials: "include",
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error updating password");
        }
        return res.json();
    })
    .then(data => {
        if (data.error) {
            errorMessage.style.display = "block";
            errorMessage.innerText = "incorrect password";
        }
    })
    .catch(err => console.log(err));
};

const showAndManagePrivacitySettings = () => {
    settingsContainer.innerHTML = `
    <h2>Privacity</h2>
    <label>Private Account</label>
    <input type="checkbox" id="private-account-input">
    <button id="change-privacity-button">Save</button>
    <button id="cancel-button">Cancel</button>
    `;
    fetch("/check_my_account_privacity", {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error fetching privacity data");
        }
        return res.json();
    })
    .then(data => {
        const checkbox = document.getElementById("private-account-input");
        if (data.privacity) {
            checkbox.checked = true;
        } else {
            checkbox.checked = false;
        }
    })
    .catch(err => console.log(err));
};

const changePrivacity = () => {
    privateAccount = document.getElementById("private-account-input").checked;
    fetch("/change_privacity_settings", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ private: privateAccount })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Error sending data");
        }
        return res.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(err => console.log(err));
};

const deleteAccount = () => {
    const result = confirm("Are you sure you want to delete your account?")
    if (result) {
        fetch("/delete_my_account", {
            method: "GET",
            credentials: "include"
        })
        .then(res => {
            if (!res.ok) {
                throw new Error("Error deleting your account")
            }
            return res.json();
        })
        .then(data => {
            console.log(data);
        })
        .catch(err => console.log(err));
    }
};

document.addEventListener("click", (e) => {
    switch(e.target.id) {
        case "profile":
            showAndManageProfileSettings();
            break;
        case "cancel-button":
            showSettingsOptions();
            break;
        case "save-button":
            sendNewProfile();
            break;
        case "security":
            showAndManageSecuritySettings();
            break;
        case "change-password-button":
            changePassword();
            break;
        case "privacity":
            showAndManagePrivacitySettings();
            break;
        case "change-privacity-button":
            changePrivacity();
            break;
        case "delete-account":
            deleteAccount();
            break;
    } 
});


