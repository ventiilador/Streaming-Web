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

document.addEventListener("click", (e) => {
    switch(e.target.id) {
        case "profile":
            showAndManageProfileSettings();
            break;
        case "cancel-button":
            showSettingsOptions();
        case "save-button":
            sendNewProfile();
    } 
});


