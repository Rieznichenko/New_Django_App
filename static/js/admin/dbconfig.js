// static/js/admin/dbconfig.js
document.addEventListener('DOMContentLoaded', function() {
    var authModeField = document.getElementById('id_auth_mode');
    toggleFields(authModeField);

    authModeField.addEventListener('change', function() {
        toggleFields(this);
    });

    function toggleFields(authModeField) {
        var usernameField = document.getElementById('id_username');
        var passwordField = document.getElementById('id_password');
        var apiKeyField = document.getElementById('id_api_key');

        if (authModeField.value === 'credentials') {
            usernameField.style.display = 'block';
            passwordField.style.display = 'block';
            apiKeyField.style.display = 'none';
        } else if (authModeField.value === 'api_key') {
            usernameField.style.display = 'block';
            passwordField.style.display = 'none';
            apiKeyField.style.display = 'block';
        }
    }
});
