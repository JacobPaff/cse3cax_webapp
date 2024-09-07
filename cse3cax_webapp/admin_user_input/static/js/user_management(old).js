// user_management.js

document.addEventListener('DOMContentLoaded', function() {
  // User list functionality
  function highlightUser(element) {
      clearActiveUser();
      element.classList.add('active');
  }

  function clearActiveUser() {
      document.querySelectorAll('#user-list .list-group-item').forEach(item => {
          item.classList.remove('active');
      });
  }
document.body.addEventListener('htmx:afterSwap', function(event) {
  if (event.detail.target.id === 'modalContainer') {
      var modal = new bootstrap.Modal(event.detail.target.querySelector('.modal'));
      modal.show();
  }
});



  // // Expertise field toggle functionality
  // const roleSelect = document.getElementById('id_role');
  // const expertiseField = document.querySelector('.expertise-field');

  // function toggleExpertiseField() {
  //     if (roleSelect && expertiseField) {
  //         const isLecturer = roleSelect.value === 'Lecturer';
  //         expertiseField.style.display = isLecturer ? 'block' : 'none';
  //     }
  // }

  // if (roleSelect) {
  //     roleSelect.addEventListener('change', toggleExpertiseField);
  //     // No need to call toggleExpertiseField() initially, as the form handles the initial state
  // }

  // User selection functionality
  // const userList = document.getElementById('user-list');

  // if (userList) {
  //     userList.addEventListener('click', function(event) {
  //         const clickedUser = event.target.closest('.list-group-item');
  //         if (clickedUser) {
  //             highlightUser(clickedUser);
  //             const isLecturer = clickedUser.dataset.role === 'Lecturer';
  //             if (expertiseField) {
  //                 expertiseField.style.display = isLecturer ? 'block' : 'none';
  //             }
  //         }
  //     });
  // }

  // Expose functions to global scope if needed
  window.highlightUser = highlightUser;
  window.clearActiveUser = clearActiveUser;
});