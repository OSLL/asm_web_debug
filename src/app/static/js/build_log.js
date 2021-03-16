var codemirrorEditor = CodeMirror.fromTextArea(document.getElementById('build_log'), {
                                    mode: 'shell',
                                    gutters: ["CodeMirror-linenumbers"],
                                    theme: 'eclipse',
                                    readOnly: 'nocursor',
                                    }); 
        
codemirrorEditor.setSize('100%', 'auto');
codemirrorEditor.getScrollerElement().style.minHeight = '100px';
codemirrorEditor.getScrollerElement().style.maxHeight = '400px';
codemirrorEditor.refresh();