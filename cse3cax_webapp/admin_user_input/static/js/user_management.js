function highlightUser(element) {
    clearActiveUser();
    element.classList.add('active');
}

function clearActiveUser() {
    document.querySelectorAll('#user-list .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
}

{/* <script>
  document.body.addEventListener('htmx:afterSwap', function(event) {
    // Clear messages after 5 seconds
    setTimeout(function() {
      var messages = document.querySelectorAll('.alert');
      messages.forEach(function(message) {
        message.style.display = 'none';
      });
    }, 5000);
  });
</script> */}