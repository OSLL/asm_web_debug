var codemirrorEditor = CodeMirror.fromTextArea(document.getElementById('build_log'), {
                                    mode: 'gas',
                                    gutters: ["CodeMirror-linenumbers"],
                                    theme: 'eclipse',
                                    readOnly: 'nocursor',
                                    lineWrapping: true,
                                    }); 
        
codemirrorEditor.setSize('100%', 'auto');
codemirrorEditor.getScrollerElement().style.minHeight = '100px';
codemirrorEditor.getScrollerElement().style.maxHeight = '400px';
codemirrorEditor.refresh();