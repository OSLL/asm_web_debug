

.data

str_fibnum:
	.string "Fib num is "
str_fibnum_length:
    .quad str_fibnum_length - str_fibnum


.text
.type _start, @function
.global _start
_start:

    movq $1, %rax 					
    movq $1, %rdi					
    movq $str_fibnum, %rsi			
    movq (str_fibnum_length), %rdx	
    syscall							
    
    push $7							// Fib(7);
    call _Fib
    add $8, %rsp  					// clear stack
    
    
    movq $60, %rax					// exit(
    movq $0, %rdi					//   EXIT_SUCCESS
    syscall							// );
    
/*
*	Result: %rax
*	Args: %rcx - number of fibonachi
*/
_Fib:
	// local var's
	.set var_c, -24
	.set var_b, -16
	.set var_a, -8

	.set arg_num, +8


	movq $1, var_a(%rsp) 
	movq $1, var_b(%rsp) 

	_Fib_lp:
		movq arg_num(%rsp), %rcx
		cmpq $0, %rcx 
		jz _Fib_exit

		decl arg_num(%rsp)

		movq var_b(%rsp), %rax
		movq %rax, var_c(%rsp)

		movq var_a(%rsp), %rax
		addq %rax, var_b(%rsp)

		movq var_c(%rsp), %rax
		movq %rax, var_a(%rsp)

		jmp _Fib_lp

	_Fib_exit:

	movq var_a(%rsp), %rax
    ret



