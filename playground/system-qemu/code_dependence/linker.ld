ENTRY(_start)

OUTPUT_FORMAT(elf32-i386)
OUTPUT_ARCH(i386:i386)

SECTIONS
{
    . = 0x0100000;
    
    .text :
    {
        *(.multiboot)
        *(.text*)
        *(.rodata)
    }
    
    .data :
    {
        *(.data)
    }
    
    .bss :
    {
        *(.bss)
    }

    .debug_line :
    {
        *(.debug_line)
    }
    
    .debug_info :
    {
        *(.debug_info)
    }

    .debug_abbrev :
    {
        *(.debug_abbrev)
    }


    .debug_aranges :
    {
        *(.debug_aranges)
    }


    .debug_str :
    {
        *(.debug_str)
    }


}