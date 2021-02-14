.global EntryPoint

EntryPoint:
	
	movl $0, %eax

	LP:
	incl %eax
	jmp LP

ret
