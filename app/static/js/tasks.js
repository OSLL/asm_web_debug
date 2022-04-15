let am_reg=0;
let am_st=0;
let stack=[];
let registers=[];
let type=0;
let id;

function update(){
    if(type===0){
        $("#form_edit").attr("action", "/tasks/edit/?id="+id+"&registers="+registers+"&stack="+stack)
    }else{
        $("#form_edit").attr("action", "/tasks/add/?registers="+registers+"&stack="+stack)
    }
}

$( document ).ready(function() {
        console.log( "ready!" );
    });
function hide(){
    $.ajax({
        success(){
            $("#view_info").hide()
        }
    })
}
function hide_edit(){
    $.ajax({
        success(){
            $("#edit_info").hide()
        }
    })
}
function show(line){
    $.ajax({
        success(){
            console.log(line);
            $("#task_id").text("#"+line[0])
            $("#task_name").text(line[1])
            $("#task_difficulty").text("Difficulty: "+line[2])
            $("#task_success").text("Success amount: "+line[3])
            $("#task_description").text(line[4])
            $("#registers").empty()
            $("#stack").empty()
            for(i of line[5]){
                console.log(i)
                $("#registers").append(
                    "<div class=\"register_stack\">"+
                        "<p style=\"width: 40%; text-align: center;\">"+i[0]+"</p>"+
                        "<p style=\"width: 40%; text-align: center;\">"+i[1]+"</p>"+
                    "</div>"
                )
            }
            for(i of line[6]){
                $("#stack").append(
                    "<div class=\"register_stack\">"+
                        "<p style=\"width: 40%; text-align: center;\">"+i[0]+"</p>"+
                        "<p style=\"width: 40%; text-align: center;\">"+i[1]+"</p>"+
                    "</div>"
                )
            }
            $("#view_info").show()
        }
    })
}
function show_edit(line=null){
    $.ajax({
        success(){
            am_reg=0;
            am_st=0;
            stack=[];
            registers=[];
            type=0;

            if(line!=null) {
                type=0;
                id=line[0];
                console.log(line);
                $("#edit_id").text("#" + line[0])
                $("#edit_name").val(line[1])
                $("#edit_difficulty").val(line[2])
                $("#edit_success").text("Success amount: " + line[3])
                $("#edit_description").val(line[4])
                $("#edit_registers").empty()
                $("#edit_stack").empty()
                $("#edit_registers").append("<input type='button' class=\"btn-secondary\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_register()\"" +
                    "value='+'>")
                for(let i of line[5]){
                    $("#edit_registers").append(
                        "<div id='register_"+am_reg+"' class=\"register_stack\">"+
                            "<input type=\"text\" style=\"width: 40%\" value='"+i[0]+"' required onchange='register_change("+am_reg+","+"0,"+"this.value"+")'>" +
                            "<input type=\"text\" style=\"width: 40%\" value='"+i[1]+"' required onchange='register_change("+am_reg+","+"1,"+"this.value"+")'>" +
                            "<input type='button' class=\"btn-danger\" onclick=\"remove_register("+am_reg+")\" " +
                        "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
                        "</div>"
                    )
                    registers.push([i[0],i[1]])
                    am_reg++;
                }
                $("#edit_stack").append("<input type='button' class=\"btn-secondary\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_stack()\"" +
                    "value='+'>")
                for(let i of line[6]){
                    $("#edit_stack").append(
                        "<div id='stack_"+am_st+"' class=\"register_stack\">"+
                            "<input type=\"text\" style=\"width: 40%\" value='"+i[0]+"' required onchange='stack_change("+am_st+","+"0,"+"this.value"+")'>" +
                            "<input type=\"text\" style=\"width: 40%\" value='"+i[1]+"' required onchange='stack_change("+am_st+","+"1,"+"this.value"+")'>" +
                            "<input type='button' class=\"btn-danger\" onclick=\"remove_stack("+am_st+")\" " +
                        "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
                        "</div>"
                    )
                    stack.push([i[0],i[1]])
                    am_st++;
                }
                $("#form_edit").attr("action", "/tasks/edit/?id="+line[0]+"&registers="+registers+"&stack="+stack)
            }else {
                type=1;
                $("#edit_id").text("")
                $("#edit_name").val("")
                $("#edit_difficulty").val(0)
                $("#edit_success").text("Success amount: 0")
                $("#edit_description").val("")
                $("#edit_registers").empty()
                $("#edit_registers").append("<input type='button' class=\"btn-secondary\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_register()\"" +
                    "value='+'>")
                $("#edit_stack").empty()
                $("#edit_stack").append("<input type='button' class=\"btn-secondary\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_stack()\"" +
                    "value='+'>")
                $("#form_edit").attr("action", "/tasks/add/?registers="+registers+"&stack="+stack)
            }
            $("#edit_info").show()
        }
    })
}
function find_by_id(data){
    $.ajax({
        success(){
            console.log(data)
            if($("#find_id").val()==""){
                alert("Empty value!")
                return
            }
            for(var i=0;i<data.length;i++){
                if(data[i][0]==$("#find_id").val()){
                    console.log(data[i])
                    show(data[i]);
                    return;
                }
            }
            alert("Task was not found!")
        }
    })
}
function remove_register(k){
    let id="#register_"+k
    registers[k][0]=""
    registers[k][1]=""
    update();
    $(id).remove();
}
function remove_stack(k){
    let id="#stack_"+k
    stack[k][0]=""
    stack[k][1]=""
    update();
    $(id).remove();
}
function add_register(){
    $("#edit_registers").append(
        "<div id='register_"+am_reg+"' class=\"register_stack\">"+
            "<input type=\"text\" style=\"width: 40%\" required onchange='register_change("+am_reg+","+"0,"+"this.value"+")'>" +
            "<input type=\"text\" style=\"width: 40%\" required onchange='register_change("+am_reg+","+"1,"+"this.value"+")'>" +
            "<input type='button' class=\"btn-danger\" onclick=\"remove_register("+am_reg+")\" " +
        "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
        "</div>"
    )
    registers.push(["",""])
    am_reg++;
}
function add_stack(){
    $("#edit_stack").append(
        "<div id='stack_"+am_st+"' class=\"register_stack\">"+
            "<input type=\"text\" style=\"width: 40%\" required onchange='stack_change("+am_st+","+"0,"+"this.value"+")'>" +
            "<input type=\"text\" style=\"width: 40%\" required onchange='stack_change("+am_st+","+"1,"+"this.value"+")'>" +
            "<input type='button' class=\"btn-danger\" onclick=\"remove_stack("+am_st+")\" " +
        "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
        "</div>"
    )
    stack.push(["",""])
    am_st++;
}

function register_change(id,type,value){
    registers[id][type]=value;
    update();
}
function stack_change(id,type,value){
    stack[id][type]=value;
    update();
}