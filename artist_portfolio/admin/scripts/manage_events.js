import { showNotification } from "./small_scripts/show_notification.js";

// function notify(message, type='success') {
//     const box = document.getElementById('notification');
//     box.textContent = message;
//     box.className = 'notification on ' + type;
//     setTimeout(() => box.classList.remove('on'), 3000);
// }

// let saveEventBtn = document.querySelector('.save-btn');
let deleteEventBtn = document.querySelector('.delete-btn');
let editEventBtn = document.querySelector('.edit-event-model');
let saveEventEditBtn = document.querySelector('.save-event-edit');
let createEventBtn = document.querySelector('.create-event');
let closeModalBtn = document.querySelector('.modal-close');
let editModal = document.getElementById('editModal');





function createNewEvent() {
    const title = document.getElementById('newTitle').value.trim();
    const description = document.getElementById('newDescription').value.trim();
    const date = document.getElementById('newDate').value;
    const time = document.getElementById('newTime').value;
    const venue = document.getElementById('newLocation').value.trim();
    const image_url = document.getElementById('newImageUrl').value.trim();

    if (!title || !date) {
        // notify('Title and date are required', 'error');
        showNotification("Error", 'Title and date are required');
        return;
    }

    fetch('/create/event', {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({title, description, date, time, location: venue, image_url})
    })
    .then(r => r.json())
    .then(j => {
        if (j.message.includes('created')) {
            notify('Event created! Refresh to see it.', 'success');
            document.getElementById('newTitle').value = '';
            document.getElementById('newDescription').value = '';
            document.getElementById('newDate').value = '';
            document.getElementById('newTime').value = '';
            document.getElementById('newLocation').value = '';
            document.getElementById('newImageUrl').value = '';
            setTimeout(() => window.location.reload(), 1500);
        } else {
            // notify(j.message, 'error');
            showNotification("Error", j.message);
        }
    })
    .catch(() => showNotification("Error", "Error creating event"));
}

createEventBtn.addEventListener('click', createNewEvent);


function editEventModal(id, title, date, time, location, description, image_url) {
    document.getElementById('editId').value = id;
    document.getElementById('editTitle').value = title;
    document.getElementById('editDate').value = date;
    document.getElementById('editTime').value = time;
    document.getElementById('editLocation').value = location;
    document.getElementById('editDescription').value = description;
    document.getElementById('editImageUrl').value = image_url;
    document.getElementById('editModal').classList.add('open');
}
editEventBtn.addEventListener('click', () => {
    const eventId = editEventBtn.getAttribute('data-event-id');
    const eventTitle = editEventBtn.getAttribute('data-event-title');
    const eventDate = editEventBtn.getAttribute('data-event-date');
    const eventTime = editEventBtn.getAttribute('data-event-time');
    const eventLocation = editEventBtn.getAttribute('data-event-location');
    const eventDescription = editEventBtn.getAttribute('data-event-description');
    const eventImageUrl = editEventBtn.getAttribute('data-event-image-url');
    editEventModal(eventId, eventTitle, eventDate, eventTime, eventLocation, eventDescription, eventImageUrl);
});


function closeEditModal() {
    document.getElementById('editModal').classList.remove('open');
}
closeModalBtn.addEventListener('click', closeEditModal);

function saveEventEdit() {
    const id = document.getElementById('editId').value;
    const title = document.getElementById('editTitle').value.trim();
    const description = document.getElementById('editDescription').value.trim();
    const date = document.getElementById('editDate').value;
    const time = document.getElementById('editTime').value;
    const venue = document.getElementById('editLocation').value.trim();
    const image_url = document.getElementById('editImageUrl').value.trim();

    if (!title || !date) {
        // notify('Title and date are required', 'error');
        showNotification("Error", 'Title and date are required');
        return;
    }

    fetch(`/edit/event/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({title, description, date, time, location: venue, image_url})
    })
    .then(r => r.json())
    .then(j => {
        // notify(j.message, 'success');
        showNotification("Success", j.message);
        closeEditModal();
        setTimeout(() => window.location.reload(), 1000);
    })
    .catch(() => showNotification("Error", "Error updating event"));
}

saveEventEditBtn.addEventListener('click', saveEventEdit);

function deleteEvent(id) {
    if (confirm('Are you sure you want to delete this event?')) {
        fetch(`/delete/event/${id}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            }
        })
        .then(r => r.json())
        .then(j => {
            // notify(j.message, 'success');
            showNotification("Success", j.message);
            setTimeout(() => location.reload(), 1000);
        })
        .catch(() => showNotification("Error", "Error deleting event"));
    }
}

deleteEventBtn.addEventListener('click', () => {
    const eventId = deleteEventBtn.getAttribute('data-event-id');
    deleteEvent(eventId);
});

const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("active");
    }
)