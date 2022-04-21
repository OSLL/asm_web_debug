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
        over: {
            id: "over",
            buttons: [
                { name: "Stop", id: "kill", style: "danger" }
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

    const $debugButtons = $("#debug-buttons");
    const $output = $("#build_log");
    const $registerTable = $("#register_body");
    const $watchTable = $("#watch_body");
    const $submitButton = $("#submit_button");
    const $sampleTest = $("#sample_test");

    const ws = new WebSocket(`${(window.location.protocol === "https") ? "wss" : "ws"}://${window.location.host}/assignment/${assignmentId}/websocket`);

    let state = State.stopped;
    let activeLine = 0;

    let codeMirror = null;
    let doc = null;
    let watchedExprs = [];

    $(document).bind('keydown', async function(e) {
        // capture Ctrl+S for data saving
        if (e.ctrlKey && e.which === 83) {
            e.preventDefault();
            await saveCode();
            showAlert("Source code was saved", "success");
        }
    });

    function showAlert(content, kind) {
        const $alert = $("#ajax-alert");
        $alert.text(content);
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

    function onDebugButtonClick(id) {
        if (id === "run") {
            setState(State.over);
            $output.val("");
            sendMessage({
                "type": "run",
                "source": doc.getValue(),
                "input": "",
                "breakpoints": getBreakpoints(),
                "watch": watchedExprs,
                "sample_test": $sampleTest ? $sampleTest.val() : null
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
        for (const button of state.buttons) {
            const $button = $(`<button class="btn btn-outline-${button.style || 'info'}">${button.name}</button>`);
            $button.on("click", () => {
                onDebugButtonClick(button.id);
            });
            $button.appendTo($debugButtons);
        }

        doc.eachLine(lineHandle => {
            doc.removeLineClass(lineHandle, "background", "active-line");
        });

        if (state === State.paused) {
            doc.addLineClass(activeLine - 1, "background", "active-line");
        } else {
            $registerTable.html("");
            $watchTable.html("");
        }
    }

    async function saveCode() {
        const data = new FormData();
        data.append("code", doc.getValue());
        data.append("arch", $("#arch_select").val());

        await fetch(`/assignment/${assignmentId}/save`, {
            method: "POST",
            body: data
        });
    }

    $submitButton.on("click", async function submitCode() {
        $submitButton.prop("disabled", true);
        await saveCode();

        const result = await fetch(`/assignment/${assignmentId}/submit`, {
            method: "POST"
        });
        const data = await result.json();

        showAlert(data.comment, data.is_correct ? "success" : "danger");

        $submitButton.prop("disabled", false);
    });

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
            if (activeLine === -1) {
                setState(State.over)
            } else {
                setState(State.paused);
            }
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
            for (const [reg, signed, unsigned, hex] of msg.data) {
                const $tr = (reg !== "eflags") ? $(`<tr>
<td>${reg}</td>
<td><span class="edit-register">${signed}</span></td>
<td><span class="edit-register">${unsigned}</span></td>
<td><span class="edit-register">${hex}</span></td>
</tr>`) : $(`<tr>
<td>flags</td>
<td colspan="3">${signed}</td>
</tr>`);
                $tr.find(".edit-register").on("click", (e) => {
                    const newVal = prompt(`Update value of register %${reg}`, e.target.innerText);
                    if (newVal) {
                        sendMessage({
                            "type": "update_register",
                            "reg": reg,
                            "value": newVal
                        });
                    }
                });
                $registerTable.append($tr);
            }
        } else if (msg.type === "watch") {
            $watchTable.html("");
            for (const [expr, val] of msg.data) {
                const $tr = $(`<tr>
<td><span class="remove">&times;</span> ${expr}</td>
<td>${val}</td>
</tr>
`);
                $tr.find(".remove").on("click", () => {
                    sendMessage({
                        "type": "remove_watch",
                        "expr": expr
                    })
                })
                $watchTable.append($tr);
            }

            const $add = $(`<tr>
<td><input id="add_watch_expr" /></td>
<td><button id="add_watch_button">add</button></td>
</tr>
`);
            $add.find("#add_watch_button").on("click", () => {
                sendMessage({
                    "type": "add_watch",
                    "expr": $("#add_watch_expr").val()
                });
            });
            $watchTable.append($add);
        } else if (msg.type === "output") {
            $output.val($output.val() + msg.data);
        } else if (msg.type === "error") {
            showAlert(msg.message, "danger");
            setState(State.stopped);
        }
    });

    $("#hex-view").on("click", () => {
        const $form = $("#hidden_form");
        $form.trigger("reset");
        $form.attr("method", "POST");
        $form.attr("action", `/hexview/${assignmentId}`);
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
