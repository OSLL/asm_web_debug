function buttonClick(btn){
	alert("You pressed " + btn.name);
}

$(function() {
	var reg = document.querySelector('#register_body');
	let registers = [
		['A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6'],['0xff3', '0x546', '0xaaa', '0x123', '0xff3', '0x546', '0xaaa', '0x123', '0x546', '0xaaa', '0x123', '0xff3']];
	createTableReg(reg, registers);

	var stack = document.querySelector('#stack_body');
	let s_elements = [['0xff', '0xaaf', '0x030', '0xccc'],['exmpl', 'exmpl', 'exmpl', 'exmpl']];
	createTableStack(stack, s_elements);

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

	$("#Compile").click(function (e){
		var editor = $('.CodeMirror')[0].CodeMirror;
		var code = editor.getValue();
		var breakpoints = [];
		var lines = editor.lineCount();
		
		for (var i = 0; i < lines; i++) {
			var info = editor.lineInfo(i);
			if (info.gutterMarkers)
				breakpoints.push(i+1);
		};

		$.ajax({
			url: '/compile',
			type:'POST',
			dataType: 'json',
			contenType: 'application/json',
			data: {'code': code, 'breakpoints': JSON.stringify(breakpoints)},
			success: function(){
				console.log(code + "\n", breakpoints);
				$("#ajax-alert").addClass('alert alert-success').text('Код успешно отправлен');
				$("#ajax-alert").show();
				$("#ajax-alert").delay(2000).fadeOut();
			},
			error: function(){
				$("#ajax-alert").addClass('alert alert-danger').text('Код не был отправлен');
				$("#ajax-alert").show();
				$("#ajax-alert").delay(2000).fadeOut();
			},
		});
		e.preventDefault();
	});


	$("#Debug").click(function (e){
		send_debug_command(e.target)		
	});


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
});