# 64-bit

##### Пример запусака патчера:
``python3 qemu-x86_64-patch.py <путь к исполняемому файлу qemu>``

#### разрешенные системные вызовы:

|number| 	abi| 	name| 	entry point |
|------|-------|--------|---------------|
|0 	   |common |read    |    sys_read   |
|1 	   |common |write   |	sys_write   |
|60    |common |exit 	|sys_exit       |



/---------------------------------Example #1:------------------------------------------------------------------------
```
.data

hello_str:
	.string "Hello x86_64!\n"
hello_str_length:
    .quad hello_str_length - hello_str

.text

.type _start, @function
.global _start
_start:

    movq $1, %rax 					// write(
    movq $1, %rdi					//   STDOUT_HANDLE,
    movq $hello_str, %rsi			//   "Hello x86_64!\n",
    movq (hello_str_length), %rdx	//   sizeof("Hello, world!\n")
    syscall							// );
    
    movq $60, %rax					// exit(
    movq $0, %rdi					//   EXIT_SUCCESS(0)
    syscall							// );
```
\-----------------------------------------------------------------------------------------------------------------------

/---------------------------------Example #2:------------------------------------------------------------------------
```
.data

file_name:
	.string "file.txt"
file_name_length:
    .quad file_name_length - file_name - 1

.text

.type _start, @function
.global _start
_start:
    movq $2, %rax 					// open(
    movq $file_name, %rdi			//  file_name,
    movq $0101, %rsi				//  O_CREAT | O_WRONLY
    movq $0700, %rdx				//  S_IWUSR
    syscall							// );
    
    movq $60, %rax					// exit(
    movq $0, %rdi					//   EXIT_SUCCESS
    syscall							// );
```
\-----------------------------------------------------------------------------------------------------------------------

/---------------------------------Example #3:------------------------------------------------------------------------
```
.data

str_fibnum:
	.string "Fib num is "
str_fibnum_length:
    .quad str_fibnum_length - str_fibnum - 1

str_hex_num:
	.string "0123456789ABCDEF"
str_hex_num_length:
	.quad str_hex_num_length - str_hex_num

.text
.type _start, @function
.global _start
_start:

    movq $1, %rax 					
    movq $1, %rdi					
    movq $str_fibnum, %rsi			
    movq (str_fibnum_length), %rdx	
    syscall							
    
    push $20							// Fib(20);
    call _Fib
    add $8, %rsp  					// clear stack
    
    push %rax						// _print_byte(rax);
    call _print_dword
    add $8, %rsp  					// clear stack
    
    movq $60, %rax					// exit(
    movq $0, %rdi					//   EXIT_SUCCESS
    syscall							// );
    
/*
*	Result: %rax
*	Args: on stack - number of fibonachi
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


/*
*	Args: on stack - value
*/
_print_byte:
    movq 8(%rsp), %rax
    shr $4, %rax
    andq $0xF, %rax
    addq $str_hex_num, %rax	
    movq %rax, %rsi	
    movq $1, %rax 					
    movq $1, %rdi							
    movq $1, %rdx	
    syscall		
    
    movq 8(%rsp), %rax
    andq $0xF, %rax
    addq $str_hex_num, %rax	
    movq %rax, %rsi	
    movq $1, %rax 					
    movq $1, %rdi							
    movq $1, %rdx	
    syscall	
    
	ret

/*
*	Args: on stack - value
*/
_print_dword:
	movq 8(%rsp), %rax
    shr $0x18, %rax
    push %rax						
    call _print_byte
    add $8, %rsp  
    
    movq 8(%rsp), %rax
    shr $0x10, %rax
    push %rax						
    call _print_byte
    add $8, %rsp  
    
    movq 8(%rsp), %rax
    shr $0x8, %rax
    push %rax						
    call _print_byte
    add $8, %rsp 
    
    movq 8(%rsp), %rax
    push %rax						
    call _print_byte
    add $8, %rsp  
    
	ret

```
\-----------------------------------------------------------------------------------------------------------------------
