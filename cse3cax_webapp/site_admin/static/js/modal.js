(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const modalElement = document.getElementById('modal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);

        htmx.on('htmx:afterSwap', (e) => {
            if (e.detail.target.id === "dialog") {
                modal.show();
            }
        });

        // Prevent modal from closing for certain status codes (201, 202)
        htmx.on('htmx:beforeSwap', (e) => {
            if (e.detail.target.id === "dialog") {
                // Only hide if the response status is 204
                if (e.detail.xhr.status === 204) {
                    modal.hide();  // Close modal only for 204 No Content
                } else if (e.detail.xhr.status === 201 || e.detail.xhr.status === 202) {
                    console.log('Preventing modal from closing for 201 or 202');
                    e.preventDefault();  // Prevent default behavior that hides the modal
                }
            }
        });
    });
})();