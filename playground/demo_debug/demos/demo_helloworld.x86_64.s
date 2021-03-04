# Description:
# Program for demonstrating debugging of programs run in QEMU user-space emulation.
# Platform:
# x86_64

.data

greetings_str:		.ascii "Hello, emulated world in x86_64!\n"
greetings_str_end:	greetings_str_ln = (greetings_str_end - greetings_str)

fname_str:		.ascii "./test\0"

.text
.global _start

_start:

	mov	$2,			%rax		# open() call
	mov	$fname_str,		%rdi		# path to the file
	mov	$0101,			%rsi		# flags: O_CREAT, O_WRONLY
	mov	$0700,			%rdx		# mode: S_IWUSR
	syscall

	mov	%rax,			%rdi		# file to write to
	mov	$1,			%rax		# write() call
	mov	$greetings_str,		%rsi		# data to write out
	mov	$greetings_str_ln,	%rdx		# length ot the data
	syscall

	mov	$3,			%rax		# close() call
	# %rdi already contains file descriptor
	syscall

	.exit:
	mov	$60,			%rax		# exit() call
	xor	%rdi,			%rdi		# exit code 0
	syscall

