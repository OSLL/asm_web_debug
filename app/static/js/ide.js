(function() {
    const State = Object.freeze({
        stopped: {
            id: "stopped",
            buttons: [
                { name: "Run", id: "run", style: "success" },
            ]
        },
        paused: {
            id: "paused",
            buttons: [
                { name: "Stop", id: "kill", style: "danger" },
                { name: "Continue", id: "continue", style: "success" },
                { name: "Step into", id: "step_into" },
                { name: "Step over", id: "step_over" },
                { name: "Step out", id: "step_out" },
            ]
        },
        running: {
            id: "running",
            buttons: [
                { name: "Stop", id: "kill", style: "danger" },
                { name: "Pause", id: "pause", style: "warning" },
            ]
        }
    });

    const codeId = location.pathname.slice(1).split('/')[0];

    const $debugButtons = $("#debug-buttons");
    const $output = $("#build_log");
    const $registerTable = $("#register_body");

    const ws = new WebSocket(`${(window.location.protocol === "https") ? "wss" : "ws"}://${window.location.host}/ws_ide`);

    let state = State.stopped;
    let activeLine = 0;

    let codeMirror = null;
    let doc = null;

    $(document).bind('keydown', function(e) {
        // capture Ctrl+S for data saving
        if (e.ctrlKey && e.which === 83) {
            e.preventDefault();	
            saveCode();
        }
    });

    function showAlert(content, kind) {
        const $alert = $("#ajax-alert");
        $alert.html(content);
        $alert.show();
        $alert.removeClass().addClass(`alert alert-${kind}`);
        $alert.delay(3000).fadeOut();
    }

    function initEditor() {
        codeMirror = CodeMirror.fromTextArea($("#code")[0], {
            lineNumbers: true,
            mode: "gas",
            viewportMargin: Infinity,
            gutters: ["CodeMirror-linenumbers", "breakpoints"],
            theme: "eclipse",
            lineWrapping: true,
        });

        doc = codeMirror.getDoc();

        let bpoints = $(".container").contents().filter(function(){
            return this.nodeType == 8;
        })[0].nodeValue;
        addBreakpoints(JSON.parse(bpoints));

        codeMirror.on("gutterClick", (_, line) => {
            const info = codeMirror.lineInfo(line);
            const breakpoint = info.gutterMarkers ? null : (() => {
                const marker = document.createElement("div");
                marker.style.color = "#a44";
                marker.style.position = "absolute";
                marker.style.left = "-40px";
                marker.style.top = "-7px";
                marker.style.fontSize = "24px";
                marker.innerHTML = "●";
                return marker;
            })();
            codeMirror.setGutterMarker(line, "breakpoints", breakpoint);

            if (state !== State.stopped) {
                sendMessage({
                    "type": breakpoint ? "add_breakpoint" : "remove_breakpoint",
                    "line": line + 1
                });
            }
        });

        codeMirror.on("beforeChange", (_, change) => {
            if (state !== State.stopped) {
                change.cancel();
            }
        });

        codeMirror.getGutterElement().style['width'] = '45px';
        codeMirror.getGutterElement().style['text-align'] = 'right';
        codeMirror.getScrollerElement().style.minHeight = '400px';
        codeMirror.setSize("100%", "100%");
        codeMirror.refresh();
    }

    function getBreakpoints() {
        const breakpoints = [];
        doc.eachLine(lineHandle => {
            const info = doc.lineInfo(lineHandle);
            if (info.gutterMarkers) {
                breakpoints.push(info.line + 1);
            }
        });

        return breakpoints;
    }

    function addBreakpoints(breakpoints){
        breakpoints.forEach(codeline => {
            addBreakpoint(codeline - 1);
        });
        codeMirror.getGutterElement().style['width'] = '45px';
        codeMirror.getGutterElement().style['text-align'] = 'right';
        codeMirror.getScrollerElement().style.minHeight = '400px';
        codeMirror.setSize("100%", "100%");
        codeMirror.refresh();
    }

    function addBreakpoint(codeline){
        const info = codeMirror.lineInfo(codeline);
        const breakpoint = info.gutterMarkers ? null : (() => {
            const marker = document.createElement("div");
            marker.style.color = "#a44";
            marker.style.position = "absolute";
            marker.style.left = "-40px";
            marker.style.top = "-7px";
            marker.style.fontSize = "24px";
            marker.innerHTML = "●";
            return marker;
        })();
        codeMirror.setGutterMarker(codeline, "breakpoints", breakpoint);
        if (state !== State.stopped) {
            sendMessage({
                "type": breakpoint ? "add_breakpoint" : "remove_breakpoint",
                "line": codeline + 1
            });
        }
    }

    function onDebugButtonClick(id) {
        if (id === "run") {
            setState(State.running);
            $output.val("");
            sendMessage({
                "type": "run",
                "source": doc.getValue(),
                "input": "",
                "breakpoints": getBreakpoints()
            });
        } else {
            sendMessage({
                "type": id
            });
        }
    }

    function setState(newState) {
        state = newState;

        $debugButtons.html("");
        const  $rightDebugButtons = $(`<div style="float: right;"></div>`);
        for (const button of state.buttons) {
            const $button = $(`<button class="btn btn-outline-${button.style || 'info'}" style="margin: 1em 1em auto auto; width: 5.3em; white-space: pre-line;">` + 
                (button.id === "run" ? `<i class="fa fa-play" aria-hidden="true"></i></br>` : ``) + 
                (button.id === "kill" ? `<i class="fa fa-stop" aria-hidden="true"></i></br>` : ``) + 
                (button.id === "continue" ? `<i class="fa fa-step-forward" aria-hidden="true"></i></br>` : ``) + 
                (button.id === "pause" ? `<i class="fa fa-pause" aria-hidden="true"></i></br>` : ``) + 
                `${button.name}</button>`);
            $button.on("click", () => {
                onDebugButtonClick(button.id);
            });
            if(state.id === "paused" && button.id !== "kill")
                $button.appendTo($rightDebugButtons);
            else
                $button.appendTo($debugButtons);
        }
        $rightDebugButtons.appendTo($debugButtons);

        doc.eachLine(lineHandle => {
            doc.removeLineClass(lineHandle, "background", "active-line");
        });

        if (state === State.paused) {
            doc.addLineClass(activeLine - 1, "background", "active-line");
        } else {
            $registerTable.html("");
        }
    }

    function saveCode() {
        $.ajax({
            url: "/save/" + codeId,
            type: "POST",
            dataType: "json",
            data: {
                code: doc.getValue(),
                breakpoints: JSON.stringify(getBreakpoints()),
                arch: $("#arch_select").val()
            },
            success: () => {
                showAlert("Source code was saved", "success");
            }
        })
    }

    function sendMessage(msg) {
        ws.send(JSON.stringify(msg));
    }

    ws.addEventListener("message", (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === "running") {
            setState(State.running);
        } else if (msg.type === "finished") {
            setState(State.stopped);
        } else if (msg.type === "paused") {
            activeLine = msg.line;
            setState(State.paused);
            sendMessage({
                "type": "get_registers"
            });
        } else if (msg.type === "compilation_result") {
            if (!msg.successful) {
                $output.val(msg.stderr);
                setState(State.stopped);
                showAlert("Compilation failed", "danger");
            }
        } else if (msg.type === "registers") {
            $registerTable.html("");
            for (const [reg, val] of msg.data) {
                const editable = (reg !== "rip" && reg !== "eflags");
                const $tr = $(`<tr>
<td>${reg}</td>
<td>
    <span class="${editable ? 'edit-register' : ''}">${val}</span>
</td>
</tr>`);
                $tr.find(".edit-register").on("click", () => {
                    const newVal = prompt(`Update value of register %${reg}`, val);
                    sendMessage({
                        "type": "update_register",
                        "reg": reg,
                        "value": newVal
                    });
                });
                $registerTable.append($tr);
            }
        } else if (msg.type === "output") {
            $output.val($output.val() + msg.data);
        }
    });

    $("#hex-view").on("click", () => {
        const $form = $("#hidden_form");
        $form.trigger("reset");
        $form.attr("method", "POST");
        $form.attr("action", `/hexview/${codeId}`);
        $form.attr("target", "_blank");

        const $input = $("#hidden_textarea");
        $input.attr("type", "text");
        $input.attr("name", "hexview");
        $input.val(doc.getValue());

        $form.submit();
    });

    initEditor();
    setState(State.stopped);
})();
