function reload_with_parameters(element, page=-1, amount=-1, task_id=-1,
                                from_date="",to_date="",date_sort=0,passed=0){
    var url = window.location.href.split('?')[0];
    url+="?"
    if(page != -1){
        url+='&page='+page.toString()
    }
    if(amount != -1){
        url+='&amount='+amount.toString()
    }
    if(task_id != -1){
        url+='&task_id='+task_id.toString()
    }
    if(from_date != ""){
        url+='&from_date='+from_date
    }
    if(to_date != ""){
        url+='&to_date='+to_date
    }
    if(date_sort != 0){
        url+='&date_sort='+date_sort.toString()
    }
    if(passed != 0){
        url+='&passed='+passed.toString()
    }
    element.href = url;
    console.log(url)
}

function discard(){
    window.location = window.location.href.split('?')[0];
}

function apply(){
    var url = window.location.href.split('?')[0];
    url+="?"
    if($("#amount_apply").val()!=""){
        url+="&amount="+$("#amount_apply").val()
    }
    if($("#task_id_apply").val()!=""){
        url+="&task_id="+$("#task_id_apply").val()
    }
    if($("#from_apply").val()!=""){
        url+="&from_date="+$("#from_apply").val()
    }
    if($("#to_apply").val()!=""){
        url+="&to_date="+$("#to_apply").val()
    }
    if($("#date_newest").is(':checked')){
        url+="&date_sort=1"
    }
    if($("#date_oldest").is(':checked')){
        url+="&date_sort=-1"
    }
    if($("#passed").is(':checked')){
        url+="&passed=1"
    }
    if($("#failed").is(':checked')){
        url+="&passed=-1"
    }
    window.location = url;
}