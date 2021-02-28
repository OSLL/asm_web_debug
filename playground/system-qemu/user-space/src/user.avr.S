.text
.global _start

_start:
   ldi	r20, 1
   ldi  r21, 1
   ldi  r22, 0

   _lp:
      mov r22, r21
      add r21, r20
      mov r20, r22
   jmp _lp
