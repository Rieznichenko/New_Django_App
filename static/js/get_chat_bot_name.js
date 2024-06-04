document.addEventListener('DOMContentLoaded', function () {

var botNameInput = document.getElementById('id_bot_name');
    var botTypeSelect = document.getElementById('id_bot_type');  // Assuming you have this


    botTypeSelect.addEventListener('change', function () {
        var selectedType = this.value;
        if (selectedType) {
            populateBotNames(selectedType);
        } else {
            botNameSelect.style.display = 'none';  // Hide if no type is selected
        }
    });


// Create a new select element
var botNameSelect = document.createElement('select');
botNameSelect.id = 'bot_name_select';
botNameSelect.style.display = 'none';  // Hide it initially

// Function to fetch and populate bot names
function populateBotNames(botType) {
    $("#id_bot_name").empty();
    var url = `${window.location.origin}/get_bot_names?bot_type=${encodeURIComponent(botType)}`;
    var options = '<option value="">---------</option>';
    var botNameSelect = document.getElementById('id_bot_name'); // Assuming 'id_discord_llm_agent' is the ID of your select element

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            botNameSelect.innerHTML = '<option value="">Select a bot</option>';
            data.bots.forEach(bot => {
                options += '<option value="' + bot.id + '">' + bot.name + '</option>';
            });
            botNameSelect.innerHTML += options;
            botNameSelect.disabled = false; // Enabling the select element
            botNameSelect.style.display = 'inline-block';  // Show the dropdown
        })
        .catch(error => {
            console.error('Error fetching bot names:', error);
            botNameSelect.style.display = 'none';  // Hide the dropdown on error
            alert('Failed to load bot names. Please try again.');
        });
}
console.log(botTypeSelect);
// Event listener for bot type change

// Event listener for bot name selection
botNameSelect.addEventListener('change', function () {
    var selectedOption = this.options[this.selectedIndex];
    botNameInput.value = selectedOption.value ? selectedOption.textContent : '';
});

// Insert the dropdown after the text field
botNameInput.insertAdjacentElement('afterend', botNameSelect);

// Handle form submission (as before)
document.getElementById('emailschedule_form').addEventListener('submit', function (event) {
    event.preventDefault();
    if (botNameSelect.value !== '' && botNameSelect.value !== botNameInput.value) {
        botNameInput.value = botNameSelect.options[botNameSelect.selectedIndex].textContent;
    }
    this.submit();
});

});
