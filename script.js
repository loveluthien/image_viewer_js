// function openFile() {
// 	var fileInput = document.getElementById('file-input').value;
// 	message_to_server['file'] = fileInput;
// 	// websocket.send(JSON.stringify(message_to_server));
// 	// fileInput.click();
// 	// console.log(fileInput);
// };

function zoom(event) {
	if (event.deltaY < 0) {
		zoom_level = Math.max(zoom_level/2, 1/4)
	}
	else {
		zoom_level = Math.min(zoom_level*2, 8)
	};
	message_to_server['zoom_level'] = zoom_level;
	message_to_server['updates'] = ['zoom_level'];
	// console.log(zoom_level);
	websocket.send(JSON.stringify(message_to_server));
};


function img_show(output) {

	var layout = {
		// title: 'Map',
		height: 400+100,
		width: 500+100,
		autosize: false,
		xaxis: {
			range: output.img.x_range,
			title: {
				text: 'R.A. [deg]',
				// font: {
				// family: 'Courier New, monospace',
				// size: 18,
				// color: '#7f7f7f'}
			},
			// autorange: "reversed",
			autorange: false,
			zeroline: false,
		},
		yaxis: {
			autorange: false,
			range: output.img.y_range,
			title: 'Dec. [deg]',
			// scaleanchor: "x",
			// scaleratio: 1,
			zeroline: false,
		},
		automargin: false,
		margin: {
			t: 20, b: 80, l: 80, r: 20
		},
	};

	var config = {
		'staticPlot': false,
		// 'staticPlot': true,
		'displayModeBar': false
	};

	var data = [
		{
			x: output.img.x,
			y: output.img.y,
			z: output.img.data,
			type: 'heatmap',
			showscale: false,
			zauto: false,
			zmax: output.img.vmax,
			zmin: output.img.vmin,
		}
	];

	Plotly.react('Image', data, layout, config);
};

function hist_show(output) {

	// console.log('update hist')
	
	var hist_layout = {
		height: 200,
		xaxis: {
			// range: [-2, 4],
			title: 'Intensity (Jy/beam)',
			zeroline: false,
		},
		yaxis: {
			title: 'N',
			type: 'log',
			zeroline: false,
		}, 
		showlegend: false,
		automargin: false,
		margin: {
			t: 20, b: 50, l: 50, r: 20
		},
		showlegend: true,
		legend: {
			x: 1,
			xanchor: 'right',
			y: 1
		}
	};

	var config = {
		'staticPlot': true,
		'displayModeBar': false
	};

	var line_min = {
		x: [output.hist.vmin, output.hist.vmin],
		y: [0, output.hist.count_max],
		mode: 'lines',
		name: 'Lines',
		line: { color: 'red', },
		name: '99%',
		showlegend: true,
	};

	var line_max = {
		x: [output.hist.vmax, output.hist.vmax],
		y: [0, output.hist.count_max],
		mode: 'lines',
		name: 'Lines',
		line: { color: 'red', },
		showlegend: false,
	};

	var hist_data = {
			x: output.hist.x,
			y: output.hist.data,
			type: 'scatter',
			line: { shape: 'hvh' },
			showlegend: false,
		};

	Plotly.react('Hist', [hist_data, line_min, line_max],
		hist_layout, config);

};

function prof_x_show(output) {

	// console.log('update prof_x');
	// console.log(output.prof_x.x[0], output.prof_x.x[output.prof_x.x.length - 1]);
	// console.log(output.prof_x.x_range);
	// console.log(output.prof_y.x_range);

	var config = {
		'staticPlot': true,
		'displayModeBar': false
	};

	var prof_x_data = [
		{
			y: output.prof_x.data,
			x: output.prof_x.x,
			type: 'scatter',
			line: {shape: 'hvh'},
		}
	];
	
	var prof_x_layout = {
		// autosize: false,
		title: 'X profile',
		yaxis: {
			title: 'Intensity (Jy/beam)',
			zeroline: false,
		},
		xaxis: {
			title: 'pixel',
			zeroline: false,
			range: output.prof_x.x_range,
		}, 
		height: 300,
		automargin: false,
		margin: {
			t: 40, b: 60, l: 80, r: 10
		},
	};

	Plotly.react('prof_x', prof_x_data, prof_x_layout, config);

};

function prof_y_show(output) {

	// console.log('update prof_y');

	var config = {
		'staticPlot': true,
		'displayModeBar': false
	};

	var prof_y_data = [
		{
			y: output.prof_y.data,
			x: output.prof_y.x,
			type: 'scatter',
			line: {shape: 'hvh'},
		}
	];
	
	var prof_y_layout = {
		// autosize: false,
		title: 'Y profile',
		yaxis: {
			title: 'Intensity (Jy/beam)',
			zeroline: false,
		},
		xaxis: {
			range: output.prof_x.x_range,
			title: 'pixel',
			zeroline: false,
		}, 
		height: 300,
		automargin: false,
		margin: {
			t: 40, b: 60, l: 80, r: 10
		},
	};

	Plotly.react('prof_y', prof_y_data, prof_y_layout, config);

};

function prof_z_show(output) {

	// console.log('update prof_z');

	var config = {
		'staticPlot': true,
		'displayModeBar': false
	};

		var prof_z_data = [
		{
			y: output.prof_z.data,
			x: output.prof_z.x,
			type: 'scatter',
			line: {shape: 'hvh'},
		}
	];
	
	var prof_z_layout = {
		// autosize: false,
		title: 'Z profile',
		yaxis: {
			title: 'Intensity (Jy/beam)',
			zeroline: false,
		},
		xaxis: {
			title: 'Frequency (GHz)',
			zeroline: false,
		}, 
		height: 300,
		automargin: false,
		margin: {
			t: 40, b: 60, l: 80, r: 10
		},
	};

	Plotly.react('prof_z', prof_z_data, prof_z_layout, config);

};


const websocket = new WebSocket("ws://localhost:9107/");

// default message
var message_to_server = {
	'greeting': 'Hello kitty?',
	'i_ch': 0,
	'cursor_x': 0,
	'cursor_y': 0,
	'zoom_level': 1,
	'updates': [],
};

var zoom_level, temp_img, temp_x, temp_y;

// Send the input to the backend
websocket.onopen = function () {
	
	websocket.send(JSON.stringify(message_to_server));
	console.log("Hi moron, server is connected!");
	message_to_server['greeting'] = 'I say good-bye.';

};


// Receive the output from the backend
websocket.onmessage = function (event) {

	var output = JSON.parse(event.data);

	var Image = document.getElementById("Image"),
		hoverInfo = document.getElementById('hoverinfo'),
		slider = document.getElementById("myRange"),
		i_ch = document.getElementById("rangeValue");
	
	// load some default variables
	zoom_level = output.zoom_level;
	slider.max = output.data_size[2] - 1;
	i_ch.innerHTML = slider.value;
	message_to_server['cen_pix'] = output.cen_pix;
	message_to_server['zoom_level'] = zoom_level;


	// update panels
	for (var field in output) {
		if (field == 'img') {
			img_show(output);
			temp_img = output.img.data;
			temp_x = output.img.x;
			temp_y = output.img.y;
		};
		if (field == 'hist') hist_show(output);
		if (field == 'prof_x') prof_x_show(output);
		if (field == 'prof_y') prof_y_show(output);
		if (field == 'prof_z') prof_z_show(output);
	}


	// showing image pixel index and its intensity on cursor position
	Image.on('plotly_hover', function (data) {
		var pix_x = data.points[0].pointIndex[1];
		var pix_y = data.points[0].pointIndex[0];

		if (message_to_server['cursor_x'] != pix_x
			|| message_to_server['cursor_y'] != pix_y) {
			message_to_server['cursor_x'] = pix_x;
			message_to_server['cursor_y'] = pix_y;
			message_to_server['updates'] = ['cursor'];
			websocket.send(JSON.stringify(message_to_server));
		};
		var avg_text = '';
		
		if (zoom_level < 1) {
			avg_text = '; ' + (1 / zoom_level).toFixed(0) + 'x'
				+ (1 / zoom_level).toFixed(0) + ' avg.';
		};
		
		if (temp_img[pix_y][pix_x] != null) {
			var ss = ('Image: (' + output.raw_xpix + ','
				+ output.raw_ypix + '); Intensity: ' + temp_img[pix_y][pix_x].toFixed(5)
				+ ' (Jy/beam' + avg_text + ')');
			hoverInfo.innerHTML = ss;
		};
	});

	// move the image center by clicking
	Image.on('plotly_click', function (data) {
		var pix_x = data.points[0].pointIndex[1];
		var pix_y = data.points[0].pointIndex[0];
		message_to_server['cen_pix'][0] = output.raw_xpix;
		message_to_server['cen_pix'][1] = output.raw_ypix;

		if (message_to_server['cen_pix'][0] != output.cen_pix[0]
			|| message_to_server['cen_pix'][1] != output.cen_pix[1]) {

			message_to_server['cursor_x'] = pix_x;
			message_to_server['cursor_y'] = pix_y;
			message_to_server['updates'] = ['center'];
			websocket.send(JSON.stringify(message_to_server));
		};
	});

	

	Image.onwheel = zoom;
	
	slider.oninput = function () {
		if (message_to_server['i_ch'] != this.value) {
			message_to_server['i_ch'] = this.value;
			message_to_server['updates'] = ['i_ch'];
			websocket.send(JSON.stringify(message_to_server));
			i_ch.innerHTML = this.value;
		}
	}
	
};


// function importData() {
	// let input = document.createElement('input');
	// input.type = 'file';
	// input.onchange = _ => {
	//   // you can use this method to get file and perform respective operations
	// 		let files =   Array.from(input.files);
	// 		console.log(input.val());
	// 		// message_to_server['file'] = files;
	// 		// websocket.send(JSON.stringify(message_to_server));
	// 	};
	// input.click();
// }

// function openFileDialog() {
// 	var fileInput = document.getElementById('file-input');
// 	fileInput.click();


// 	// Add an event listener to handle file selection
// 	fileInput.addEventListener('change', function(event) {
// 		var selectedFile = event.target.files[0];

//         var fileName = selectedFile.name;
//         var filePath = URL.createObjectURL(selectedFile);
//         console.log('Selected file name:', fileName);
//         console.log('Selected file path:', filePath);
// 		// console.log('Selected file:', selectedFile);
// 		// Perform further actions with the selected file
// 	});
// }


