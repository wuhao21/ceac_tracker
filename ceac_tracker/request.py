import requests
from bs4 import BeautifulSoup
import json
import base64
import os
from ceac_tracker.captcha_resolver.two_captcha_resolve import resolve_captcha
from ceac_tracker.utils.my_logging import get_logger

logger = get_logger(__file__)


def query_status(location, application_num):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

    session = requests.Session()
    ROOT = "https://ceac.state.gov"
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    # -------NIV page------
    r = session.get(url=f"{ROOT}/ceacstattracker/status.aspx?App=NIV", headers=headers)
    with open("tmp/NIV.html", "w") as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, features="lxml")

    # Find captcha image
    captcha = soup.find(name="img", id="c_status_ctl00_contentplaceholder1_defaultcaptcha_CaptchaImage")
    image_url = ROOT + captcha["src"]
    logger.info(f"Captcha URL = {image_url}")
    img_resp = session.get(image_url)
    with open("tmp/captcha.jpeg", "wb") as f:
        f.write(img_resp.content)
    img_base64 = base64.b64encode(img_resp.content).decode("ascii")

    # Resolve captcha
    captcha_num = resolve_captcha(img_base64)

    # Fill form
    def update_from_current_page(cur_page, name, data):
        ele = cur_page.find(name="input", attrs={"name": name})
        if ele:
            data[name] = ele["value"]

    data = {
        "ctl00$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSubmit",
        "ctl00_ToolkitScriptManager1_HiddenField": ";;AjaxControlToolkit, Version=4.1.40412.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-US:acfc7575-cdee-46af-964f-5d85d9cdcf92:de1feab2:f9cec9bc:a67c2700:f2c8e708:8613aea7:3202a5a2:ab09e3fe:87104b7c:be6fb298",
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnSubmit",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": "8GJOG5GAuT1ex7KX3jakWssS08FPVm5hTO2feqUpJk8w5ukH4LG/o39O4OFGzy/f2XLN8uMeXUQBDwcO9rnn5hdlGUfb2IOmzeTofHrRNmB/hwsFyI4mEx0mf7YZo19g",
        "__VIEWSTATEGENERATOR": "DBF1011F",
        "__VIEWSTATEENCRYPTED": "",
        "ctl00$ContentPlaceHolder1$Visa_Application_Type": "NIV",
        "ctl00$ContentPlaceHolder1$Location_Dropdown": location,
        "ctl00$ContentPlaceHolder1$Visa_Case_Number": application_num,
        "ctl00$ContentPlaceHolder1$Captcha": "34HDM",
        "LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha": "a81747f3a56d4877bf16e1a5450fb944",
        "LBD_BackWorkaround_c_status_ctl00_contentplaceholder1_defaultcaptcha": "1",
        "__ASYNCPOST": "true",
    }
    data["ctl00$ContentPlaceHolder1$Captcha"] = captcha_num
    fields_need_update = [
        "__VIEWSTATE",
        "__VIEWSTATEGENERATOR",
        "LBD_VCID_c_status_ctl00_contentplaceholder1_defaultcaptcha",
    ]
    for field in fields_need_update:
        update_from_current_page(soup, field, data)

    # logger.info(json.dumps(data, indent=4))
    # logger.info(f"{ROOT}/ceacstattracker/status.aspx")

    # -------Result page------
    r = session.post(url=f"{ROOT}/ceacstattracker/status.aspx", headers=headers, data=data)
    with open("tmp/RESULT.html", "w") as f:
        f.write(r.text)

    # Get useful data
    soup = BeautifulSoup(r.text, features="lxml")
    status_tag = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatus")
    if not status_tag:
        return {"success": False}
    application_num_returned = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblCaseNo").string
    assert application_num_returned == application_num
    status = status_tag.string
    visa_type = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblAppName").string
    case_created = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblSubmitDate").string
    case_last_updated = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblStatusDate").string
    description = soup.find("span", id="ctl00_ContentPlaceHolder1_ucApplicationStatusView_lblMessage").string

    result = {
        "success": True,
        "visa_type": visa_type,
        "status": status,
        "case_created": case_created,
        "case_last_updated": case_last_updated,
        "description": description,
        "application_num": application_num_returned,
    }
    return result


if __name__ == "__main__":
    res = query_status("BEJ", "AA00B7QPGN")
    logger.info(json.dumps(res, indent=4))
