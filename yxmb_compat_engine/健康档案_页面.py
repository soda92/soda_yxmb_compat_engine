from kapybara.shortcuts import WebDriver
from urllib.parse import urlparse
from phis_config import ProgramConfigV2
from .async_xhr import get_async_xhr
import re
from .result_writer import ResultWriter # 确保导入

# 不再需要这些导入
# from kapybara.common.envWrite import env_write
# from kapybara.common.write_excel import excel_append
# from .运行时数据 import 已完成数量


def get_root_url() -> str:
# ... (此函数不变) ...
    url = ProgramConfigV2.get_url()
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def get_org_code(driver) -> str:
# ... (此函数不变) ...
    org_code = re.findall("orgCode *: *'(.*)'", driver.page_source)
    for i in org_code:
        if len(i) == 4:
            return i
    raise ValueError("无法找到机构码")


def 搜索并打开病人页面(driver: WebDriver, id_number: str, menuId: str, writer: ResultWriter):
    """
    根据身份证号查询并打开个人首页
    """
    sfzh = str(id_number).replace("x", "X").strip()
    writer.log_current_person(sfzh) # 使用 writer 记录当前处理的人

    org_code = get_org_code(driver)
    patient_id = get_async_xhr(sfzh, org_code)

    if patient_id == -1 or patient_id is None:
        # 找不到查询结果，重试一次
        patient_id = get_async_xhr(sfzh, org_code)
        if patient_id == -1 or patient_id is None:
            # 如果还是找不到，说明没有建档，使用 writer 记录
            writer.log_failure(sfzh, "暂无建档")
            return

    target_url = (
        f"{get_root_url()}/phis/app/ehr/index/{patient_id}?targetMenuId={menuId}"
    )
    original_window = driver.current_window_handle

    driver.switch_to.new_window("tab")
    driver.get(target_url)
    return original_window