import { showNotification } from "./small_scripts/show_notification.js";

let deleteImg = document.querySelectorAll('.delete-img');
let deleteVid = document.querySelectorAll('.delete-vid');
let uploadImgBtn = document.querySelector('.upload-img');
let addVidBtn = document.querySelector('.add-vid');

deleteImg.forEach(button => {
    button.addEventListener('click', () => {
        const imageId = button.getAttribute('data-image-id');
        deleteItem(imageId);
    });
});

deleteVid.forEach(button => {
    button.addEventListener('click', () => {
        const videoId = button.getAttribute('data-vid-id');
        deleteItem(videoId);
    }); 
});

uploadImgBtn.addEventListener('click', () => {
    uploadImage();
});

addVidBtn.addEventListener('click', () => {
    addVideo();
});


function uploadImage() {
    const fileInput = document.getElementById('imageFile');
    const title = document.getElementById('imageTitle').value;

    if (!fileInput.files[0]) {
        // notify('Please select an image file');
        showNotification("Error", "Please select an image file.")
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('title', title);

    fetch('/upload/gallery/image', {
        method: 'POST',
        headers: {
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // notify(data.message);
        showNotification("Success", data.message);
        if (data.message.includes('uploaded')) {
            location.reload();
        }
    })
    .catch(err => {
        // notify('Error uploading image');
        showNotification("Error", "Error uploading image");
    });
}

function addVideo() {
    const url = document.getElementById('videoUrl').value.trim();
    const title = document.getElementById('videoTitle').value;

    console.log('the url is ', url);
    console.log('the title is ', title);

    if (!url) {
        // notify('Please enter a YouTube URL');
        showNotification("Error", "Please enter a YouTube URL");
        return;
    }

    fetch('/add/gallery/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
         },
        body: JSON.stringify({ url: url, title: title })
    })
    .then(response => response.json())
    .then(data => {
        // notify(data.message);
        showNotification("Success", data.message);
        if (data.message.includes('added')) {
            document.getElementById('videoUrl').value = '';
            document.getElementById('videoTitle').value = '';
            location.reload();
        }
    })
    .catch(err => {
        // notify('Error adding video');
        showNotification("Error", "Error adding video");
    });
}

function deleteItem(id) {
    if (confirm('Are you sure you want to delete this item?')) {
        fetch(`/delete/gallery/item/${id}`, { 
            method: 'POST',
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content

         })
        .then(response => response.json())
        .then(data => {
            // notify(data.message);
            showNotification("Success", data.message);
            location.reload();
        })
        .catch(err => {
            showNotification("Error", "Error deleting item");
        });
    }
}

const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
navLinks.classList.toggle("active");
}
)