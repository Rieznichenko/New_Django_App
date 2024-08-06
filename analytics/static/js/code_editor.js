// static/js/code_editor.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CodeMirror editor
    var editor = CodeMirror.fromTextArea(document.getElementById('id_embedded_code'), {
        lineNumbers: true,
        mode: 'python',
        theme: 'default',
        matchBrackets: true,
        autoCloseBrackets: true,
        indentUnit: 4,
        tabSize: 4,
    });

    // Create and insert the Run button
    var runButton = document.createElement('button');
    runButton.type = 'button';
    runButton.textContent = 'Test';
    runButton.onclick = function() {
        var code = editor.getValue();
        $.ajax({
            url: testCodeURL,
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            data: { code: code },
            success: function(response) {
                alert('Output: ' + response.output);
            },
            error: function(xhr, status, error) {
                alert('Error: ' + xhr.responseText);
            }
        });
    };

    // Insert the Run button after the CodeMirror editor
    var editorWrapper = document.querySelector('.CodeMirror');
    if (editorWrapper) {
        editorWrapper.parentNode.insertBefore(runButton, editorWrapper.nextSibling);
    }
});

function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
            break;
        }
    }
    return cookieValue;
}
