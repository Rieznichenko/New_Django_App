document.addEventListener('DOMContentLoaded', function() {
    const databaseNameField = document.querySelector('#id_database_name');
    const databaseTableField = document.querySelector('#id_database_table');
    const form = document.querySelector('#odoofields_form');  // Adjust form ID based on your actual form ID
    const fieldNameField = document.querySelector("#id_odootablefield_set-0-field_name")
    // const relation_read_field = document.querySelector("#id_odd_relation-0-oddo_read_field")
    // const relation_write_field = document.querySelector("#id_odd_relation-0-oddo_write_field")

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
                // relation_read_field.innerHTML = '';
                // relation_write_field.innerHTML = ''

                data.choices.forEach(choice => {
                    const option1 = document.createElement('option');
                    option1.value = choice;
                    option1.textContent = choice;
                    fieldNameField.appendChild(option1);
    
                    // const option2 = document.createElement('option');
                    // option2.value = choice;
                    // option2.textContent = choice;
                    // relation_read_field.appendChild(option2);
    
                    // const option3 = document.createElement('option');
                    // option3.value = choice;
                    // option3.textContent = choice;
                    // relation_write_field.appendChild(option3);
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


// custom relation stuff here


const readModelSelect = document.getElementById('id_select_read_model');
const writeModelSelect = document.getElementById('id_select_write_model');

let readModelChanged = false;
let writeModelChanged = false;



function checkBothChanged() {
    if (readModelChanged && writeModelChanged) {
        select_db = document.querySelector('#id_select_database').value;
        select_read_model = document.querySelector('#id_select_read_model').value;
        select_write_model = document.querySelector('#id_select_write_model').value;
        const relation_read_field = document.querySelector("#id_odd_relation-0-oddo_read_field")
        const relation_write_field = document.querySelector("#id_odd_relation-0-oddo_write_field")

        fetch(`/get_field_choices-relation/${select_db}/${select_read_model}/${select_write_model}`)  // Replace with your actual endpoint for fetching field choices
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
                
                relation_read_field.innerHTML = '';
                relation_write_field.innerHTML = ''

                
                data.choices_read.forEach(choice => {
                    const option2 = document.createElement('option');
                    option2.value = choice;
                    option2.textContent = choice;
                    relation_read_field.appendChild(option2);
                });

                data.choices_write.forEach(choice => {
    
                    const option3 = document.createElement('option');
                    option3.value = choice;
                    option3.textContent = choice;
                    relation_write_field.appendChild(option3);


                });
                
            });


    }
  }
  readModelSelect.addEventListener('change', function() {
    readModelChanged = readModelSelect.value !== "";
    checkBothChanged();
  });

  writeModelSelect.addEventListener('change', function() {
    writeModelChanged = writeModelSelect.value !== "";
    checkBothChanged();
  });
});


function handleDynamicElement(event) {
    try{
    const targetClass = 'form-row dynamic-odootablefield_set';

    if (event.target.classList.contains("form-row") && event.target.classList.contains("dynamic-odootablefield_set")) {
        const originalRow = document.querySelector('#odootablefield_set-0');
        
        const newRow = event.target;
        
        const originalSelect = originalRow.querySelector('select');
        const newSelect = newRow.querySelector('select');
        
        newSelect.innerHTML = originalSelect.innerHTML;

    }
    else if(event.target.classList.contains("form-row") && event.target.classList.contains("dynamic-odd_relation")){
        console.log("Event raise", event)
        const originalRow = document.querySelector('#odd_relation-0');
        
        const newRow = event.target;        
        const originalSelect1 = originalRow.querySelector('select[name$="oddo_write_field"]');
        const originalSelect2 = originalRow.querySelector('select[name$="oddo_read_field"]');
        
        // Get the two select elements in the new row
        const newSelect1 = newRow.querySelector('select[name$="oddo_write_field"]');
        const newSelect2 = newRow.querySelector('select[name$="oddo_read_field"]');

        
        newSelect1.innerHTML = originalSelect1.innerHTML;
        newSelect2.innerHTML = originalSelect2.innerHTML;


    }
    else {
        console.log("Target does not match the condition");
    }

    if (databaseNameField && databaseTableField && form) {
        console.log("DOne")

    }

}catch{}





}
