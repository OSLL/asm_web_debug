.set MAGIC, 0x1badb002              # подсказка для grub, что он нашел multikernel
.set FLAGS, (1<<0 | 1<<1)
.set CHECKSUM, -(MAGIC + FLAGS)

.section .multiboot
    .long MAGIC
    .long FLAGS
    .long CHECKSUM


.section .text
.extern EntryPoint

.global loader
loader:
    mov $kernel_stack, %esp            # инициализация стека
   
    call EntryPoint                    # переход на пользовательский код
    
STOP_CPU:
    cli
    hlt
    jmp STOP_CPU
        
    
.section .bss
.space 2*1024*1024 

kernel_stack: