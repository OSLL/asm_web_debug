.global _start

_start:
                      
        mov   r0, #3         
        mov   r1, #2         
        add   r2, r1, r0      
        mov   r7, #70
stop:   b stop 