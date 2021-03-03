function buttonClick(btn){
	alert("You pressed " + btn.name);
}

$(function() { 
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
	$("#HexView").click(function (e){
		var editor = $('.CodeMirror')[0].CodeMirror;
		var code = editor.getValue();

		function hexdump(buffer) {
    		var lines = [];
    		for (var b = 0; b < buffer.length; b += 16) {

       			var block = buffer.slice(b, b + 16);
        		var addr = b.toString(16).padStart(8, '0')

        		var codes = block.split('').map(function (ch) {
            		var code = ch.charCodeAt(0)
            		return ' ' + code.toString(16).padStart(2, '0').toUpperCase();
            		}).join("");
       			codes += " 00".repeat(16 - block.length);
        		var chars = block.replace(/[\x00-\x1F]/g, '.');
        		lines.push(addr + " " + codes + "  " + chars);
    			}
    	return lines.join("\\n");
		};

		// submit form with openning new tab
		var form = $('#hidden_form')
		form.trigger("reset")
		form.attr('method', "POST");
		form.attr('action', "/hexview")
		form.attr('target', "_blank")
	
		var input = $("#hidden_input")
		input.attr('type', "text")
		input.attr('name', "hexview")
		input.attr('value', hexdump(code))
		
		input.appendTo(form)
		form.appendTo($('body'))
		
		form.submit()

	}); 
});