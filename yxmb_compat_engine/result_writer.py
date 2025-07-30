import pandas as pd
from kapybara.common.write_excel import excel_append
from kapybara.common.envWrite import env_write
from kapybara.common.excel_create import check_and_create_excel
import logging

class ResultWriter:
    """
    负责记录程序执行结果，包括写入成功/异常名单，并维护已完成数量。
    """

    def __init__(self, success_path: str, failure_path: str, env_path: str, initial_completed_count: int = 0):
        self.success_path = success_path
        self.failure_path = failure_path
        self.env_path = env_path
        self.completed_count = initial_completed_count

        # 定义表头
        self.success_columns = ["身份证号", "成功"]
        self.failure_columns = ["身份证号", "异常原因"]

        # 初始化Excel文件
        self._setup_excel_file(self.success_path, self.success_columns)
        self._setup_excel_file(self.failure_path, self.failure_columns)

    def _setup_excel_file(self, file_path, columns):
        """检查Excel是否具有正确的表头,如果没有，则添加表头"""
        check_and_create_excel(file_path)
        try:
            existing_data = pd.read_excel(file_path)
            if not set(columns).issubset(existing_data.columns):
                header_df = pd.DataFrame(columns=columns)
                header_df.to_excel(file_path, index=False, header=True)
                logging.warning('文件 %s 没有表头,已添加表头', file_path)
        except (pd.errors.EmptyDataError, ValueError):
            header_df = pd.DataFrame(columns=columns)
            header_df.to_excel(file_path, index=False, header=True)
            logging.info('文件 %s 为空,已添加表头', file_path)

    def _increment_and_log_count(self):
        """内部方法，用于增加计数并写入env文件"""
        self.completed_count += 1
        env_write(self.env_path, 3, f"已完成数量:{self.completed_count}")

    def log_success(self, id_number: str, reason: str = "成功"):
        """记录一条成功的操作"""
        excel_append(self.success_path, "身份证号", id_number + "\t", "成功", reason)
        self._increment_and_log_count()
        logging.info(f"记录成功: {id_number}")

    def log_failure(self, id_number: str, reason: str):
        """记录一条失败或跳过的操作"""
        excel_append(self.failure_path, "身份证号", id_number + "\t", "异常原因", reason)
        self._increment_and_log_count()
        logging.warning(f"记录异常: {id_number}, 原因: {reason}")

    def log_current_person(self, id_number: str):
        """更新当前正在处理的人员信息"""
        env_write(self.env_path, 2, f"当前处理身份证号:{id_number}")
        logging.info("当前处理身份证号: %s", id_number)
