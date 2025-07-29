import logging
from kapybara.browserlib.custom_browser import CustomBrowser
from .setup import setup_excel_file
from phis_logging import setup_logging
from phis_login import 登录健康档案系统
from .main_数据 import 获取剩余数据
from .data_validator import validate_record


def run(patient_func):
    setup_logging()

    # if is_software_expired():
    #     logging.error('软件已到期')
    #     return
    setup_excel_file("执行结果/异常名单.xlsx", ["身份证号", "异常原因"])
    setup_excel_file("执行结果/成功名单.xlsx", ["身份证号", "成功"])

    data_remaining, headers = 获取剩余数据()
    remaining_counts = len(data_remaining)
    logging.info("剩余操作数: %d", remaining_counts)
    if len(remaining_counts) == 0:
        logging.info("程序已执行完成")
        return
    if "身份证号" not in headers:
        logging.critical("未找到身份证号列，请检查文档/名单.xlsx")
        return

    _driver = CustomBrowser(disable_image=False)
    登录健康档案系统()

    try:
        for record in data_remaining:
            result, _sfzh, date_data = validate_record(record, headers)
            if not result:
                continue

            patient_func(record, headers, date_data)

    except Exception as e:
        logging.error(e)
        raise
    else:
        logging.info("程序已执行完成")
        _driver.quit()
        # env_write('执行结果/env.txt', 10, '执行完成:1')


if __name__ == "__main__":
    run()
