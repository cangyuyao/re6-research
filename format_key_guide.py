import re
import argparse
import os

def attempt_merge(line1, line2):
    """
    核心逻辑：检查两行是否具有相同的 <ICON> 或 <KEY> 标签。
    若相同，合并文本；若文本内容完全一致，则去重只保留一个。
    """
    tag_pattern = r'(<[^>]+>)'
    parts1 = re.split(tag_pattern, line1)
    parts2 = re.split(tag_pattern, line2)
    
    # 结构不一致或没有标签，不处理
    if len(parts1) != len(parts2) or len(parts1) == 1:
        return None
        
    for j in range(1, len(parts1), 2):
        tag1, tag2 = parts1[j], parts2[j]
        # 标签必须完全一致，且仅限于 ICON 或 KEY
        if tag1 != tag2 or not (tag1.startswith('<ICON') or tag1.startswith('<KEY')):
            return None
            
    # 执行合并
    merged_parts = [parts1[0]]
    for j in range(1, len(parts1), 2):
        tag = parts1[j]
        text1_clean = parts1[j+1].strip()
        text2_clean = parts2[j+1].strip()
        
        merged_parts.append(tag)
        
        # 判断是否是行内最后一个元素，决定尾部空格数量
        is_last = (j + 1 == len(parts1) - 1)
        spacing = " " if is_last else "  "
        
        # 【新增功能】：如果两行文本完全相同，则只保留一个
        if text1_clean == text2_clean:
            merged_parts.append(f" {text1_clean}{spacing}")
        else:
            merged_parts.append(f" {text1_clean} {text2_clean}{spacing}")

    return "".join(merged_parts).rstrip()

def process_file(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 '{input_path}'")
        return

    # 如果未指定输出路径，则自动生成：原文件名 + "_optimized" + 原后缀
    if not output_path:
        base_name, ext = os.path.splitext(input_path)
        output_path = f"{base_name}_optimized{ext}"

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_content = []
    i = 0
    while i < len(lines):
        current_line = lines[i].rstrip('\n')
        output_content.append(current_line)
        
        # 检查是否是 [Line X] 标记
        if re.match(r'^\[Line \d+\]$', current_line.strip()):
            if i + 2 < len(lines):
                l1 = lines[i+1].rstrip('\n')
                l2 = lines[i+2].rstrip('\n')
                
                # 尝试合并
                merged = attempt_merge(l1, l2)
                if merged:
                    output_content.append(merged)
                    i += 2 # 跳过原有的两行
        i += 1

    final_text = "\n".join(output_content)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    print(f"成功！处理后的文件已保存至: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文本本地化格式优化工具")
    parser.add_argument("input", help="输入的 .txt 文件路径")
    parser.add_argument("-o", "--output", help="输出的文件路径 (可选，若不指定则自动添加 _optimized 后缀)")

    args = parser.parse_args()
    process_file(args.input, args.output)