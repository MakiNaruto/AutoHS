import os
import time
from xml.dom import minidom

class HearthStoneLogWatcher:
    def __init__(self):
        super().__init__()

    def find_start_position_reverse(self, log_file_path):
        START_MARKERS = [" - CREATE_GAME"]
        block_size = 4096
        overlap = 200

        with open(log_file_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            position = size
            last_buffer = b""

            while position > 0:
                read_size = min(block_size, position)
                position -= read_size
                f.seek(position)
                buffer = f.read(read_size)

                # 拼接上次读取的尾部作为 overlap
                combined = buffer + last_buffer
                lines = combined.split(b"\n")

                for i in reversed(range(len(lines))):
                    try:
                        line = lines[i].decode(errors="ignore")
                    except Exception:
                        continue
                    if any(marker in line for marker in START_MARKERS):
                        # 找到匹配行，计算它的偏移量
                        prefix = b"\n".join(lines[:i])
                        offset = position + len(prefix) + (1 if prefix else 0)
                        return offset

                # 更新 last_buffer 为当前读取块的前 overlap 字节
                last_buffer = buffer[-overlap:] if len(buffer) >= overlap else buffer

        return 0  # 没找到，从头开始

    def log_listener(self, log_file_path):
        # 1. 查找最近的开始标记位置
        start_offset = self.find_start_position_reverse(log_file_path)
        # 2. 从该位置顺序回放日志初始化状态

        with open(log_file_path, "r", encoding="utf-8") as f:
            f.seek(start_offset)
            # f.seek(0, 2)  # 跳到文件末尾
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                self.log_praser(line)

    def pretty_xml(self, root):
        # 假设 root 有 to_xml_string() 方法，返回字符串形式的 XML
        xml = root.to_xml_string()

        # 解析为 DOM
        dom = minidom.parseString(xml)

        # 美化输出（不带 xml 声明）
        pretty = dom.toprettyxml(indent="\t")

        # 去除多余空行
        lines = [line for line in pretty.split("\n") if line.strip()]

        # 去掉 <?xml ... ?> 行（第一行）
        if lines[0].startswith("<?xml"):
            lines = lines[1:]

        return "\n".join(lines)
