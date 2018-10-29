function changeTab(index, url, addHistory = true) {
    let page_breadcrumb = $('#page-breadcrumb');
    if(page_breadcrumb.data('currentTabId') !== index) {
        page_breadcrumb.data('currentTabId', index);
        $(".tab-page").hide();
        $('#tab' + index).show();
        $('.tab-button').removeClass('tab-button-active');
        $('#tab-button' + index).addClass('tab-button-active');
        if(addHistory)
            history.pushState(null, '', url);
    }
}
function backToTab(tabList) {
    $(window).on('popstate', function () {
        let adres = location.href.split('/');
        let tab_url = adres[adres.length - 1];
        for(let i = 0; i < tabList.length; i++){
            if(tabList[i]['url'] === tab_url){
                changeTab(i + 1, '', false);
                break;
            }
        }
    });
}
