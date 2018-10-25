$(document).ready( function () {
    $('#zero_config').DataTable();
    $('#datetimepicker5').datetimepicker({
        format: 'DD-MM-YYYY HH:mm',
        locale: 'pl-pl',
        minDate: moment(moment().add(1, 'minutes').format("DD-MM-YYYY HH:mm"), "DD-MM-YYYY HH::mm"),
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
            locale: 'pl-pl',
                icons: {
                    time: "fas fa-clock",
                    date: "fa fa-calendar",
                    up: "fa fa-arrow-up",
                    down: "fa fa-arrow-down"
                }
            });

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
                'devices_ids': form[0].value.replace('[', '').replace(']', '').split(',').map(Number),
                "unix_time": moment(form[1].value, 'DD-MM-YYYY HH:mm').unix(),
                "action_id": parseInt(form[2].value, 10)
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
                toastr[response.responseJSON.status](response.responseJSON.message, "Nie dodano zadania");
            }
        });
         return false;
    });

    $('#form-add-schedule').submit(function () {
        const form =   $('#form-add-schedule').serializeArray();
        let sign = (form[2].value === '6') ? 1 : (($('#change-sign').html() === "+") ? 1 : -1);
        const data = JSON.stringify(
            {
                'devices_ids': form[0].value.replace('[', '').replace(']', '').split(',').map(Number),
                "action_id": parseInt(form[1].value, 10),
                'hour_type': parseInt(form[2].value, 10),
                'time_offset': sign * moment.duration(form[3].value, 'HH:mm').asMinutes()
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
                toastr[response.responseJSON.status](response.responseJSON.message, "Nie dodano harmonogramu");
            }
        });
         return false;
    });

    $(document).keydown(function(e) {
        if ( e.key === "Escape")
            hide_front_form();
    });

     $('#hour-type-combobox').on('change', function(e){
         if ($(this).val() === '6'){
            $('#change-sign').hide();
         }else{
             $('#change-sign').show();
         }
     });
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
            toastr[response.responseJSON.status](response.responseJSON.message, "Nie usunięto zadania");
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
             toastr[response.responseJSON.status](response.responseJSON.message, "Nie usunięto harmonogramu");
         }
     });
 }

