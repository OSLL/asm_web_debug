#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from selenium import webdriver

from basic_test import BasicTest

class OpenPagesTest(BasicTest):

    def test_open_slash(self):
        self.driver.get(self.getUrl('/'))
        assert "Welcome to ASM Web IDE" in self.driver.title, "No 'Welcome to ASM Web IDE' in title"

    def test_open_code(self):
        self.open_code_page()
        code_id = self.get_code_id_from_current_url()
        assert code_id == self.CODE_ID, 'New code_id != test.CODE_ID'
        assert "Web ASM" in self.driver.title, "No 'Web ASM' in title"

    def test_open_empty_hexview(self):
        text = ""
        hextext = ["3C 4E 6F 20 63 6F 64 65 20 66 6F 72 20 68 65 78", "76 69 65 77 21 3E"]
        self.set_code_and_open_hexview(text, hextext)

    def test_open_hexview(self):
        text = "Test"
        hextext = ["54 65 73 74"]
        self.set_code_and_open_hexview(text, hextext)

    def test_open_unexistent_hexview_by_get(self):
        unexistent_id = 'non_exist_id'
        self.driver.get(self.getUrl(f"/hexview/{unexistent_id}"))
        assert 'No such code_id' in self.driver.page_source, "No 'No such code_id' for unexistent code_id"

    def set_code_and_open_hexview(self, text, hextext_list):
        self.open_code_page()
        
        # send empty string to textarea
        self.set_code(text)

        # go to hexview
        hexview_button = self.driver.find_element_by_id('HexView')
        hexview_button.click()

        # set active tab to hexview
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # check code_id in hex
        code_id = self.get_code_id_from_current_url()
        assert code_id == self.CODE_ID, 'Hexview code_id != test.CODE_ID'
        
        assert all([text in self.driver.page_source for text in hextext_list]), f"No '{hextext_list}' in hexview"

        # set active tab to first tab
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        