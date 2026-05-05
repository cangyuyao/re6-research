import struct
import os
import sys

def extract_gmd_to_txt_v2(file_path, output_path):
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件: {file_path}")
        return

    with open(file_path, 'rb') as f:
        # 1. 读取 Magic (4 字节)
        magic = f.read(4)
        if magic != b'GMD\x00':
            print("❌ 这可能不是一个标准的 GMD 文件！")
            return

        # 2. 读取 Header (20 字节)
        header_bytes = f.read(20)
        header_data = struct.unpack('<5I', header_bytes)
        
        # 索引 4 是文本行数
        string_count = header_data[4]
        print(f"✅ 成功读取文件头！总文本行数: {string_count}")

        # 3. 读取 Offset Table (偏移量表)
        # 紧跟在 Header 后面，共 string_count * 4 个字节
        offsets = []
        for i in range(string_count):
            offset_bytes = f.read(4)
            offset = struct.unpack('<I', offset_bytes)[0]
            offsets.append(offset)
            
            # 顺便验证：第一个偏移量应该是 0
            if i == 0 and offset != 0:
                print(f"⚠️ 警告：第一个偏移量不是 0，而是 {offset}，文件结构可能异常！")

        # 4. 读取 Text Size (文本区总大小)
        unknown_padding = f.read(4)
        padding_val = struct.unpack('<I', unknown_padding)[0]
        print(f"🔍 文本区总大小设定值为: {padding_val} 字节 (Hex: {unknown_padding.hex()})")

        # 此时，指针刚好抵达文本数据区的起点！
        string_block_start = f.tell()
        print(f"📍 文本数据区起始绝对位置: {string_block_start} 字节\n")

        # 5. 根据偏移量提取文本
        extracted_texts = []
        for i in range(string_count):
            # 跳转到每句话的起始位置
            f.seek(string_block_start + offsets[i])

            # 逐字节读取，直到遇到 \x00
            chars = bytearray()
            while True:
                char = f.read(1)
                if char == b'\x00' or not char:
                    break
                chars.extend(char)

            # 解码为 UTF-8 文本
            text = chars.decode('utf-8', errors='replace')
            
            # 【新增：清洗换行符】
            # 先将原生的 \r\n 替换为 \n，再将可能单独存在的 \r 替换为 \n
            # 这样就能保证 Python 写入文件时不会产生双重换行
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            extracted_texts.append(text)

    # 6. 写入 TXT 文件
    with open(output_path, 'w', encoding='utf-8') as out_f:
        for i, text in enumerate(extracted_texts):
            out_f.write(f"[Line {i}]\n")
            out_f.write(f"{text}\n\n")

    print(f"🎉 提取完成！共提取 {len(extracted_texts)} 行文本。请查看 {output_path}。")


# =======================
# 命令行入口逻辑
# =======================
if __name__ == "__main__":
    # 检查是否传入了参数
    if len(sys.argv) < 2:
        print("❌ 错误：缺少目标文件名！")
        print("👉 正确用法示例：python extract_gmd.py mes_stage06_eng.gmd")
        sys.exit(1)

    # 获取传入的第一个参数
    input_file = sys.argv[1]

    # 去掉路径和扩展名，提取出基础名字
    if input_file.lower().endswith('.gmd'):
        base_name = input_file[:-4]
    else:
        base_name = input_file
        input_file = f"{input_file}.gmd" # 自动补全后缀

    # 自动推导输出的 TXT 文件名
    target_file = input_file
    output_text = f"{base_name}.txt"

    print(f"📦 准备处理的配置：")
    print(f"   原 GMD 文件: {target_file}")
    print(f"   目标输出物:  {output_text}\n")

    # 执行主程序
    extract_gmd_to_txt_v2(target_file, output_text)
