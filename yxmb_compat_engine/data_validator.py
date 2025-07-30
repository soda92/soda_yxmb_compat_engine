import logging
import re
import numpy as np
from .chinese_id_check import is_valid_chinese_id
from kapybara.common.write_excel import excel_append
from typing import Tuple, Optional
import pandas as pd


def validate_record(record: dict, headers: list, config: dict) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    验证单个记录。

    Args:
        record (dict): 一条数据记录。
        headers (list): 表头列表。
        config (dict): 从 toml 文件加载的配置。

    Returns:
        验证结果，身份证号，日期。
    """
    # 检查身份证号是否为空或NaN
    if isinstance(record["身份证号"], float) and np.isnan(record["身份证号"]):
        return False, None, None
    if isinstance(record["身份证号"], str) and record["身份证号"].strip() == "":
        return False, None, None

    # 从配置中获取验证规则
    validation_config = config.get("validation", {})
    strict_id_check = validation_config.get("strict_id_check", True)

    # 验证身份证号格式
    id_number = str(record["身份证号"])
    if strict_id_check:
        verified, message = is_valid_chinese_id(id_number)
        if not verified:
            logging.error(f"身份证号 {id_number} 无效: {message}")
            excel_append(
                "执行结果/异常名单.xlsx",
                "身份证号",
                id_number + "\t",
                "异常原因",
                message,
            )
            return False, None, None

    sfzh = id_number.replace("x", "X").strip()

    # 根据配置的列名顺序查找日期
    date_columns_priority = validation_config.get("date_columns", ["随访日期", "成功", "日期"])
    date_value = None
    found_column = None
    for col_name in date_columns_priority:
        if col_name in headers:
            date_value = record[col_name]
            found_column = col_name
            break
    
    if found_column is None:
        logging.critical(f'{sfzh} - 在表头中未找到任何指定的日期列: {date_columns_priority}')
        return False, None, None

    # ... (日期解析逻辑保持不变) ...
    date_data_str = ""
    if isinstance(date_value, (int, float)) and not np.isnan(date_value):
        try:
            date_data_str = pd.to_datetime(
                date_value, unit="D", origin="1899-12-30"
            ).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    if not date_data_str:
        date_data_str = str(date_value)

    date_match = re.findall(r"\d{4}-\d{2}-\d{2}", date_data_str)
    if not date_match:
        excel_append(
            "执行结果/异常名单.xlsx",
            "身份证号",
            sfzh + "\t",
            "异常原因",
            f"在列 '{found_column}' 中找到的日期格式不正确",
        )
        logging.critical(f"{sfzh} - 在列 '{found_column}' 中找到的日期格式不正确: {date_data_str}")
        return False, None, None

    return True, sfzh, date_match[0]
