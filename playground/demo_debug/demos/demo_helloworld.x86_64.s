# Description:
# Program for demonstrating debugging of programs run in QEMU user-space emulation.
# Platform:
# x86_64

.data

greetings_str:		.ascii "Hello, emulated world in x86_64!\n"
greetings_str_end:	greetings_str_ln = (greetings_str_end - greetings_str)

.text
.global _start

_start:

	mov	$1,			%rax		# syswrite() call
	mov	$1,			%rdi		# stdout file
	mov	$greetings_str,		%rsi		# data to write out
	mov	$greetings_str_ln,	%rdx		# length ot the data
	syscall

	.exit:
	mov	$60,			%rax		# exit() call
	xor	%rdi,			%rdi		# exit code 0
	syscall

