$(()=>{
    $(".mybutton button").on('click', (e)=>{
        $.get('/admin_view', {updated: 'true'})
        .done(function(data){
            $('#top-information').text(data);
        });
    });
})