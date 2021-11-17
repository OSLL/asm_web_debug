.global _start_seccomp

_start_seccomp:
    mov $157, %rax      # SYS_prctl
    mov $22, %rdi       # PR_SET_SECCOMP
    mov $1, %rsi        # SECCOMP_MODE_STRICT
    syscall

    xor %rax, %rax
    xor %rdi, %rdi
    xor %rsi, %rsi
    jmp _start
