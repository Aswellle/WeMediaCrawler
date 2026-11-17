# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/douyin/login.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


import asyncio
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from cache.cache_factory import CacheFactory
from tools import utils


class DouYinLogin(AbstractLogin):

    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext, # type: ignore
                 context_page: Page, # type: ignore
                 login_phone: Optional[str] = "",
                 cookie_str: Optional[str] = ""
                 ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.scan_qrcode_time = 60
        self.cookie_str = cookie_str

    async def begin(self):
        """
            Start login douyin website
            The verification accuracy of the slider verification is not very good... If there are no special requirements, it is recommended not to use Douyin login, or use cookie login
        """

        # popup login dialog
        await self.popup_login_dialog()

        # select login type
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[DouYinLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

        # If the page redirects to the slider verification page, need to slide again
        await asyncio.sleep(6)
        current_page_title = await self.context_page.title()
        if "验证码中间页" in current_page_title:
            await self.check_page_display_slider(move_step=3, slider_level="hard")

        # check login state
        utils.logger.info(f"[DouYinLogin.begin] login finished then check login state ...")
        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info("[DouYinLogin.begin] login failed please confirm ...")
            sys.exit()

        # wait for redirect
        wait_redirect_seconds = 5
        utils.logger.info(f"[DouYinLogin.begin] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self):
        """Check if the current login status is successful and return True otherwise return False"""
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)

        for page in self.browser_context.pages:
            try:
                local_storage = await page.evaluate("() => window.localStorage")
                if local_storage.get("HasUserLogin", "") == "1":
                    return True
            except Exception as e:
                # utils.logger.warn(f"[DouYinLogin] check_login_state waring: {e}")
                await asyncio.sleep(0.1)

        if cookie_dict.get("LOGIN_STATUS") == "1":
            return True

        return False

    # 登录面板候选选择器：抖音多次更换面板 DOM ID
    # （旧版 login-panel-new，现版 login-full-panel-*），任一命中即认为已弹出
    _LOGIN_PANEL_SELECTORS = (
        "xpath=//div[@id='login-panel-new']",
        "xpath=//div[starts-with(@id, 'login-full-panel')]",
        "xpath=//div[contains(@class, 'login-panel') or contains(@class, 'login-full-panel')]",
    )
    # 兜底"登录"入口候选：新版面板遮挡旧按钮，点击需绕过遮挡检测
    _LOGIN_BUTTON_SELECTORS = (
        "xpath=//p[text() = '登录']",
        "xpath=//button[.//text() = '登录' or contains(., '登录')]",
        "xpath=//*[contains(@class, 'login-btn') or @data-e2e='login-icon']",
    )

    async def popup_login_dialog(self):
        """If the login dialog box does not pop up automatically, we will manually click the login button"""
        # 任一面板候选可见即认为已自动弹出
        for dialog_selector in self._LOGIN_PANEL_SELECTORS:
            try:
                await self.context_page.wait_for_selector(dialog_selector, timeout=1000 * 10 // len(self._LOGIN_PANEL_SELECTORS))
                utils.logger.info(f"[DouYinLogin.popup_login_dialog] login panel detected: {dialog_selector}")
                return
            except Exception:
                continue

        utils.logger.error("[DouYinLogin.popup_login_dialog] login dialog box does not pop up automatically")
        utils.logger.info("[DouYinLogin.popup_login_dialog] login dialog box does not pop up automatically, we will manually click the login button")
        for button_selector in self._LOGIN_BUTTON_SELECTORS:
            try:
                login_button_ele = self.context_page.locator(button_selector)
                # force=True：旧入口可能被新版面板的透明遮罩拦截指针事件，
                # 但点击本身只是唤起面板，强制点击即可达成目的
                await login_button_ele.click(timeout=10_000, force=True)
                await asyncio.sleep(0.5)
                return
            except Exception as e:
                utils.logger.info(
                    f"[DouYinLogin.popup_login_dialog] login button candidate failed "
                    f"({button_selector}): {e}, trying next ..."
                )
        raise RuntimeError(
            "[DouYinLogin.popup_login_dialog] 未能唤起抖音登录面板：所有面板检测与登录入口候选均失败。"
            "可能是抖音页面改版或出现风控验证码，请人工打开抖音确认页面状态后重试。"
        )

    async def login_by_qrcode(self):
        utils.logger.info("[DouYinLogin.login_by_qrcode] Begin login douyin by qrcode...")
        # 二维码图片候选：新版登录面板的 DOM 与旧版不同，逐个候选探测
        qrcode_img_selectors = (
            "xpath=//div[@id='animate_qrcode_container']//img",
            "xpath=//div[starts-with(@id, 'login-full-panel')]//img",
            "xpath=//div[contains(@class, 'qrcode') or contains(@class, 'QrCode')]//img",
            "xpath=//img[contains(@src, 'qrcode') or contains(@src, 'data:image')]",
        )
        base64_qrcode_img = ""
        for selector in qrcode_img_selectors:
            base64_qrcode_img = await utils.find_login_qrcode(
                self.context_page,
                selector=selector
            )
            if base64_qrcode_img:
                utils.logger.info(f"[DouYinLogin.login_by_qrcode] qrcode found via {selector}")
                break
        if not base64_qrcode_img:
            utils.logger.info("[DouYinLogin.login_by_qrcode] login qrcode not found please confirm ...")
            sys.exit()

        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)
        await asyncio.sleep(2)

    async def login_by_mobile(self):
        utils.logger.info("[DouYinLogin.login_by_mobile] Begin login douyin by mobile ...")
        mobile_tap_ele = self.context_page.locator("xpath=//li[text() = '验证码登录']")
        await mobile_tap_ele.click()
        await self.context_page.wait_for_selector("xpath=//article[@class='web-login-mobile-code']")
        mobile_input_ele = self.context_page.locator("xpath=//input[@placeholder='手机号']")
        await mobile_input_ele.fill(self.login_phone)
        await asyncio.sleep(0.5)
        send_sms_code_btn = self.context_page.locator("xpath=//span[text() = '获取验证码']")
        await send_sms_code_btn.click()

        # Check if there is slider verification
        await self.check_page_display_slider(move_step=10, slider_level="easy")
        cache_client = CacheFactory.create_cache(config.CACHE_TYPE_MEMORY)
        max_get_sms_code_time = 60 * 2  # Maximum time to get verification code is 2 minutes
        while max_get_sms_code_time > 0:
            utils.logger.info(f"[DouYinLogin.login_by_mobile] get douyin sms code from redis remaining time {max_get_sms_code_time}s ...")
            await asyncio.sleep(1)
            sms_code_key = f"dy_{self.login_phone}"
            sms_code_value = cache_client.get(sms_code_key)
            if not sms_code_value:
                max_get_sms_code_time -= 1
                continue

            sms_code_input_ele = self.context_page.locator("xpath=//input[@placeholder='请输入验证码']")
            await sms_code_input_ele.fill(value=sms_code_value.decode())
            await asyncio.sleep(0.5)
            submit_btn_ele = self.context_page.locator("xpath=//button[@class='web-login-button']")
            await submit_btn_ele.click()  # Click login
            # todo ... should also check the correctness of the verification code, it may be incorrect
            break

    async def check_page_display_slider(self, move_step: int = 10, slider_level: str = "easy"):
        """
        Check if slider verification appears on the page
        :return:
        """
        # Wait for slider verification to appear
        back_selector = "#captcha-verify-image"
        try:
            await self.context_page.wait_for_selector(selector=back_selector, state="visible", timeout=30 * 1000)
        except PlaywrightTimeoutError:  # No slider verification, return directly
            return

        gap_selector = 'xpath=//*[@id="captcha_container"]/div/div[2]/img[2]'
        max_slider_try_times = 20
        slider_verify_success = False
        while not slider_verify_success:
            if max_slider_try_times <= 0:
                utils.logger.error("[DouYinLogin.check_page_display_slider] slider verify failed ...")
                sys.exit()
            try:
                await self.move_slider(back_selector, gap_selector, move_step, slider_level)
                await asyncio.sleep(1)

                # If the slider is too slow or verification failed, it will prompt "The operation is too slow", click the refresh button here
                page_content = await self.context_page.content()
                if "操作过慢" in page_content or "提示重新操作" in page_content:
                    utils.logger.info("[DouYinLogin.check_page_display_slider] slider verify failed, retry ...")
                    await self.context_page.click(selector="//a[contains(@class, 'secsdk_captcha_refresh')]")
                    continue

                # After successful sliding, wait for the slider to disappear
                await self.context_page.wait_for_selector(selector=back_selector, state="hidden", timeout=1000)
                # If the slider disappears, it means the verification is successful, break the loop. If not, it means the verification failed, the above line will throw an exception and be caught to continue the loop
                utils.logger.info("[DouYinLogin.check_page_display_slider] slider verify success ...")
                slider_verify_success = True
            except Exception as e:
                utils.logger.error(f"[DouYinLogin.check_page_display_slider] slider verify failed, error: {e}")
                await asyncio.sleep(1)
                max_slider_try_times -= 1
                utils.logger.info(f"[DouYinLogin.check_page_display_slider] remaining slider try times: {max_slider_try_times}")
                continue

    async def move_slider(self, back_selector: str, gap_selector: str, move_step: int = 10, slider_level="easy"):
        """
        Move the slider to the right to complete the verification
        :param back_selector: Selector for the slider verification background image
        :param gap_selector:  Selector for the slider verification slider
        :param move_step: Controls the ratio of single movement speed, default is 1, meaning the distance moves in 0.1 seconds no matter how far, larger value means slower
        :param slider_level: Slider difficulty easy hard, corresponding to the slider for mobile verification code and the slider in the middle of verification code
        :return:
        """

        # get slider background image
        slider_back_elements = await self.context_page.wait_for_selector(
            selector=back_selector,
            timeout=1000 * 10,  # wait 10 seconds
        )
        slide_back = str(await slider_back_elements.get_property("src")) # type: ignore

        # get slider gap image
        gap_elements = await self.context_page.wait_for_selector(
            selector=gap_selector,
            timeout=1000 * 10,  # wait 10 seconds
        )
        gap_src = str(await gap_elements.get_property("src")) # type: ignore

        # Identify slider position
        slide_app = utils.Slide(gap=gap_src, bg=slide_back)
        distance = slide_app.discern()

        # Get movement trajectory
        tracks = utils.get_tracks(distance, slider_level)
        new_1 = tracks[-1] - (sum(tracks) - distance)
        tracks.pop()
        tracks.append(new_1)

        # Drag slider to specified position according to trajectory
        element = await self.context_page.query_selector(gap_selector)
        bounding_box = await element.bounding_box() # type: ignore

        await self.context_page.mouse.move(bounding_box["x"] + bounding_box["width"] / 2, # type: ignore
                                           bounding_box["y"] + bounding_box["height"] / 2) # type: ignore
        # Get x coordinate center position
        x = bounding_box["x"] + bounding_box["width"] / 2 # type: ignore
        # Simulate sliding operation
        await element.hover() # type: ignore
        await self.context_page.mouse.down()

        for track in tracks:
            # Loop mouse movement according to trajectory
            # steps controls the ratio of single movement speed, default is 1, meaning the distance moves in 0.1 seconds no matter how far, larger value means slower
            await self.context_page.mouse.move(x + track, 0, steps=move_step)
            x += track
        await self.context_page.mouse.up()

    async def login_by_cookies(self):
        utils.logger.info("[DouYinLogin.login_by_cookies] Begin login douyin by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".douyin.com",
                'path': "/"
            }])
