function createDatepicker(minDate) {

    $('#datetimepicker-year').datetimepicker({
        maxDate: moment().format("YYYY"),
        minDate: moment(minDate, "YYYY"),
        format: 'YYYY',
        locale: 'pl-pl'
    });
    $('#datetimepicker-month').datetimepicker({
        maxDate: moment().format("YYYY-MM"),
        minDate: moment(minDate, "YYYY-MM"),
        format: 'YYYY-MM',
        locale: 'pl-pl'
    });
    $('#datetimepicker-day').datetimepicker({
        maxDate: moment().format("YYYY-MM-DD"),
        minDate: moment(minDate, "YYYY-MM-DD"),
        format: 'YYYY-MM-DD',
        locale: 'pl-pl'
    });
}
function pickerClick(type){
    if(type==='year'){
        let picker = $('#datetimepicker-year');
        if(picker.data('ready') === true)
            picker.data('ready', false);
        else
            picker.data('ready', true);
        picker.datetimepicker('format', 'YYYY');
        picker.datetimepicker('viewMode', 'years');

        picker = $('#datetimepicker-month');
        picker.data('ready', false);
        picker.datetimepicker('hide');

        picker = $('#datetimepicker-day');
        picker.data('ready', false);
        picker.datetimepicker('hide');
    }else if(type==='month'){
       let picker = $('#datetimepicker-month');
        if(picker.data('ready') === true)
            picker.data('ready', false);
        else
            picker.data('ready', true);
        picker.datetimepicker('format', 'YYYY-MM');
        picker.datetimepicker('viewMode', 'months');

        picker = $('#datetimepicker-year');
        picker.data('ready', false);
        picker.datetimepicker('hide');

        picker = $('#datetimepicker-day');
        picker.data('ready', false);
        picker.datetimepicker('hide');
    }else if(type==='day'){
       let picker = $('#datetimepicker-day');
        if(picker.data('ready') === true)
            picker.data('ready', false);
        else
            picker.data('ready', true);
        picker.datetimepicker('format', 'YYYY-MM-DD');
        picker.datetimepicker('viewMode', 'days');

        picker = $('#datetimepicker-month');
        picker.data('ready', false);
        picker.datetimepicker('hide');

        picker = $('#datetimepicker-year');
        picker.data('ready', false);
        picker.datetimepicker('hide');
    }
}
function enablePickerNavigation() {
    $('#datetimepicker-year').on('datetimepicker.hide',function(){
        if($('#datetimepicker-year').data('ready') === true)
            window.location.href = 'year/' + $('#energy-history-input-year').val();
        }
    );
    $('#datetimepicker-month').on('datetimepicker.hide',function(){
        if($('#datetimepicker-month').data('ready') === true)
            window.location.href = 'month/' + $('#energy-history-input-month').val();
        }
    );
    $('#datetimepicker-day').on('datetimepicker.hide',function(){
        if($('#datetimepicker-day').data('ready') === true)
            window.location.href = 'day/' + $('#energy-history-input-day').val();
        }
    );
}
