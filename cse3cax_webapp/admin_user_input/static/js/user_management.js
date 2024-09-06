function highlightUser(element) {
    clearActiveUser();
    element.classList.add('active');
}

function clearActiveUser() {
    document.querySelectorAll('#user-list .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
}