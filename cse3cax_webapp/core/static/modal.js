/**
 * Modal handling script
 *
 * Author: Jacob Paff
 * Revision: 1.0
 */

(function() {
    /**
     * Wait for the DOM to be fully loaded before executing the script
     */
    document.addEventListener('DOMContentLoaded', function() {
        /**
         * Get the modal element
         */
        const modalElement = document.getElementById('modal');
        if (!modalElement) return;

        /**
         * Initialise the Bootstrap modal
         */
        const modal = new bootstrap.Modal(modalElement);

        /**
         * Show the modal after the htmx swap event
         */
        htmx.on('htmx:afterSwap', (e) => {
            if (e.detail.target.id === "dialog" || e.detail.target.id === "overloadedLecturersModalContainer") {
                modal.show();
            }
        });

        /**
         * Hide the modal before the htmx swap event
         */
        htmx.on('htmx:beforeSwap', (e) => {
            if (e.detail.target.id === "dialog" && !e.detail.xhr.status === 204) {
                modal.hide();
            }
        });
    });
})();