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
    function getUserTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('user them --> dark')
            return 'dark';
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            console.log('user theme --> light')
            return 'light';
        } else {
            return 'no-preference';
        }
    }

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

        const userTheme = getUserTheme()
        if (userTheme == 'dark'){
            reqBackgroundColor = '#000'
        } else{
            reqBackgroundColor = '#f5f5f5'
        }
        
        const modalContent = document.createElement('div');
        modalContent.id = 'modalContent';
        modalContent.style.backgroundColor = "#fff";
        modalContent.style.margin = '15% auto';
        modalContent.style.padding = '20px';
        modalContent.style.borderRadius = '10px';
        modalContent.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
        modalContent.style.width = '60%';
        modalContent.style.position = 'relative';
        
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
        copyBtn.style.fontSize = '24px';
        copyBtn.style.marginRight = '15px';
        copyBtn.onclick = function() {
            copyTextToClipboard(htmlContent.innerText);
            copyBtn.innerHTML = '✔'; // Change to a check mark or any other indicator
            setTimeout(() => {
                copyBtn.innerHTML = '📋'; // Revert back to original icon after 2 seconds
            }, 2000);
        };
        
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '28px';
        closeBtn.style.color = '#555';
        closeBtn.onclick = closeModal;
        
        modalButtons.appendChild(copyBtn);
        modalButtons.appendChild(closeBtn);
        
        const htmlContent = document.createElement('div');
        htmlContent.id = 'htmlContent';
        htmlContent.style.fontFamily = 'Arial, sans-serif';
        htmlContent.style.fontSize = '25px';
        htmlContent.style.color = '#333';
        htmlContent.style.lineHeight = '1.5';
        htmlContent.style.backgroundColor = reqBackgroundColor;
        htmlContent.style.padding = '5px';
        htmlContent.style.borderRadius = '10px';
        htmlContent.style.margin = '40px 10px 0px 10px';

        const pre = document.createElement('pre');
        pre.id = 'preContent';
        pre.style.whiteSpace = 'pre-wrap';

        htmlContent.appendChild(pre)
        modalContent.appendChild(modalButtons);
        modalContent.appendChild(htmlContent);
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
        
        const htmlContent = document.getElementById('htmlContent');
        const pre = document.getElementById('preContent');
        // pre.style.wordWrap = 'break-word';
        pre.innerText = `
            <div id="chat-container"></div>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
            <script src="https://ia.humanytek.com/static/js/chatbot-ui.js"></script>
            <link rel="stylesheet" href="https://ia.humanytek.com/static/css/chatbot-ui.css">
            <script>
                createChatBot(id="9c291c7d-0424-41de-8737-f04e2c5dc0f6");
            </script>
        `;

        // Show the modal
        modal.style.display = 'block';

        // Collapse the sidebar
        const sidebar = document.getElementById('nav-sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
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
