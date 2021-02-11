; Description:
; Program for demonstrating debugging of programs run in QEMU user-space emulation.
; Platform:
; avr

.text
.global _start

_start:

	; Since there is no way to do a linux kernel call from AVR,
	; there are some placeholder register operations
	ldi	r17,	'A'
	ldi	r18,	'V'
	ldi	r19,	'R'
