import struct
import os
import re
import sys

def repack_txt_to_gmd(original_gmd_path, txt_path, output_gmd_path):
    if not os.path.exists(original_gmd_path):
        print(f"❌ 找不到原 GMD 文件: {original_gmd_path}")
        return
    if not os.path.exists(txt_path):
        print(f"❌ 找不到修改后的 TXT 文件: {txt_path}")
        return

    print("🚀 开始解析并重组 GMD 文件...")

    # ==========================================
    # 1. 解析你修改后的 TXT 文件
    # ==========================================
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    pattern = re.compile(r'\[Line \d+\]\n(.*?)(?=\n\[Line \d+\]|\Z)', re.DOTALL)
    matches = pattern.findall(txt_content)

    extracted_texts = []
    for match in matches:
        if match.endswith('\n\n'):
            text = match[:-2]
        elif match.endswith('\n'):
            text = match[:-1]
        else:
            text = match
        extracted_texts.append(text)

    # ==========================================
    # 2. 从原 GMD 文件中提取 Header 数据
    # ==========================================
    with open(original_gmd_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'GMD\x00':
            print("❌ 原文件不是标准的 GMD 文件！")
            return
            
        header_bytes = f.read(20)
        original_string_count = struct.unpack('<5I', header_bytes)[4]

    if len(extracted_texts) != original_string_count:
        print(f"⚠️ 警告：TXT 行数 ({len(extracted_texts)}) 与原文件 ({original_string_count}) 不匹配！")
        print("为了防止游戏崩溃，将强制使用原文件行数（缺失补空，多余截断）。")
    
    final_texts = []
    for i in range(original_string_count):
        if i < len(extracted_texts):
            final_texts.append(extracted_texts[i])
        else:
            final_texts.append("") 

    # ==========================================
    # 3. 构建新的文本区和偏移表 (已优化空行处理)
    # ==========================================
    new_string_block = bytearray()
    new_offset_table = bytearray()
    current_offset = 0

    for text in final_texts:
        # 如果这一行是完全空的（没有任何字符）
        if text == "":
            # 写入 0xFFFFFFFF (即十六进制的 FF FF FF FF)
            # 这告诉引擎：此项无文本，不要去文本区寻找。
            new_offset_table.extend(struct.pack('<I', 0xFFFFFFFF))
            # 注意：这里我们不往 new_string_block 里加 \x00，也不增加 current_offset
        else:
            # 如果有正常的文本
            new_offset_table.extend(struct.pack('<I', current_offset))
            text_bytes = text.encode('utf-8') + b'\x00'
            new_string_block.extend(text_bytes)
            current_offset += len(text_bytes)

    # ==========================================
    # 4. 计算新的文本区总大小
    # ==========================================
    new_string_block_size = len(new_string_block)
    size_bytes = struct.pack('<I', new_string_block_size)

    # ==========================================
    # 5. 拼装成最终的 GMD 文件写入硬盘
    # ==========================================
    with open(output_gmd_path, 'wb') as out_f:
        out_f.write(magic)              
        out_f.write(header_bytes)       
        out_f.write(new_offset_table)   
        out_f.write(size_bytes)         
        out_f.write(new_string_block)   

    print("\n🎉 封包圆满成功！")
    print(f" - 处理行数: {original_string_count}")
    print(f" - 剔除了所有无内容的空行，对应偏移量已标记为 FF FF FF FF")
    print(f" - 新文本区大小: {new_string_block_size} 字节")
    print(f" - 生成的可用文件: {output_gmd_path}")


# =======================
# 命令行入口逻辑
# =======================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 错误：缺少目标文件名！")
        print("👉 正确用法示例：python repack_gmd.py mes_stage06_eng.gmd")
        sys.exit(1)

    input_file = sys.argv[1]

    if input_file.lower().endswith('.gmd'):
        base_name = input_file[:-4]
    else:
        base_name = input_file
        input_file = f"{input_file}.gmd" 

    original_gmd = f"{base_name}_eng.gmd"
    modified_txt = f"{base_name}_merged.txt"
    output_gmd   = f"{base_name}_MOD.gmd"

    # result = re.sub(r'_(chS|chT|eng|fre|ger|ita|jpn|pol|por|rus|spa)', '', base_name)

    print(f"📦 准备处理的配置：")
    print(f"   原 GMD 文件: {original_gmd}")
    print(f"   源 TXT 文件: {modified_txt}")
    print(f"   目标输出物:  {output_gmd}\n")

    repack_txt_to_gmd(original_gmd, modified_txt, output_gmd)