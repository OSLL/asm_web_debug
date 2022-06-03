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

class CheckRegistersTest(BasicTest):
	line_number = "19"
	checked_reg = {"rax": "1", "rdi": "-30"}

	def test_registers(self):
		self.open_code_page()

        # send code to textarea
		self.set_code(X86_CODE)

		try:
			line = WebDriverWait(self.driver, 3).until(
				lambda d: d.find_element_by_xpath("//*[contains(text(), '" + self.line_number + "')]")
				)
			line.click() 
		except:
			assert False, f'Wrong line'

		compile_button = self.driver.find_element_by_id('Compile')
		compile_button.click()
		self.compare_registers(self.checked_reg)

	def compare_registers(self, checked_reg):
		for reg in checked_reg.keys():
			try:
				el = WebDriverWait(self.driver, 5).until(
					lambda d: d.find_element_by_id(reg + "-value")
					)
				if el.text != checked_reg[reg]:
					assert False, f'Wrong register {reg}. Expected value {checked_reg[reg]}, got {el.text}'
			except:
				assert False, f'Wrong register'