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

    $("#blinds_action_open" ).click(function() {
        execute_instant_action(1);
    });
    $("#blinds_action_close" ).click(function() {
        execute_instant_action(2);
    });
    $("#blinds_action_stop" ).click(function() {
        execute_instant_action(3);
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

     updateActionCountdowns();
     setInterval(updateActionCountdowns, 1000);
});

function formatRemainingTime(time) {
    if(time < 0) {
        time = 0;
    }
    let days = Math.floor(time / (60 * 60 * 24));
    let hours = Math.floor(time / (60 * 60));
    let minutes = Math.floor(time / 60);
    let seconds = Math.floor(time);

    let res = "";
    if(days > 0) res += days + "d ";
    if(hours > 0) res += (hours % 24) + "h ";
    if(minutes > 0) res += (minutes % 60) + "m ";
    res += (seconds % 60) + "s";

    return res;
}

function updateActionCountdowns() {
    $(".action-entry").each(function(i) {
        let actionTime = moment($(this).find(".action-time").text(), 'DD-MM-YYYY HH:mm').unix();
        let currTime = moment().unix();
        let diff = actionTime - currTime;
        $(this).find(".countdown").text(formatRemainingTime(diff));
    }); 
 }

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

 function execute_instant_action(action_id) {
     const data = JSON.stringify(
         {
             'device_ids': $("#device_ids").val().replace('[', '').replace(']', '').split(',').map(Number),
             "action_id": action_id
         });
     $.ajax({
         url: "instantAction",
         type: "POST",
         contentType: 'application/json',
         dataType: 'json',
         data: data,
         success: function (response) {
         },
         error: function (response) {
             toastr[response.responseJSON.status](response.responseJSON.message, "Nie wykonano zadania");
         }
     });
 }
