function buttonClick(btn){
	alert("You pressed " + btn.name);
}

$(function() {
	var hash_saved_code = ''

	test_table_create()		// test table creation for registers an stacks

	setup_button_handle()	// setup button handling

	capture_hotkey() 	// setup capturing browser hotkyes


	function test_table_create(){
		var reg = document.querySelector('#register_body');
		let registers = [
			['A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6'],['0xff3', '0x546', '0xaaa', '0x123', '0xff3', '0x546', '0xaaa', '0x123', '0x546', '0xaaa', '0x123', '0xff3']];
		createTableReg(reg, registers);
	
		var stack = document.querySelector('#stack_body');
		let s_elements = [['0xff', '0xaaf', '0x030', '0xccc'],['exmpl', 'exmpl', 'exmpl', 'exmpl']];
		createTableStack(stack, s_elements);
	}

	function createTableReg(parent, arr){
		var i = 0;
		while(i<arr[0].length){
			var tr = document.createElement('tr');
			for(var j=0; j<4; j++){
				var td = document.createElement('div');
				if(j%2){
					var input = document.createElement('input');
					input.value = arr[j%2][i];
					input.name = arr[0][i];
					input.classList.add('register-input')
					td.appendChild(input);
					i++;
				}
				else td.appendChild(document.createTextNode(arr[j%2][i]));
				tr.appendChild(td);
			}
			parent.appendChild(tr);	
		}
	}

	function createTableStack(parent, arr){
		var alen = arr[0].length;

		for(var i=0; i<alen; i++){
			var tr = document.createElement('tr');
			for(var j=0; j<2; j++){
				var td = document.createElement('div');
				var text = document.createTextNode(arr[j][i]);
				td.appendChild(text);
				tr.appendChild(td);
			}
			parent.appendChild(tr);			
		}
	}

	function capture_hotkey(){
		var block_saving = false

		$(document).bind('keydown', function(e) {
			// capture Ctrl+S for data saving
            if(e.ctrlKey && (e.which == 83)) {
				e.preventDefault();	
				var [is_equal, hash] = check_hash_code(hash_saved_code)
				if (is_equal)
				{
					warning_alert('Вы уже сохраняли этот код!')
					return
				}
				else
					hash_saved_code = hash
				
				// TODO: save code 
				success_alert('Код сохранён!');
			}
        });
	}

	function get_code_and_breakpoints(){
		var editor = $('.CodeMirror')[0].CodeMirror;
		var breakpoints = [];
		var lines = editor.lineCount();
		
		for (var i = 0; i < lines; i++) {
			var info = editor.lineInfo(i);
			if (info.gutterMarkers)
				breakpoints.push(i+1);
		};
		return [editor.getValue(), breakpoints]
	}

	function setup_button_handle(){
		// compile button
		$("#Compile").click(function (e){
			var [code, breakpoints] = get_code_and_breakpoints()
			
			$.ajax({
				url: '/compile',
				type:'POST',
				dataType: 'json',
				contenType: 'application/json',
				data: {'code': code, 'breakpoints': JSON.stringify(breakpoints)},
				success: function(resp){
					console.log(resp)
					success_alert('Код успешно отправлен')
				},
				error: function(resp){
					failure_alert('Код не был отправлен. ' + resp.responseText)
				},
			});
			e.preventDefault();
		}); 

		// debug-button
		setup_debug_button_handle()

		// hexview button
		$("#HexView").click(function (e){
			var editor = $('.CodeMirror')[0].CodeMirror;
			var code = editor.getValue();
	
			// submit form with openning new tab
			var form = $('#hidden_form')
			form.trigger("reset")
			form.attr('method', "POST");
			form.attr('action', "/hexview")
			form.attr('target', "_blank")
		
			var input = $("#hidden_textarea")
			input.attr('type', "text")
			input.attr('name', "hexview")
			input.val(code)
			
			input.appendTo(form)
			form.appendTo($('body'))
			
			form.submit()
	
		}); 
	}

	function setup_debug_button_handle(){
		$("#Debug").click(function (e){
			send_debug_command(e.target)		
		});
		$("#Continue").click(function (e){
			send_debug_command(e.target)		
		});
		$("#Step_into").click(function (e){
			send_debug_command(e.target)		
		});
		$("#Step_over").click(function (e){
			send_debug_command(e.target)		
		});
		$("#Step_out").click(function (e){
			send_debug_command(e.target)		
		});
	}


	function send_debug_command(button){
		$.ajax({
			url: '/debug',
			type:'POST',
			contenType: 'application/json',
			data: {'debug_command': button.getAttribute('debug_code')},
			success: function(response){
				console.log(response);
			},
			error: function(response){
				console.log(response);
			},
		});
	}


	function calc_hash_code(){
		return $.MD5(JSON.stringify(get_code_and_breakpoints()))
	}

	function check_hash_code(hash){
		var new_hash = calc_hash_code()
		if (hash != new_hash)
			return [false, new_hash]
		else
			return [true, new_hash] 
	}
	
	function success_alert(text, delay=2000){
		$("#ajax-alert").removeClass()
		$("#ajax-alert").addClass('alert alert-success')
		_show_alert(text, delay)
	}

	function failure_alert(text, delay=2000){
		$("#ajax-alert").removeClass()
		$("#ajax-alert").addClass('alert alert-danger')
		_show_alert(text, delay)
	}

	function warning_alert(text, delay=2000){
		$("#ajax-alert").removeClass()
		$("#ajax-alert").addClass('alert alert-warning')
		_show_alert(text, delay)
	}

	function _show_alert(text, delay=2000)
	{
		$("#ajax-alert").text(text);
		$("#ajax-alert").show();
		$("#ajax-alert").delay(delay).fadeOut();
	}
});
