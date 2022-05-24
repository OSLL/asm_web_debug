function reload_with_parameters(element, page=-1, task_id=-1){
    var url = window.location.href.split('?')[0];
    let was = false
    if(page != -1){
        url+='?page='+page.toString()
        was = true
    }
    if(task_id != -1){
        if(was) {
            url+='&task_id='+task_id.toString()
        }
        else {
            url += '?task_id=' + page.toString()
        }
        was = true
    }
    element.href = url;
}