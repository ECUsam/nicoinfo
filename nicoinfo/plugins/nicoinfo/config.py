from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    # 日志配置
    logger_level = 'INFO'
    log_path = './log/'
