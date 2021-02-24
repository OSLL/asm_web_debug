var codemirrorEditor = CodeMirror.fromTextArea(document.getElementById('code'), {
                                    lineNumbers: true,
                                    mode: 'gas',
                                    gutters: ["CodeMirror-linenumbers", "breakpoints"],
                                    theme:'eclipse',
                                    });

codemirrorEditor.on("gutterClick", function(cm, n) {
                                var info = cm.lineInfo(n);
                                cm.setGutterMarker(n, "breakpoints", info.gutterMarkers ? null : makeMarker());
                                });

function makeMarker() {
                        var marker = document.createElement("div");
                        marker.style.color = "#822";
                        marker.style.position = "absolute";
                        marker.style.left = "-40px";
                        marker.innerHTML = "●";
                        return marker;
                        };

codemirrorEditor.getGutterElement().style['width'] = '45px';
codemirrorEditor.getGutterElement().style['text-align'] = 'right';
codemirrorEditor.refresh();