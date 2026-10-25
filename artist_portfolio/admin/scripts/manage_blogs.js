import { showNotification } from "./small_scripts/show_notification.js";

let editingId = null;
let saveBtn = document.getElementById('saveBtn');
let editButtons = document.querySelectorAll('.edit-btn');
editButtons.forEach(button => {
    button.addEventListener('click', () => {
        editBlogFromButton(button);
    });
});
let deleteButtons = document.querySelectorAll('.delete-btn');
deleteButtons.forEach(button => {
    button.addEventListener('click', () => {
        const id = button.dataset.id;
        deleteBlog(id);
    });
});

function editBlogFromButton(button) {
    const id = button.dataset.id;
    const title = button.dataset.title;
    const excerpt = button.dataset.excerpt;
    const content = button.dataset.content;

    editingId = id;
    document.getElementById('formTitle').textContent = 'Edit Blog';
    document.getElementById('blogTitle').value = title;
    document.getElementById('blogExcerpt').value = excerpt;
    document.getElementById('blogContent').value = content;
    document.getElementById('saveBtn').textContent = 'Update Blog';
}

function saveBlog() {
    const title = document.getElementById('blogTitle').value;
    const excerpt = document.getElementById('blogExcerpt').value;
    const content = document.getElementById('blogContent').value;

    if (!title || !excerpt || !content) {
        showNotification("Error", 'All fields are required');
        return;
    }

    const url = editingId ? `/edit/blog/${editingId}` : '/create/blog';
    const method = 'POST';

    fetch(url, {
        method: method,
        headers: { 
            'Content-Type': 'application/json',
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
            },
        body: JSON.stringify({ title, excerpt, content })
    })
    .then(response => response.json())
    .then(data => {
        showNotification("Success", data.message);
        if (data.message.includes('created') || data.message.includes('updated')) {
            location.reload();
        }
    })
    .catch(err => showNotification("Error", 'Error saving blog'));
}

function deleteBlog(id) {
    if (confirm('Are you sure you want to delete this blog?')) {
        fetch(`/delete/blog/${id}`, { method: 'POST',
            headers:{
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
            }
            })
        .then(response => response.json())
        .then(data => {
            showNotification("Success", data.message);
            location.reload();
        })
        .catch(err => showNotification("Error", 'Error deleting blog'));
    }
}

const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
        navLinks.classList.toggle("active");
        }
    )

saveBtn.addEventListener('click', saveBlog);