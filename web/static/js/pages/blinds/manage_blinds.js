$(document).ready( function () {
    $('#zero_config').DataTable();
    $('#datetimepicker5').datetimepicker({
        format: 'DD-MM-YYYY HH:mm',
        minDate: moment(moment().format("DD-MM-YYYY"), "DD-MM-YYYY"),
                icons: {
                    time: "fas fa-clock",
                    date: "fa fa-calendar",
                    up: "fa fa-arrow-up",
                    down: "fa fa-arrow-down"
                }
            });
        $('#datetimepicker6').datetimepicker({
            defaultDate: moment('00:00', 'HH:mm'),
            format: 'HH:mm',
                icons: {
                    time: "fas fa-clock",
                    date: "fa fa-calendar",
                    up: "fa fa-arrow-up",
                    down: "fa fa-arrow-down"
                }
            });
} );

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
$('#change-sign').click(function (evt) {
    let target = $(evt.target);
    if (target.html() === "+") {
        target.html("-");
    } else {
        target.html("+");
    }
});

$(".choose-time").click(function(evt){
    let target = $(evt.target);
    if(target.data('timer')){
        clearInterval(target.data('timer'));
        target.html(target.data('datetime'));
        target.css({cursor: 'zoom-in'});
        target.removeData('timer');
    }else {
        target.data('datetime', target.html());
        let m = moment(target.data('datetime'), "DD-MM-YYYY HH:mm");
        m.locale('pl');
        target.html(m.fromNow());
        target.css({cursor: 'zoom-out'});
        target.data('timer', setInterval(function () {
            target.html(m.fromNow());
        }, 1000));
    }
});


$('#form-add-task').submit(function () {
    const form =   $('#form-add-task').serializeArray();
    const data = JSON.stringify(
        {
            'devices': form[0].value.replace('[', '').replace(']', '').split(',').map(Number),
            "timedate": moment(form[1].value, 'DD-MM-YYYY HH:mm').unix(),
            "action": parseInt(form[2].value, 10)
        });
    $.ajax({
        url         : "addTask",
        type        : "POST",
        contentType : 'application/json',
        dataType    : 'json',
        data        : data,
        success    : function (response) {
            location.reload();
        },
        error: function (response){
        let message;
        switch(response.responseJSON.code){
            case 1:
                message = "Niewłaściwe dane";
                break;
            case 2:
                message = "Błąd bazy danych";
                break;
            default:
                message = "Nieznany błąd";
                break;
        }
        toastr[response.responseJSON.status](message, "Nie dodano zadania")
        }
    });
     return false;
});

$('#form-add-schedule').submit(function () {
    const form =   $('#form-add-schedule').serializeArray();
    const data = JSON.stringify(
        {
            'devices': form[0].value.replace('[', '').replace(']', '').split(',').map(Number),
            "action": parseInt(form[1].value, 10),
            'hour_type': parseInt(form[2].value, 10),
            'time_offset':  moment.duration(form[3].value, 'HH:mm').asMinutes()
        });
    $.ajax({
        url         : "addSchedule",
        type        : "POST",
        contentType : 'application/json',
        dataType    : 'json',
        data        : data,
        success    : function (response) {
            location.reload();
        },
        error: function (response){
        let message;
        switch(response.responseJSON.code){
            case 1:
                message = "Niewłaściwe dane";
                break;
            case 2:
                message = "Błąd bazy danych";
                break;
            default:
                message = "Nieznany błąd";
                break;
        }
        toastr[response.responseJSON.status](message, "Nie dodano harmonogramu")
        }
    });
     return false;
});

function show_front_form(id){
    $('#' + id).css({display: 'flex'}).animate({
        opacity: 1
    }, 300);
}
function hide_front_form(){
    $('.front-form').animate({
        opacity: 0
    }, 300, function(){
        $('.front-form').css({display: 'none'})
    });
}
function delete_task(task_id) {
    const data = JSON.stringify(
        {
            'task_id': parseInt(task_id, 10)
        });
    $.ajax({
        url: "deleteTask",
        type: "POST",
        contentType: 'application/json',
        dataType: 'json',
        data: data,
        success: function (response) {
            location.reload();
        },
        error: function (response) {
            let message;
            switch (response.responseJSON.code) {
                case 1:
                    message = "Niewłaściwe dane";
                    break;
                case 2:
                    message = "Błąd bazy danych";
                    break;
                default:
                    message = "Nieznany błąd";
                    break;
            }
            toastr[response.responseJSON.status](message, "Nie usunięto zadania")
        }
    });
}

 function delete_schedule(schedule_id) {
     const data = JSON.stringify(
         {
             'schedule_id': parseInt(schedule_id, 10)
         });
     $.ajax({
         url: "deleteSchedule",
         type: "POST",
         contentType: 'application/json',
         dataType: 'json',
         data: data,
         success: function (response) {
             location.reload();
         },
         error: function (response) {
             let message;
             switch (response.responseJSON.code) {
                 case 1:
                     message = "Niewłaściwe dane";
                     break;
                 case 2:
                     message = "Błąd bazy danych";
                     break;
                 default:
                     message = "Nieznany błąd";
                     break;
             }
             toastr[response.responseJSON.status](message, "Nie usunięto harmonogramu")
         }
     });
 }
