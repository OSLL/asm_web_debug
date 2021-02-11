var codemirrorEditor = CodeMirror.fromTextArea(document.getElementById('build_log'), {
                                    mode: 'shell',
                                    gutters: ["CodeMirror-linenumbers"],
                                    theme: 'eclipse',
                                    readOnly: 'nocursor',
                                    }); 
        
codemirrorEditor.setSize('100%', 100);
codemirrorEditor.refresh();