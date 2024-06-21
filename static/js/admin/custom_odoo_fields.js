document.addEventListener('DOMContentLoaded', function() {
    const databaseNameField = document.querySelector('#id_database_name');
    const databaseTableField = document.querySelector('#id_database_table');
    const form = document.querySelector('#odoofields_form');  // Adjust form ID based on your actual form ID
    const fieldNameField = document.querySelector("#id_odootablefield_set-0-field_name")

    function updateTableChoices(databaseId) {
        fetch(`/get_table_choices/${databaseId}/`)
            .then(response => response.json())
            .then(data => {
                databaseTableField.innerHTML = '';
                data.choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.value = choice;
                    option.textContent = choice;
                    databaseTableField.appendChild(option);
                });
                databaseTableField.disabled = false;
            });
    }

    if (databaseNameField && databaseTableField && form) {
        console.log(form)
        databaseNameField.addEventListener('change', function() {
            const databaseId = this.value;
            if (databaseId) {
                updateTableChoices(databaseId);
            } else {
                databaseTableField.innerHTML = '';
                databaseTableField.disabled = true;
            }
        });

        form.addEventListener('submit', function() {
            databaseTableField.disabled = false;  // Enable field before form submission
        });
    }




    // if database_table stuff is changes
    function updateFieldChoices(tableId, database_id) {
        fetch(`/get_field_choices/${tableId}/${database_id}`)  // Replace with your actual endpoint for fetching field choices
            .then(response => response.json())
            .then(data => {
                fieldNameField.innerHTML = '';
                data.choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.value = choice;
                    option.textContent = choice;
                    fieldNameField.appendChild(option);
                });
                fieldNameField.disabled = false;
            });
    }

    if (databaseNameField && databaseTableField && form) {
        databaseTableField.addEventListener('change', function() {
            const tableId = this.value;
            if (tableId) {
                updateFieldChoices(tableId, databaseNameField.value);
            } else {
                fieldNameField.innerHTML = '';
                fieldNameField.disabled = true;
            }
        });

        form.addEventListener('submit', function() {
            fieldNameField.disabled = false;  // Enable field before form submission
        });
    }

});
