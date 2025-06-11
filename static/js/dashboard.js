const currentOptionContainer = document.getElementById("current-option-container");

document.addEventListener("click", (e) => {
    if (e.target.id == "submit-video-option") {
        currentOptionContainer.innerHTML = `
        <h2>Submit a Video</h2>
        <form method="post" id="video-form">
            <label for="title">Title</label>
            <input type="text" name="title" id="title-input">
            <label for="description">Description</label>
            <textarea name="description" id="description-input"></textarea>
            <button type="submit">Submit</button>
        </form>
        `
    }
});