let am_reg=0;
let am_st=0;
let stack=[];
let registers=[];
let type=0;
let id;

const url = 'http://127.0.0.1:8080'

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
function show(task_id){
    $.ajax({
        url: url + '/tasks/' + task_id,
        type: 'Get',
        success: function(result){
            $("#task_id").text("#"+result._id)
            $("#task_name").text(result.name)
            $("#task_difficulty").text("Difficulty: " + result.difficulty)
            $("#task_success").text("Success amount: " + result.success)
            $("#task_description").text(result.description)
            $("#registers").empty()
            $("#stack").empty()
            for(var [name, value] of Object.entries(result.registers)){
                $("#registers").append(
                    "<div class=\"register_stack\">"+
                        "<p style=\"width: 40%; text-align: center;\">"+name+"</p>"+
                        "<p style=\"width: 40%; text-align: center;\">"+value+"</p>"+
                    "</div>"
                )
            }
            for(var [name, value] of Object.entries(result.stack)){
                $("#stack").append(
                    "<div class=\"register_stack\">"+
                        "<p style=\"width: 40%; text-align: center;\">"+name+"</p>"+
                        "<p style=\"width: 40%; text-align: center;\">"+value+"</p>"+
                    "</div>"
                )
            }
            $("#view_info").show()
        }
    })
}

function add_task(){
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
    $("#edit_info").show()

}


function show_edit(task_id){
    $.ajax({
        url: url + '/tasks/' + task_id,
        type: 'Get',
        success: function(result){
            am_reg=0;
            am_st=0;
            stack=[];
            registers=[];
            type=0;

            id=result._id;
            $("#edit_id").text("#" + result._id)
            $("#edit_name").val(result.name)
            $("#edit_difficulty").val(result.difficulty)
            $("#edit_success").text("Success amount: " + result.success)
            $("#edit_description").val(result.description)
            $("#edit_registers").empty()
            $("#edit_stack").empty()
            $("#edit_registers").append("<input type='button' class=\"btn-secondary\" " +
                "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_register()\"" +
                "value='+'>")
            for(var [name, value] of Object.entries(result.registers)){
                $("#edit_registers").append(
                    "<div id='register_"+am_reg+"' class=\"register_stack\">"+
                        "<input type=\"text\" style=\"width: 40%\" value='"+name+"' required onchange='register_change("+am_reg+","+"0,"+"this.value"+")'>" +
                        "<input type=\"text\" style=\"width: 40%\" value='"+value+"' required onchange='register_change("+am_reg+","+"1,"+"this.value"+")'>" +
                        "<input type='button' class=\"btn-danger\" onclick=\"remove_register("+am_reg+")\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
                    "</div>"
                )
                registers.push([name,value])
                am_reg++;
            }
            $("#edit_stack").append("<input type='button' class=\"btn-secondary\" " +
                "style=\"width: 35px; height: 35px; border-radius: 50%\" onclick=\"add_stack()\"" +
                "value='+'>")
            for(var [name, value] of Object.entries(result.stack)){
                $("#edit_stack").append(
                    "<div id='stack_"+am_st+"' class=\"register_stack\">"+
                        "<input type=\"text\" style=\"width: 40%\" value='"+name+"' required onchange='stack_change("+am_st+","+"0,"+"this.value"+")'>" +
                        "<input type=\"text\" style=\"width: 40%\" value='"+value+"' required onchange='stack_change("+am_st+","+"1,"+"this.value"+")'>" +
                        "<input type='button' class=\"btn-danger\" onclick=\"remove_stack("+am_st+")\" " +
                    "style=\"width: 35px; height: 35px; border-radius: 50%\" value='-'>"+
                    "</div>"
                )
                stack.push([name,value])
                am_st++;
            }
            $("#form_edit").attr("action", "/tasks/edit/?id="+id+"&registers="+registers+"&stack="+stack)
            $("#edit_info").show()
        }
    })
}
function find_by_id(){
    let task_id = $("#find_id").val()
    $.ajax({
        url: url + '/tasks/' + task_id,
        type: 'Get',
        success: function(result){
            if($("#find_id").val()==""){
                alert("Empty value!")
                return
            }
            show(result._id);
        },
        error: function(error){
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
