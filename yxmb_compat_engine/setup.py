import pandas as pd
from kapybara.common.excel_create import check_and_create_excel
import logging


def setup_excel_file(file_path, columns):
    """检查Excel是否具有正确的表头,如果没有，则添加表头"""
    check_and_create_excel(file_path)
    try:
        existing_data = pd.read_excel(file_path)
        if not set(columns).issubset(existing_data.columns):
            # File exists but headers are wrong/missing
            header_df = pd.DataFrame(columns=columns)
            header_df.to_excel(file_path, index=False, header=True)  # noqa: E501
            logging.warning('文件 %s 没有表头,已添加表头', file_path)
    except (
        pd.errors.EmptyDataError,
        ValueError,
    ):  # ValueError for empty file with no columns
        # File is empty, add headers
        header_df = pd.DataFrame(columns=columns)
        header_df.to_excel(file_path, index=False, header=True)  # noqa: E501
        logging.info('文件 %s 为空,已添加表头', file_path)
