import logging
import re
import numpy as np
from .chinese_id_check import is_valid_chinese_id
from kapybara.common.write_excel import excel_append
from typing import Tuple
import pandas as pd


def validate_record(record, headers) -> Tuple[bool, str, str]:
    """
    验证单个记录。

    Args:
        record (dict): 一条数据记录。
        headers (list): 表头列表。

    Returns:
        验证结果，身份证号，日期。
    """
    # 检查身份证号是否为空或NaN
    if isinstance(record['身份证号'], float) and np.isnan(record['身份证号']):
        return False, None, None
    if isinstance(record['身份证号'], str) and record['身份证号'].strip() == '':
        return False, None, None

    # 验证身份证号格式
    id_number = str(record['身份证号'])
    verified, message = is_valid_chinese_id(id_number)
    if not verified:
        logging.error(f'身份证号 {id_number} 无效: {message}')
        excel_append(
            '执行结果/异常名单.xlsx',
            '身份证号',
            id_number + '\t',
            '异常原因',
            message,
        )
        return False, None, None

    sfzh = id_number.replace('x', 'X').strip()

    # 验证并提取日期
    date_value = None
    if '成功' in headers:
        date_value = record['成功']
    elif '日期' in headers:
        date_value = record['日期']
    elif '随访日期' in headers:
        date_value = record['随访日期']
    else:
        logging.critical(f'{sfzh} - 在表头中未找到 "成功" 或 "日期" 或 "随访日期" 列')
        return False, None, None

    date_data_str = ''
    if isinstance(date_value, (int, float)) and not np.isnan(date_value):
        # Handle Excel date serial number
        try:
            # Excel for Windows epoch is 1899-12-30
            date_data_str = pd.to_datetime(date_value, unit='D', origin='1899-12-30').strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass  # Will be handled by regex check later
    
    if not date_data_str:
        date_data_str = str(date_value)

    date_match = re.findall(r'\d{4}-\d{2}-\d{2}', date_data_str)
    if not date_match:
        excel_append(
            '执行结果/异常名单.xlsx',
            '身份证号',
            sfzh + '\t',
            '异常原因',
            '日期格式不正确',
        )
        logging.critical(f'{sfzh} - 日期格式不正确')
        return False, None, None

    return True, sfzh, date_match[0]
