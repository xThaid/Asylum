function updateCell(name, value){
    let maxPower = 4000;
    let peityValue = value;
    if(name === 'summary_power_store') {
        let storePeity = $('#summary_power_store_peity');
        if (value < 0 ) {
            storePeity.peity('donut', {
                fill: ["#eeeeee", "#E1A500"],
                radius: 40,
                innerRadius: 33
            });
            peityValue = maxPower + value;
        }else{
            storePeity.peity('donut', {
                fill: ["#E1A500", "#eeeeee"],
                radius: 40,
                innerRadius: 33
            });
        }
    }
    $('#' + name + '_peity').text(peityValue + "/" + maxPower).change();
    $('#' + name).text(value);
}

function update_data(){
    $.ajax({
        url         : "getCurrentPowerData",
        type        : "GET",
        contentType : 'application/json',
        dataType    : 'json',
        success    : function (response) {
            updateCell('production_current', response.production);

            updateCell('consumption_current', response.consumption);

            updateCell('summary_power_use', response.use);
            updateCell('summary_power_import', response.import);
            updateCell('summary_power_export', response.export);
            updateCell('summary_power_store', response.store);
        }
    });
    setTimeout(update_data, 1000);
}

function createPeity(){
    $('.peity-donut-green').peity('donut',{
    fill: ["#28B779", "#eeeeee"],
    radius: 40,
    innerRadius: 33
    });
    $('.peity-donut-red').peity('donut',{
        fill: ["#DA542E", "#eeeeee"],
        radius: 40,
        innerRadius: 33
    });
    $('.peity-donut-orange').peity('donut',{
        fill: ["#E1A500", "#eeeeee"],
        radius: 40,
        innerRadius: 33
    });
}
