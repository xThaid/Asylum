function updateCell(name, value){
    $('#' + name).text(value);
}
function updateDustIndicator(name, value, norm){
  let color = "";
  let text = "";

  if (value < norm){
    text = "ŚWIETNA";
    color = "#70CA2C";
  }else if(value < 2 * norm){
    text = "DOBRA";
    color = "#D3D124";
  }else if(value < 3 * norm){
    text = "UMIARKOWANA";
    color = "#EFAE16";
  }else if(value < 4 * norm){
    text = "ZŁA";
    color = "#EF7728";
  }else{
    text = "FATALNA";
    color = "#B30C5A";
  }

  $('#indicator_' + name).css("background", color);
  $("#indicator_" + name).text(text);
}

function updateTemperatureIndicator(name, value){
  let color = "";
  let text = "";

  if (value < -15){
    text = "BARDZO ZIMNO";
    color = "#0066CC";
  }else if(value < -5){
    text = "ZIMNO";
    color = "#00CCFF";
  }else if(value < 5){
    text = "CHŁODNO";
    color = "#00FF99";
  }else if(value < 15){
    text = "UMIARKOWANIE";
    color = "#FFFF66";
  }else if(value < 25){
    text = "CIEPŁO";
    color = "#FFCC00";
  }else if(value < 35){
    text = "GORĄCO";
    color = "#FF6600";
  }
  else{
    text = "BARDZO GORĄCO";
    color = "#CC3300";
  }

  $('#indicator_' + name).css("background", color);
  $("#indicator_" + name).text(text);
}


function updateHumidityIndicator(name, value){
  let color = "";
  let text = "";

  if (value < 20){
    text = "BARDZO NISKA";
    color = "#FFCC00";
  }else if(value < 40){
    text = "NISKA";
    color = "#FFFF66";
  }else if(value < 60){
    text = "UMIARKOWANA";
    color = "#00FF99";
  }else if(value < 80){
    text = "WYSOKA";
    color = "#00CCFF";
  }else{
    text = "BARDZO WYSOKA";
    color = "#0066CC";
  }

  $('#indicator_' + name).css("background", color);
  $("#indicator_" + name).text(text);
}

function updatePressureIndicator(name, value){
  let color = "";
  let text = "";

  if (value < 990){
    text = "BARDZO NISKIE";
    color = "#0066CC";
  }else if(value < 1000){
    text = "NISKIE";
    color = "#00CCFF";
  }else if(value < 1020){
    text = "UMIARKOWANE";
    color = "#00FF99";
  }else if(value < 1030){
    text = "WYSOKIE";
    color = "#FFFF66";
  }else{
    text = "BARDZO WYSOKIE";
    color = "#FFCC00";
  }

  $('#indicator_' + name).css("background", color);
  $("#indicator_" + name).text(text);
}

function updateChangeArrow(name, change, step, min){
  let arrowUp = '<i class="mdi mdi-arrow-up-bold meteo-arrow"></i>';
  let arrowDown = '<i class="mdi mdi-arrow-down-bold meteo-arrow"></i>';
  let constant = '<i class="mdi mdi-bullseye meteo-arrow"></i>';

  let color = "";
  let arrows = "";

  if (Math.abs(change) <= min){
    arrows = constant;
    color = "orange";
  }else{
    if (change < 0){
      if (-change <= step + min){
        color = "red";
        arrows += arrowDown;
      }else if (-change <= 2 * step + min){
        color = "red";
        arrows += arrowDown;
        arrows += arrowDown;
      }else {
        color = "red";
        arrows += arrowDown;
        arrows += arrowDown;
        arrows += arrowDown;
      }
    }else{
      if (change <= step + min){
        color = "green";
        arrows += arrowUp;
      }else if (change <= 2 * step + min){
        color = "green";
        arrows += arrowUp;
        arrows += arrowUp;
      }else {
        color = "green";
        arrows += arrowUp;
        arrows += arrowUp;
        arrows += arrowUp;
      }
    }
  }

  $('#change_' + name).css("color", color);
  $("#change_" + name).append(arrows);
}

function update_data(){
    let mult = 1 / 100;
    $.ajax({
        url         : "/meteo/getCurrentData",
        type        : "GET",
        contentType : 'application/json',
        dataType    : 'json',
        success     : function (response) {
            updateCell('temperature', (response.temperature * mult).toFixed(1) + " °C");
            updateTemperatureIndicator('temperature', response.temperature * mult);
            updateChangeArrow('temperature', response.temperature_delta, 4, 1);
            updateCell('humidity', (response.humidity * mult).toFixed(1) + " %");
            updateHumidityIndicator('humidity', response.humidity * mult);
            updateChangeArrow('humidity', response.humidity_delta, 10, 2);
            updateCell('pressure', (response.pressure * mult).toFixed(1) + " hPa");
            updatePressureIndicator('pressure', response.pressure * mult);
            updateChangeArrow('pressure', response.pressure_delta, 4, 1);
            updateCell('dust_PM10', response.dust_PM10 + " µg/m³");
            updateDustIndicator('dust_PM10', response.dust_PM10, 15);
            $("#change_dust_PM10").text((response.dust_PM10 * 100 / 15).toFixed(0) + " %");
            updateCell('dust_PM25', response.dust_PM25 + " µg/m³");
            updateDustIndicator('dust_PM25', response.dust_PM25, 25);
            $("#change_dust_PM25").text((response.dust_PM25 * 100 / 25).toFixed(0) + " %");
            updateCell('dust_PM100', response.dust_PM100 + " µg/m³");
            updateDustIndicator('dust_PM100', response.dust_PM100, 50);
            $("#change_dust_PM100").text((response.dust_PM100 * 100 / 50).toFixed(0) + " %");
            updateDustValues();
        },
        error       : function() {
          setTimeout(update_data, 1000);
        }
    });
}

function updateDustValues(){
  $.ajax({
      url         : "getCurrentDustData",
      type        : "GET",
      contentType : 'application/json',
      dataType    : 'json',
      success     : function (response) {
          updateCell('dust_PM10', response.dust_PM10 + " µg/m³");
          updateDustIndicator('dust_PM10', response.dust_PM10, 15);
          $("#change_dust_PM10").text((response.dust_PM10 * 100 / 15).toFixed(0) + " %");
          updateCell('dust_PM25', response.dust_PM25 + " µg/m³");
          updateDustIndicator('dust_PM25', response.dust_PM25, 25);
          $("#change_dust_PM25").text((response.dust_PM25 * 100 / 25).toFixed(0) + " %");
          updateCell('dust_PM100', response.dust_PM100 + " µg/m³");
          updateDustIndicator('dust_PM100', response.dust_PM100, 50);
          $("#change_dust_PM100").text((response.dust_PM100 * 100 / 50).toFixed(0) + " %");
          setTimeout(updateDustValues, 1000);
      },
      error       : function() {
        setTimeout(updateDustValues, 1000);
      }
  });
}
