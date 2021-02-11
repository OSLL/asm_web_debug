# Description:
# Program for demonstrating debugging of programs run in QEMU user-space emulation.
# Platform:
# arm

.data

greetings_str:		.ascii "Hello, emulated world in ARM!\n"
greetings_str_end:	greetings_str_ln = (greetings_str_end - greetings_str)

.text
.global _start

_start:

	mov	r7,	#4
	mov	r0,	#1
	ldr	r1,	=greetings_str
	ldr	r2,	=greetings_str_ln
	svc	#0

	mov 	r7,	#1
	mov	r1,	#10
	svc 	#0
