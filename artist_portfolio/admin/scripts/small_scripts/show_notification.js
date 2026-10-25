export function showNotification(type, message) {
        
    let notificationTimeout;
    // const notification = document.getElementById('notification-container');
    const notification = document.querySelector('.notification-card');
    const notificationMessage = document.getElementById('notification');
    const typeElement = document.querySelector('.type');

    notification.classList.remove('success', 'error', 'info');

    if (type === 'Success') {
        notification.classList.add('success');
    } else if (type === 'Error') {
        notification.classList.add('error');
    } else if (type === 'Info') {
        notification.classList.add('info');
    }
    
    typeElement.textContent = type;
    notificationMessage.textContent = message;

    // Clear any existing timer if user clicks multiple times
    clearTimeout(notificationTimeout);
    
    // Add class to slide the notification into view
    notification.classList.add('show');
    
    // Auto-hide after 3 seconds
    notificationTimeout = setTimeout(() => {
        closeNotification();
    }, 3000);
    }

    function closeNotification() {
    const notification = document.getElementById('notification-container');
    notification?.classList.remove('show');
    }

    document.querySelector('.close-btn')?.addEventListener('click', closeNotification);
