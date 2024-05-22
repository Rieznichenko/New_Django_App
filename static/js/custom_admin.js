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
        modal.style.zIndex = '1000';
        modal.style.left = '0';
        modal.style.top = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.overflow = 'auto';
        modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    
        const modalContent = document.createElement('div');
        modalContent.id = 'modalContent';
        modalContent.style.backgroundColor = '#fff';
        modalContent.style.margin = '10% auto';
        modalContent.style.padding = '20px';
        modalContent.style.borderRadius = '10px';
        modalContent.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        modalContent.style.width = '70%';
        modalContent.style.position = 'relative';
    
        const textSpan = document.createElement('span');
        textSpan.id = 'htmlContent';
        textSpan.innerText = 'Your text to copy'; // Add some sample text
        textSpan.style.display = 'block';
        textSpan.style.marginBottom = '20px';
        textSpan.style.color = '#333';
        textSpan.style.fontFamily = 'Arial, sans-serif';
        textSpan.style.fontSize = '16px';
    
        const modalButtons = document.createElement('div');
        modalButtons.id = 'modalButtons';
        modalButtons.style.position = 'absolute';
        modalButtons.style.top = '10px';
        modalButtons.style.right = '10px';
    
        const copyBtn = document.createElement('button');
        copyBtn.innerHTML = '📋'; // You can use an image like this: '<img src="path_to_icon.png" alt="Copy">'
        copyBtn.style.cursor = 'pointer';
        copyBtn.style.background = 'none';
        copyBtn.style.border = 'none';
        copyBtn.style.color = '#555';
        copyBtn.style.fontSize = '20px';
        copyBtn.style.marginRight = '10px';
        copyBtn.onclick = function() {
            copyTextToClipboard(textSpan.innerText);
            copyBtn.innerHTML = '✔'; // Change to a check mark or any other indicator
            setTimeout(() => {
                copyBtn.innerHTML = '📋'; // Revert back to original icon after 2 seconds
            }, 2000);
        };

        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '24px';
        closeBtn.style.color = '#555';
        closeBtn.onclick = closeModal;

        modalButtons.appendChild(copyBtn);
        modalButtons.appendChild(closeBtn);
        modalContent.appendChild(modalButtons);
        modalContent.appendChild(textSpan);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
    }

    function openModal(widgetId) {
        const modal = document.getElementById('customModal');
        const modalContent = document.getElementById('htmlContent');

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
    document.querySelectorAll('#viewScript').forEach(button => {
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
