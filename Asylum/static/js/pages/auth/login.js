function completeRequestCallback(response) {
    $('form').each(function () { this.reset(); });
    toastr.options =
        {
            "closeButton": true,
            "debug": false,
            "newestOnTop": false,
            "progressBar": false,
            "positionClass": "toast-top-center",
            "preventDuplicates": false,
            "onclick": null,
            "showDuration": "300",
            "hideDuration": "1000",
            "timeOut": "10000",
            "extendedTimeOut": "2000",
            "showEasing": "swing",
            "hideEasing": "linear",
            "showMethod": "fadeIn",
            "hideMethod": "fadeOut"
        };
    let message;
    switch (response.responseJSON.code){
        case 0:
            window.location.replace(response.responseJSON['url']);
            break;
        case 1:
            message  = 'Błąd podczas komunikacji z bazą danych';
            break;
        case 2:
            message  = 'Nieprawidłowy login lub hasło';
            break;
        case 3:
            message  = 'Brakujące parametry';
            break;
        default:
            message  = 'Nieznany błąd';
            break;
    }
    toastr[response.responseJSON.status](message, "Logowanie");
}
$(document).ready(function(){
    $('form').submit(function () {
        const form =   $('form').serializeArray();
        const data = JSON.stringify(
            {
                "username": form[0].value,
                "password": form[1].value
            });
        $.ajax({
            url         : "login",
            type        : "POST",
            contentType : 'application/json',
            dataType    : 'json',
            data        : data,
            complete    : completeRequestCallback
        });
         return false;
    });
});