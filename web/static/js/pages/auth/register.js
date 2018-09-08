function completeRequestCallback(response) {
    $('form').each(function () { this.reset(); });
    toastr[response.responseJSON.status](response.responseJSON.message, "Rejestracja");
}
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
$(document).ready(function(){
    $('form').submit(function () {
        const form =   $('form').serializeArray();

        if(form[2].value !== form[3].value) {
            toastr['warning']('Podane hasła nie są identyczne', "Rejestracja");
            return false;
        }
        const data = JSON.stringify(
            {
                "login": form[0].value,
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
