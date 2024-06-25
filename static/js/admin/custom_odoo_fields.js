document.addEventListener('DOMContentLoaded', function() {
    const databaseNameField = document.querySelector('#id_database_name');
    const databaseTableField = document.querySelector('#id_database_table');
    const form = document.querySelector('#odoofields_form');  // Adjust form ID based on your actual form ID
    const fieldNameField = document.querySelector("#id_odootablefield_set-0-field_name")
    const relation_read_field = document.querySelector("#id_odd_relation-0-oddo_read_field")
    const relation_write_field = document.querySelector("#id_odd_relation-0-oddo_write_field")

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
                relation_read_field.innerHTML = '';
                relation_write_field.innerHTML = ''

                data.choices.forEach(choice => {
                    const option1 = document.createElement('option');
                    option1.value = choice;
                    option1.textContent = choice;
                    fieldNameField.appendChild(option1);
    
                    const option2 = document.createElement('option');
                    option2.value = choice;
                    option2.textContent = choice;
                    relation_read_field.appendChild(option2);
    
                    const option3 = document.createElement('option');
                    option3.value = choice;
                    option3.textContent = choice;
                    relation_write_field.appendChild(option3);
                    });
                
            });
            fieldNameField.disabled = false;
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

document.addEventListener('DOMNodeInserted', handleDynamicElement);

});


function handleDynamicElement(event) {
    try{
    const targetClass = 'form-row dynamic-odootablefield_set';
    console.log("tagret class", event.target.classList)

    if (event.target.classList.contains("form-row") && event.target.classList.contains("dynamic-odootablefield_set")) {
        console.log("if clause")
        const originalRow = document.querySelector('#odootablefield_set-0');
        
        const newRow = event.target;
        
        const originalSelect = originalRow.querySelector('select');
        const newSelect = newRow.querySelector('select');
        
        newSelect.innerHTML = originalSelect.innerHTML;

    }
    else if(event.target.classList.contains("form-row") && event.target.classList.contains("dynamic-odd_relation")){
        const originalRow = document.querySelector('#odd_relation-0');
        
        const newRow = event.target;
        console.log(newRow)
        
        const originalSelect1 = originalRow.querySelector('select[name$="oddo_write_field"]');
        const originalSelect2 = originalRow.querySelector('select[name$="oddo_read_field"]');
        
        // Get the two select elements in the new row
        const newSelect1 = newRow.querySelector('select[name$="oddo_write_field"]');
        const newSelect2 = newRow.querySelector('select[name$="oddo_read_field"]');

        
        newSelect1.innerHTML = originalSelect1.innerHTML;
        newSelect2.innerHTML = originalSelect2.innerHTML;


    }


}catch{}
}
