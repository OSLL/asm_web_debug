$(function() {
    let hash_saved_code = "";
    let code_id = get_code_id();

    test_table_create(); // test table creation for registers an stacks
    setup_button_handle(); // setup button handling
    capture_hotkey(); // setup capturing browser hotkyes

    function test_table_create() {
        let reg = document.querySelector('#register_body');
        let registers = [
            ['A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6', 'A1', 'B2', 'C3', 'A6'],
            ['0xff3', '0x546', '0xaaa', '0x123', '0xff3', '0x546', '0xaaa', '0x123', '0x546', '0xaaa', '0x123', '0xff3']
        ];
        createTableReg(reg, registers);

        let stack = document.querySelector('#stack_body');
        let s_elements = [
            ['0xff', '0xaaf', '0x030', '0xccc'],
            ['exmpl', 'exmpl', 'exmpl', 'exmpl']
        ];
        createTableStack(stack, s_elements);
    }

    function createTableReg(parent, arr) {
        let i = 0;
        while (i < arr[0].length) {
            let tr = document.createElement('tr');
            for (let j = 0; j < 4; j++) {
                let td = document.createElement('div');
                if (j % 2) {
                    let input = document.createElement('input');
                    input.value = arr[j % 2][i];
                    input.name = arr[0][i];
                    input.classList.add('register-input')
                    td.appendChild(input);
                    i++;
                } else td.appendChild(document.createTextNode(arr[j % 2][i]));
                tr.appendChild(td);
            }
            parent.appendChild(tr);
        }
    }

    function createTableStack(parent, arr) {
        let alen = arr[0].length;

        for (let i = 0; i < alen; i++) {
            let tr = document.createElement('tr');
            for (let j = 0; j < 2; j++) {
                let td = document.createElement('div');
                let text = document.createTextNode(arr[j][i]);
                td.appendChild(text);
                tr.appendChild(td);
            }
            parent.appendChild(tr);
        }
    }

    function capture_hotkey() {
        $(document).bind('keydown', function(e) {
            // capture Ctrl+S for data saving
            if (e.ctrlKey && (e.which === 83)) {
                e.preventDefault();
                let [is_equal, hash] = check_hash_code(hash_saved_code)
                if (is_equal) {
                    warning_alert('Вы уже сохраняли этот код!')
                    return
                } else
                    hash_saved_code = hash

                let [code, breakpoints] = get_code_and_breakpoints()

                $.ajax({
                    url: '/save/' + code_id,
                    type: 'POST',
                    dataType: 'json',
                    contenType: 'application/json',
                    data: {
                        'code': code,
                        'breakpoints': JSON.stringify(breakpoints),
                        'arch': $("#arch_select").val()
                    },
                    success: function(resp) {
                        if (resp['success_save'])
                            success_alert('Код сохранён!');
                        else
                            failure_alert('Код не был сохранён из-за ошибки на сервере.')
                    },
                    error: function(resp) {
                        failure_alert('Код не был отправлен на сохранение. Попробуйте снова')
                    },
                });

            }
        });
    }

    function get_code_and_breakpoints() {
        let editor = $('.CodeMirror')[0].CodeMirror;
        let breakpoints = [];
        let lines = editor.lineCount();

        for (let i = 0; i < lines; i++) {
            let info = editor.lineInfo(i);
            if (info.gutterMarkers)
                breakpoints.push(i + 1);
        }

        return [editor.getValue(), breakpoints]
    }

    function setup_button_handle() {
        // compile button
        $("#Compile").click(function(e) {
            let [code, breakpoints] = get_code_and_breakpoints()
            success_alert("<span class='spinner-border spinner-border-sm'></span> Компиляция...", 30000)

            $.ajax({
                url: '/compile/' + code_id,
                type: 'POST',
                dataType: 'json',
                contenType: 'application/json',
                data: {
                    'code': code,
                    'breakpoints': JSON.stringify(breakpoints),
                    'arch': $("#arch_select").val()
                },
                success: function(resp) {
                    let editor = $('.CodeMirror')[1].CodeMirror;
                    editor.getDoc().setValue(resp['build_logs']);
                    console.log(resp)
                    if (resp['success_build'])
                        success_alert(`Компиляция прошла успешно. ${Date(resp['timestamp'])}`)
                    else
                        failure_alert(`Компиляция провалилась. Проверьте логи компиляции. ${Date(resp['timestamp'])}`, 5000)
                },
                error: function(resp) {
                    failure_alert(`Код не был отправлен. Попробуйте снова. ${Date()}`)
                },
            });
            e.preventDefault();
        });

        // run-button
        $('#Run').click(function(e) {
            let [code, breakpoints] = get_code_and_breakpoints()
            success_alert(`<span class='spinner-border spinner-border-sm'></span> Запуск... ${Date()}`, delay = 0)

            $.ajax({
                url: '/run/' + code_id,
                type: 'POST',
                dataType: 'json',
                contenType: 'application/json',
                data: {
                    'code': code,
                    'breakpoints': JSON.stringify(breakpoints),
                    'arch': $("#arch_select").val()
                },
                success: function(resp) {
                    let editor = $('.CodeMirror')[1].CodeMirror;
                    editor.getDoc().setValue(resp['run_logs']);
                    console.log(resp)
                    let msg = ''
                    if (resp['success_run']) {
                        success_alert(`Программа выполнена. ${Date(resp['timestamp'])}`)
                    } else {
                        failure_alert(`Запуск программы провалился. Проверьте логи. ${Date(resp['timestamp'])}`, 5000)
                    }
                },
                error: function(resp) {
                    failure_alert(`Программа не была запущена. Попробуйте снова. ${Date()}`, 5000)
                },
            });
            e.preventDefault();
        });

        // debug-button
        setup_debug_button_handle()

        // hexview button
        $("#HexView").click(function(e) {
            let editor = $('.CodeMirror')[0].CodeMirror;
            let code = editor.getValue();

            // submit form with openning new tab
            let form = $('#hidden_form')
            form.trigger("reset")
            form.attr('method', "POST");
            form.attr('action', "/hexview/" + code_id)
            form.attr('target', "_blank")

            let input = $("#hidden_textarea")
            input.attr('type', "text")
            input.attr('name', "hexview")
            input.val(code)

            input.appendTo(form)
            form.appendTo($('body'))

            form.submit()

        });
    }

    function setup_debug_button_handle() {
        $("#Debug").click(function(e) {
            send_debug_command(e.target)
        });
        $("#Continue").click(function(e) {
            send_debug_command(e.target)
        });
        $("#Step_into").click(function(e) {
            send_debug_command(e.target)
        });
        $("#Step_over").click(function(e) {
            send_debug_command(e.target)
        });
        $("#Step_out").click(function(e) {
            send_debug_command(e.target)
        });
    }


    function send_debug_command(button) {
        $.ajax({
            url: '/debug/' + code_id,
            type: 'POST',
            contenType: 'application/json',
            data: {
                'debug_command': button.getAttribute('debug_code')
            },
            success: function(response) {
                console.log(response);
            },
            error: function(response) {
                console.log(response);
            },
        });
    }


    function calc_hash_code() {
        return $.MD5(JSON.stringify(get_code_and_breakpoints()))
    }

    function check_hash_code(hash) {
        let new_hash = calc_hash_code()
        if (hash != new_hash)
            return [false, new_hash]
        else
            return [true, new_hash]
    }

    function success_alert(text, delay = 2000) {
        $("#ajax-alert").removeClass();
        $("#ajax-alert").addClass('alert alert-success');
        _show_alert(text, delay);
    }

    function failure_alert(text, delay = 2000) {
        $("#ajax-alert").removeClass();
        $("#ajax-alert").addClass('alert alert-danger');
        _show_alert(text, delay)
    }

    function warning_alert(text, delay = 2000) {
        $("#ajax-alert").removeClass();
        $("#ajax-alert").addClass('alert alert-warning');
        _show_alert(text, delay)
    }

    function _show_alert(text, delay = 2000) {
        $("#ajax-alert").html(text);
        $("#ajax-alert").show();
        $("#ajax-alert").delay(delay).fadeOut();
    }

    function get_code_id() {
        return location.pathname.slice(1).split('/')[0]
    }
});
