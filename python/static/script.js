const socket = io();

// Get elements
const videoFeed = document.getElementById("video-feed");
const prevButton = document.getElementById("prev-button");
const nextButton = document.getElementById("next-button");

// Request new frame periodically
setInterval(() => {
    socket.emit("request_frame", {});
}, 30);

// Update video feed
socket.on("frame", (data) => {
    videoFeed.src = `data:image/jpeg;base64,${data.image}`;
});

// Handle button clicks
prevButton.addEventListener("click", () => {
    socket.emit("change_shirt", { direction: "prev" });
});

nextButton.addEventListener("click", () => {
    socket.emit("change_shirt", { direction: "next" });
});
