import json
import os
import subprocess

from beancount_bot.dispatcher import Dispatcher
from beancount_bot.util import logger

_PATH = os.path.split(os.path.realpath(__file__))[0]
_SCRIPT_PATH = os.path.join(_PATH, 'costflow-parser.js')


class CostflowDispatcher(Dispatcher):
    """
    Costflow 语法处理器
    """

    def get_name(self) -> str:
        return 'Costflow'

    def get_usage(self) -> str:
        with open(self.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if 'account' in config and len(config['account']) > 0:
            account = '\n'.join([f'  {k}：{v}' for k, v in config['account'].items()])
        else:
            account = '未定义账户'

        if 'formula' in config and len(config['formula']) > 0:
            formula = '\n'.join([f'  {k}：{v}' for k, v in config['formula'].items()])
        else:
            formula = '未定义公式'

        return '语法文档：https://www.costflow.io/docs/syntax/\n\n' \
               f'账户：\n{account}\n\n' \
               f'公式：\n{formula}'

    def __init__(self, costflow_config: str):
        self.config = costflow_config

    def quick_check(self, input_str: str) -> bool:
        # 基本什么都可以接受
        return True

    def _process_raw(self, input_str: str) -> str:
        try:
            output = subprocess.check_output(
                ['node', _SCRIPT_PATH,
                 '--config', self.config,
                 '--json',
                 input_str], stderr=subprocess.STDOUT, timeout=3,
                universal_newlines=True)
        except subprocess.CalledProcessError as e:
            logger.error(f'Costflow 解析错误：{e.output}', e)
            raise ValueError('Costflow 解析错误，请检查相关配置！')
        logger.debug("调用 Costflow CLI 返回：%s", output)
        data = json.loads(output)
        if 'error' in data:
            raise ValueError(f'Costflow 错误：{data["error"]}')
        return data['output']
