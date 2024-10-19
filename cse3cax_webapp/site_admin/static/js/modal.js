(function() {
    /**
     * Wait for the DOM to be fully loaded before executing the script
     */
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM fully loaded and parsed.');

        /**
         * Function to initialize and show the correct modal
         */
        function initializeAndShowModal(modalId) {
            console.log('Attempting to initialize modal with ID:', modalId);
            const modalElement = document.getElementById(modalId);
            if (!modalElement) {
                console.log('Modal element not found for ID:', modalId);
                return;
            }
            
            // Initialize the Bootstrap modal
            const modal = new bootstrap.Modal(modalElement);
            console.log('Modal initialized:', modalId);

            // Show the modal
            modal.show();
            console.log('Modal shown:', modalId);
        }

        /**
         * Listen for htmx events to control modal behavior
         */
        htmx.on('htmx:afterSwap', (e) => {
            console.log('htmx:afterSwap event triggered for target ID:', e.detail.target.id);
            
            // Check which modal should be shown
            if (e.detail.target.id === "dialog") {
                console.log('Showing default modal.');
                initializeAndShowModal('modal'); // Default modal
            } else if (e.detail.target.id === "overloadedLecturers") {
                console.log('Showing overloaded lecturers modal.');
                initializeAndShowModal('overloadedLecturersModalContainer'); // Second modal
            } else {
                console.log('Target ID does not match: ', e.detail.target.id);
            }
        });

        htmx.on('htmx:beforeSwap', (e) => {
            console.log('htmx:beforeSwap event triggered for target ID:', e.detail.target.id);
            
            // Hide the relevant modal before swapping content
            if (e.detail.target.id === "dialog" && e.detail.xhr.status === 204) {
                console.log('Hiding default modal before swap.');
                const modalElement = document.getElementById('modal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                        console.log('Default modal hidden.');
                    }
                }
            } else if (e.detail.target.id === "overloadedLecturersModalContainer") {
                console.log('Hiding overloaded lecturers modal before swap.');
                const modalElement = document.getElementById('overloadedLecturersModalContainer');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                        console.log('Overloaded lecturers modal hidden.');
                    }
                }
            }
        });
    });
})();
