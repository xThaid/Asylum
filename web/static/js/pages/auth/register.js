function completeRequestCallback(response) {
    $('form').each(function () { this.reset(); });
    toastr.options =
        {
            "closeButton": true,
            "debug": false,
            "newestOnTop": false,
            "progressBar": false,
            "positionClass": "toast-top-right",
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
            message  = 'Pomyślnie stworzono konto';
            break;
        case 1:
            message  = 'Błąd podczas komunikacji z bazą danych';
            break;
        case 2:
            message  = 'Podany login jest już zajęty';
            break;
        case 3:
            message  = 'Brakujące parametry';
            break;
        case 4:
            message  = 'Nieprawidłowy login';
            break;
        case 5:
            message  = 'Nieprawidłowa nazwa użytkownika';
            break;
        case 6:
            message  = 'Nieprawidłowe hasło';
            break;
        case 7:
            message  = 'Podane hasła sa różne';
            break;
        case 8:
            message  = 'Nieprawidłowa rola';
            break;
        case 9:
            message  = 'Nie masz do tego uprawnień';
            break;
        default:
            message  = 'Nieznany błąd';
            break;
    }
    toastr[response.responseJSON.status](message, "Rejestracja")
}

$(document).ready(function(){
    $('form').submit(function () {
        const form =   $('form').serializeArray();
        const data = JSON.stringify(
            {
                "username": form[0].value,
                "name": form[1].value,
                'password': form[2].value,
                'repassword': form[3].value,
                'role': form[4].value
            });
        $.ajax({
            url         : "register",
            type        : "POST",
            contentType : 'application/json',
            dataType    : 'json',
            data        : data,
            complete    : completeRequestCallback
        });
         return false;
    });
});
