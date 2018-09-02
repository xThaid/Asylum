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
    toastr[response.responseJSON.status](mresponse.responseJSON.message, "Logowanie");
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