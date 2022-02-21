function ajaxRequest(params) {
    let url = '/logs/get_filtered';
    console.log(params)
    $.get(url + '?' + $.param(params.data)).then(function (res) {
        params.success(res);
    });
}

function LogLink(value, row, index) {
    return `<a href='/logs/${value}' target='_blank'>${value}</a>`;
}

function detailFormatter(index, row) {
    let html = [];
    $.each(row, function (key, value) {
        if (key == "message") {
            value = value.replace(/[<|>]/g, '')
            .replace(/[False|True]/gi, function(i){
                return i.toLowerCase();
            }).replace(/None/g, 'null');
            value = value.replace(/\{.*\}/, function (x) {
                try {
                    x = JSON5.parse(x);
                } catch {
                    return x;
                }
                return JSON5.stringify(x, null, "\t");
            });
            html.push(`<p><b>${key}:</b></p><pre class="msg_pre language-json5"> <code>${value}</code></pre>`);
        }
    });
    return html.join('');
}

function MsgFormatter(value, row, index) {
    return value.replace(/[\u00A0-\u9999<>\&]/gim, function(i) {
        return '&#' + i.charCodeAt(0) + ';';
    });
}

function queryParams(params) {
    if(params.filter) {
        let filter = JSON.parse(params.filter);
        return {
            limit: params.limit,
            offset: params.offset,
            sort: params.sort,
            order: params.order,
            pathname: filter["pathname"],
            levelname: filter["levelname"],
            message: filter["message"],
            time: filter["time"]
        }; 
    }
    else return {
        limit: params.limit,
        offset: params.offset,
        sort: params.sort,
        order: params.order
    }
}