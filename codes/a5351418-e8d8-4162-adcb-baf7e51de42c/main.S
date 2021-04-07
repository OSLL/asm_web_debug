.set MAGIC, 0x1badb002
.set FLAGS, (1<<0 | 1<<1)
.set CHECKSUM, -(MAGIC + FLAGS)

.section .multiboot
    .long MAGIC
    .long FLAGS
    .long CHECKSUM

.section .text

.global _start

_start:
	mov $kernel_stack, %esp
    
	pushl %ebp
	movl %esp, %ebp

	pushl $11
	call Fib
	addl $4, %esp

	popl %ebp
	cli
    hlt


Fib:
	.set var_c, -12
	.set var_b, -8
	.set var_a, -4

	.set arg_num, +4


	movl $1, var_a(%esp) 
	movl $1, var_b(%esp) 

	_Fib_lp:
		movl arg_num(%esp), %ecx
		cmpl $0, %ecx 
		jz _Fib_exit

		decl arg_num(%esp)

		movl var_b(%esp), %eax
		movl %eax, var_c(%esp)

		movl var_a(%esp), %eax
		addl %eax, var_b(%esp)

		movl var_c(%esp), %eax
		movl %eax, var_a(%esp)

		jmp _Fib_lp

	_Fib_exit:

	movl var_a(%esp), %eax

ret

.section .bss
.space 2*1024*1024 

kernel_stack: