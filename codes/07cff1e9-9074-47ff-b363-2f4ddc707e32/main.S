.data

hello_str:
	.string "Hello12131 x86_64!\n"
hello_str_length:
    .quad hello_str_length - hello_str

.text

.type _start, @function
.global _start
_start:

    movq $1, %rax 					// write(
    movq $1, %rdi					//   STDOUT_FILENO,
    movq $hello_str, %rsi			//   "Hello x86_64!\n",
    movq (hello_str_length), %rdx	//   sizeof("Hello, world!\n")
    syscall							// );
    
    movq $60, %rax					// exit(
    movq $0, %rdi					//   EXIT_SUCCESS
    syscall							// );



