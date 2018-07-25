$(function(){

    if(window.location.pathname === '/'){
        window.location.pathname = '/home';
    }

    $('.navbar-link').each(function(){
        if(window.location.pathname.startsWith($( this ).attr('href'))){
            $( this ).addClass('navbar-link-active');
        }
    });
});