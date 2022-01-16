#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from basic_test import BasicTest

X86_CODE = """
.data
greetings_str:		.ascii "Hello, emulated world in x86_64!\\n"
greetings_str_end:	greetings_str_ln = (greetings_str_end - greetings_str)
fname_str:		.ascii "./test"
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
	syscall
	.exit:
	mov	$60,			%rax		# exit() call
	xor	%rdi,			%rdi		# exit code 0
	syscall
"""

ARM_CODE = """
.data
greetings_str:		.ascii "Hello, emulated world in ARM!\\n"
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
"""

AVR_CODE = """
.text
.global _start
_start:
	ldi	r17,	'A'
	ldi	r18,	'V'
	ldi	r19,	'R'
"""

WRONG_CODE = "it's not a code!"

class CompileCodeTest(BasicTest):

    ARCH_CODES = [X86_CODE, ARM_CODE, AVR_CODE]
    SUCCESS_MSG = "Компиляция прошла успешно"
    FAILURE_MSG = "Компиляция провалилась. Проверьте логи компиляции." 

    def test_success_compile(self):
        self.open_code_page()
        for code, arch in zip(self.ARCH_CODES, self.ARCHS):
            self.compile_code(code, arch, True)

    def test_wrong_compile(self):
        self.open_code_page()
        for arch in self.ARCHS:
            self.compile_code(WRONG_CODE, arch, False)

    def compile_code(self, code, arch, succcess=True):
        msg = self.SUCCESS_MSG if succcess else self.FAILURE_MSG
        
        # choose arch
        select = Select(self.driver.find_element_by_id('arch_select'))
        select.select_by_value(arch)

        # send code to textarea
        self.set_code(code)
        
        # find compile button and click
        compile_button = self.driver.find_element_by_id('Compile')
        compile_button.click()
        
        # wait alert
        try:
            WebDriverWait(self.driver, 3).until(
                EC.text_to_be_present_in_element(
                    (By.ID, 'ajax-alert'),
                    msg)
            ) 
        except:
            assert False, f'No message "{msg}". Arch {arch}'