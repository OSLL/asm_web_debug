$(function() {
    changeURLFilter();
})

function changeURLFilter() {
    const inputs = $('.filter-control .form-control');

    //parse url
    let params = location.search.replace('?','').split('&')
                    .reduce(
                        function(p,e) {
                            let a = e.split('=');
                            p[decodeURIComponent(a[0])] = decodeURIComponent(a[1]);
                            return p;
                        },
                        {}  
                    );
    
                    

    for(let i = 0; i < inputs.length; ++i) {
        let par = $(inputs[i]).parents('th').data('field');
        if(par in params)
        {
            $(inputs[i]).val(params[par]).keyup()
            $(inputs[i]).append($('<option>').val(params[par]).text(params[par]).prop('selected', true))
            $(inputs[i]).change();
    }
}
    
    //change url
    function changeURLByParam(tag, par) {
        tag = encodeURIComponent(tag);
        par = encodeURIComponent(par);
        let url = location.href;
        if(location.search == '' && !(/\?$/.test(url))) url += '?';
        let regexp = new RegExp(`(&${tag}=)([^&]*)`);

        if(regexp.test(url)) {
            if(par === '')
                url = url.replace(regexp, '');
                if(/\?$/.test(url)) url = url.slice(0, url.length - 1);
            else
                url = url.replace(regexp, '$1' + par);
        } else {
            url += `&${tag}=${par}`
        }

        history.pushState(null, null, url); 
    }

    inputs.on('change', function() {
        const tag = $(this).parents('th').data('field');
        const par = $(this).val();
        changeURLByParam(tag, par);
    });

}