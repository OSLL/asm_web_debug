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
