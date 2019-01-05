function updateCell(name, value, color){
    $('#' + name).text(value);
    $('#arrow-' + name).css("color", color);
}

function update_data(){
    $.ajax({
        url         : "getCurrentData",
        type        : "GET",
        contentType : 'application/json',
        dataType    : 'json',
        success    : function (response) {
            updateCell('temperature', response.temperature / 10, function(){
              if (response.temperature < - 150){
                return "#0045CF";
              }
              else if (response.temperature < -50) {
                  return "#00B3CF";
              }
              else if (response.temperature < 50) {
                  return "#A2B556";
              }
              else if (response.temperature < 150) {
                  return "#E1DD00";
              }
              else if (response.temperature < 250) {
                  return "#FE9414";
              }
              else{
                return "#FE1414";
              }
            });
            updateCell('humidity', response.humidity / 10, function(){
              if (response.humidity < 300){
                return "#E1DD00";
              }else if (response.humidity < 550){
                return "#A2B556";
              }else if (response.humidity < 800){
                return "#00B3CF";
              }else{
                return "#0045CF";
              }
            });
            updateCell('pressure', response.pressure / 10, function(){
              if (response.pressure < 9950){
                return "#E1DD00";
              }else if(response.pressure <1010){
                return "#5DDA0B";
              }else{
                return "#FE9414";
              }
            });
            updateCell('dust_PM10', response.dust_PM10 + " (" + Math.round(response.dust_PM10 / 0.15) + " %)", function(){
              if(response.dust_PM10 < 15){
                return "#71CA2B";
              }else if (response.dust_PM10 < 30){
                return "#D3D125";
              }else if (response.dust_PM10 < 45){
                return "#F4F5F7";
              }else if(response.dust_PM10 < 60){
                return "#EF333B";
              }else{
                return "#B30C5A";
              }
            });
            updateCell('dust_PM25', response.dust_PM25 + " (" + Math.round(response.dust_PM25 / 0.25) + " %)", function(){
              if(response.dust_PM25 < 25){
                return "#71CA2B";
              }else if (response.dust_PM25 < 50){
                return "#D3D125";
              }else if (response.dust_PM25 < 75){
                return "#F4F5F7";
              }else if(response.dust_PM25 < 100){
                return "#EF333B";
              }else{
                return "#B30C5A";
              }
            });
            updateCell('dust_PM100', response.dust_PM100 + " (" + Math.round(response.dust_PM100 / 0.5) + " %)", function(){
              if(response.dust_PM100 < 50){
                return "#71CA2B";
              }else if (response.dust_PM100 < 100){
                return "#D3D125";
              }else if (response.dust_PM100 < 150){
                return "#F4F5F7";
              }else if(response.dust_PM100 < 200){
                return "#EF333B";
              }else{
                return "#B30C5A";
              }
            });
        }
    });
    setTimeout(update_data, 1000);
}
