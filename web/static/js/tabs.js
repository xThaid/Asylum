function changeTab(index) {
    $(".tab-page").hide();
    $('#tab' + index).show();
    $('.tab-button').removeClass('tab-button-active');
    $('#tab-button' + index).addClass('tab-button-active');
}