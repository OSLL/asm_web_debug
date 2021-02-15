$("#Run").click(function (e){
	codemirrorEditor.save();
	var code = codemirrorEditor.getValue();
	var breakpoints = [];
	var lines = codemirrorEditor.lineCount();
	
	for (var i = 0; i < lines; i++) {
		var info = codemirrorEditor.lineInfo(i);
		if (info.gutterMarkers)
			breakpoints.push(i+1);
	}

	$.ajax({
		url: '/index',
		type:'POST',
		dataType: 'json',
		contenType: 'application/json',
		data: {'code': code, 'breakpoints': JSON.stringify(breakpoints)},
	});
	e.preventDefault();
});