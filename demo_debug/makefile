LD_X86_64 = x86_64-linux-gnu-ld -o
AS_X86_64 = x86_64-linux-gnu-as -g
LD_ARM_EABI = arm-linux-gnueabi-ld -o
AS_ARM_EABI = arm-linux-gnueabi-as -g
LD_AVR = avr-ld -m avr6 -o
AS_AVR = avr-as -g -mmcu=avr6


# Empty target to just make all demos
demos: demos_helloworld
demos_helloworld: ./demos/demo_helloworld.x86_64.out ./demos/demo_helloworld.arm.out ./demos/demo_helloworld.avr.out


./demos/demo_helloworld.x86_64.out: ./demos/demo_helloworld.x86_64.o
	$(LD_X86_64) ./demos/demo_helloworld.x86_64.out ./demos/demo_helloworld.x86_64.o
./demos/demo_helloworld.x86_64.o: ./demos/demo_helloworld.x86_64.s
	$(AS_X86_64) ./demos/demo_helloworld.x86_64.s -o ./demos/demo_helloworld.x86_64.o

./demos/demo_helloworld.arm.out: ./demos/demo_helloworld.arm.o
	$(LD_ARM_EABI) ./demos/demo_helloworld.arm.out ./demos/demo_helloworld.arm.o
./demos/demo_helloworld.arm.o: ./demos/demo_helloworld.arm.s
	$(AS_ARM_EABI) ./demos/demo_helloworld.arm.s -o ./demos/demo_helloworld.arm.o

./demos/demo_helloworld.avr.out: ./demos/demo_helloworld.avr.o
	$(LD_AVR) ./demos/demo_helloworld.avr.out ./demos/demo_helloworld.avr.o
./demos/demo_helloworld.avr.o: ./demos/demo_helloworld.avr.s
	$(AS_AVR) ./demos/demo_helloworld.avr.s -o ./demos/demo_helloworld.avr.o

clean:
	rm ./demos/demo*.o
	rm ./demos/demo*.out
