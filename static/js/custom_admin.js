// static/admin/js/custom_admin.js
// Function to copy text to clipboard
function copyTextToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            console.log('Text copied to clipboard');
        })
        .catch(err => {
            console.error('Unable to copy text to clipboard:', err);
        });
}
document.addEventListener('DOMContentLoaded', function() {
    function createModal() {
        const modal = document.createElement('div');
        modal.id = 'customModal';
        modal.style.display = 'none';
        modal.style.position = 'fixed';
        modal.style.zIndex = '1';
        modal.style.left = '0';
        modal.style.top = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.overflow = 'auto';
        modal.style.backgroundColor = 'rgba(0,0,0,0.4)';

        const modalContent = document.createElement('div');
        modalContent.id = 'modalContent';
        modalContent.style.backgroundColor = '#fefefe';
        modalContent.style.margin = '15% auto';
        modalContent.style.padding = '20px';
        modalContent.style.border = '1px solid #888';
        modalContent.style.width = '80%';

        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.float = 'right';
        closeBtn.style.cursor = 'pointer';
        closeBtn.onclick = closeModal;

        modalContent.appendChild(closeBtn);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
    }

    function openModal(widgetId) {
        const modal = document.getElementById('customModal');
        const modalContent = document.getElementById('modalContent');

        if (!modal || !modalContent) {
            console.error('Modal or modal content not found');
            return;
        }

        // Clear previous content
        modalContent.innerText = `
        <div id="chat-container"></div>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script src="https://ia.humanytek.com/static/js/chatbot-ui.js"></script>
        <link rel="stylesheet" href="https://ia.humanytek.com/static/css/chatbot-ui.css">
        <script>
            createChatBot(id="${widgetId}");
        </script>
    `;

        // Show the modal
        modal.style.display = 'block';

        // Collapse the sidebar
        const sidebar = document.getElementById('nav-sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
        }

        // Change main div class
        const mainDiv = document.getElementById('main');
        if (mainDiv) {
            mainDiv.className = 'main';
        }
    }

    function closeModal() {
        const modal = document.getElementById('customModal');
        if (modal) {
            modal.style.display = 'none';
        }

        // Expand the sidebar
        const sidebar = document.getElementById('nav-sidebar');
        if (sidebar) {
            sidebar.style.display = 'block';
        }

        // Revert main div class
        const mainDiv = document.getElementById('main');
        if (mainDiv) {
            mainDiv.className = 'main shifted';
        }
    }

    // Close modal when clicking outside of it
    window.onclick = function(event) {
        const modal = document.getElementById('customModal');
        if (event.target === modal) {
            closeModal();
        }
    };

    // Attach click events to buttons after DOM is loaded
    document.querySelectorAll('.button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
        });
    });

    // Initialize the modal on page load
    createModal();

    // Expose the openModal and closeModal functions globally
    window.openModal = openModal;
    window.closeModal = closeModal;
});
