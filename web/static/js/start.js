$(function(){
    if(window.location.pathname === '/'){
        window.location.pathname = '/home';
    }

    $('.navbar-link').each(function(){
        if(window.location.pathname.startsWith($( this ).attr('href'))){
            $( this ).addClass('navbar-link-active');
        }
    });

    $('.user-icon').click(function(){
        $('.user-menu').toggle();
    });
    $('body').click(function(evt){
        if(evt.target.id === "user-icon")
            return;
        $('.user-menu').hide();
    });
});