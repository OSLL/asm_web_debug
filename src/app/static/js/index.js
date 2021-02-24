function buttonClick(btn){
	alert("You pressed " + btn.name);
}

$(function() {
	var reg = document.querySelector('#register_body');
	let registers = [
		['A1', 'B2', 'C3', 'A6'],['0xff3', '0x546', '0xaaa', '0x123'], 
		['A1', 'B2', 'C3', 'A6'],['0xff3', '0x546', '0xaaa', '0x123']
		];
	createTableReg(reg, registers);

	var stack = document.querySelector('#stack_body');
	let s_elements = [['0xff', '0xaaf', '0x030', '0xccc'],['exmpl', 'exmpl', 'exmpl', 'exmpl']];
	createTableStack(stack, s_elements);

	function createTableReg(parent, arr){
		for(var i=0; i<arr[0].length; i++){
			var tr = document.createElement('tr');
			for(var j=0; j<4; j++){
				var td = document.createElement('div');
				if(j%2){
					var input = document.createElement('input');
					input.value = arr[j][i];
					td.appendChild(input);
				}
				else td.appendChild(document.createTextNode(arr[j][i]));
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
});