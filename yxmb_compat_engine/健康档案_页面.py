from kapybara.common.envWrite import env_write
from kapybara.common.write_excel import excel_append
from kapybara.shortcuts import WebDriver
import logging
from urllib.parse import urlparse
from phis_config import ProgramConfigV2
from .async_xhr import get_async_xhr

from .运行时数据 import 已完成数量

def get_root_url() -> str:
    url = ProgramConfigV2.get_url()
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def 搜索并打开病人页面(driver: WebDriver, id_number: str, menuId: str):
    """
    根据身份证号查询并打开个人首页
    """
    global 已完成数量
    sfzh = id_number
    sfzh = str(sfzh).replace('x', 'X').strip()
    logging.info('当前处理身份证号: %s', sfzh)
    env_write('执行结果/env.txt', 2, f'当前处理身份证号:{sfzh}')

    patient_id = get_async_xhr(sfzh)

    if patient_id == -1 or patient_id is None:
        # 找不到查询结果
        patient_id = get_async_xhr(sfzh)
        if patient_id == -1 or patient_id is None:
            # 如果还是找不到，说明没有建档
            已完成数量 += 1
            env_write('执行结果/env.txt', 3, f'已完成数量:{已完成数量}')
            logging.info('无档案')
            excel_append(
                '执行结果/异常名单.xlsx', '身份证号', sfzh + '\t', '异常原因', '暂无建档'
            )
            return

    target_url = f'{get_root_url()}/phis/app/ehr/index/{patient_id}?targetMenuId={menuId}'
    original_window = driver.current_window_handle

    driver.switch_to.new_window('tab')
    driver.get(target_url)
    return original_window
