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
});