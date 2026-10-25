import { showNotification } from "./small_scripts/show_notification.js"

// function notify(message) {
//     const msgBox = document.getElementById('msgBox');
//     msgBox.textContent = message;
//     msgBox.classList.add('on');
//     setTimeout(() => msgBox.classList.remove('on'), 5000);
// }

let markAsReadButtons = document.querySelectorAll('.mark-read-btn');
let deleteButtons = document.querySelectorAll('.delete-btn');

markAsReadButtons.forEach(button => {
    button.addEventListener('click', () => {
        const id = button.getAttribute('data-message-id');
        markAsRead(id);
    });
});

deleteButtons.forEach(button => {
    button.addEventListener('click', () => {
        const id = button.getAttribute('data-message-id');
        deleteMessage(id);
    });
});

function markAsRead(id) {
    fetch(`/mark/message/read/${id}`, { method: 'POST', 
        headers: {
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
        }
     })
    .then(response => response.json())
    .then(data => {
        // notify(data.message);
        showNotification("Success", data.message);
        location.reload();
    })
    .catch(err => showNotification("Error", 'Error marking message as read'));
}

function deleteMessage(id) {
    if (confirm('Are you sure you want to delete this message?')) {
        fetch(`/delete/message/${id}`, { method: 'POST',
            headers: {
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
            }
         })
        .then(response => response.json())
        .then(data => {
            // notify(data.message);
            showNotification("Success", data.message);
            location.reload();
        })
        .catch(err => showNotification("Error", data.message));
    }
}

const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("active");
    }
)