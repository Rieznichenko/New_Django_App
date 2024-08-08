document.addEventListener('DOMContentLoaded', function () {
    $('#id_select_database').on('change', function () {

        var url = `${window.location.origin}/get-read-choices/${encodeURIComponent($(this).val())}`;
     
        $.getJSON(url, function (j) {
            var options_read_model = '<option value="">---------</option>';
            var options_write_model = '<option value="">---------</option>';
            
            for (var i = 0; i < j.length; i++) {
                console.log("J", j[i])
                if(j[i].type == "read"){
                options_read_model +=
                    '<option value="' + j[i].id + '">' + j[i].database_name__db_name + '</option>';
                }
                else{
                options_write_model +=
                    '<option value="' + j[i].id + '">' + j[i].database_name__db_name + '</option>';
                }

            }
            
            $("#id_select_read_model").html(options_read_model);
            $("#id_select_write_model").html(options_write_model);
            $('#id_select_read_model').prop('disabled', false);
            $('#id_select_write_model').prop('disabled', false);
        }).fail(function() {
            console.error('Error with the AJAX request.');
        });
    });
});
