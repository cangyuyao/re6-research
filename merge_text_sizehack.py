import re
import os
import argparse

# 分别设置英文和日文的字号标签（你可以根据排版需求自由修改）
ENG_TEXT_SIZE = "18"
JPN_TEXT_SIZE = "18" 

def parse_localization_file(filepath, text_size, flatten=False):
    """
    解析本地化文本文件，并根据传入的 text_size 为非空行添加 <SIZE> 标签。
    """
    data = {}
    header = []
    current_key = None
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n') 
            
            match = re.match(r'^\[Line (\d+)\]$', line)
            
            if match:
                current_key = match.group(0)
                data[current_key] = []
            elif current_key is not None:
                data[current_key].append(line)
            else:
                header.append(line)
                
    for key in data:
        while data[key] and data[key][-1] == '':
            data[key].pop()
            
        # 新增：如果启用了 flatten（平铺），将多行合并为单行
        if flatten and data[key]:
            # 过滤掉中间可能的纯空行，把所有有内容的行用空格连接
            valid_lines = [line for line in data[key] if line.strip()]
            if valid_lines:
                data[key] = [" ".join(valid_lines)]
            else:
                data[key] = []
                
        for i in range(len(data[key])):
            if data[key][i].strip():  
                # 根据传入的语言专属字号添加标签
                data[key][i] = f"<SIZE {text_size}>{data[key][i]}"
                
        data[key] = '\n'.join(data[key])
        
    while header and header[-1] == '':
        header.pop()
    header_str = '\n'.join(header)
        
    return header_str, data

def merge_localization_files(eng_path, jpn_path, output_path, flatten_eng):
    # 解析时分别传入对应的字号
    # 为英文文件传入 flatten_eng 参数
    eng_header, eng_data = parse_localization_file(eng_path, ENG_TEXT_SIZE, flatten=flatten_eng)
    _, jpn_data = parse_localization_file(jpn_path, JPN_TEXT_SIZE, flatten=False)
    
    all_keys = set(eng_data.keys()).union(set(jpn_data.keys()))
    
    def get_key_number(key):
        match = re.search(r'\d+', key)
        return int(match.group()) if match else 0
        
    sorted_keys = sorted(all_keys, key=get_key_number)
    
    with open(output_path, 'w', encoding='utf-8') as out:
        if eng_header:
            out.write(f"{eng_header}\n\n")
            
        for key in sorted_keys:
            eng_text = eng_data.get(key)
            jpn_text = jpn_data.get(key)
            
            eng_has_content = eng_text is not None and bool(eng_text.strip())
            jpn_has_content = jpn_text is not None and bool(jpn_text.strip())
            
            out.write(f"{key}\n")
            
            # if eng_has_content or jpn_has_content:
                # out.write("<SIZE 0>\n")
            
            if eng_has_content and jpn_has_content:
                if eng_text == jpn_text:
                    out.write(f"{eng_text}\n\n")
                else:
                    eng_lines = eng_text.split('\n')
                    jpn_lines = jpn_text.split('\n')
                    
                    for i in range(min(len(eng_lines), len(jpn_lines))):
                        # 分别使用对应的字号生成正则匹配规则
                        pattern_eng = r'^(<SIZE ' + ENG_TEXT_SIZE + r'>)?(<CHAR\s*\d+>)'
                        pattern_jpn = r'^(<SIZE ' + JPN_TEXT_SIZE + r'>)?(<CHAR\s*\d+>)'
                        
                        m_eng = re.match(pattern_eng, eng_lines[i])
                        m_jpn = re.match(pattern_jpn, jpn_lines[i])
                        
                        if m_eng and m_jpn and m_eng.group(2) == m_jpn.group(2):
                            prefix = m_jpn.group(1) or ""
                            tag_to_remove = m_jpn.group(2)
                            
                            rest_of_line = jpn_lines[i][len(prefix) + len(tag_to_remove):]
                            jpn_lines[i] = f"{prefix}{rest_of_line}"
                            
                    eng_text_out = '\n'.join(eng_lines)
                    jpn_text_out = '\n'.join(jpn_lines)
                    
                    if len(eng_lines) >= 3 or len(jpn_lines) >= 3:
                        out.write(f"{eng_text_out}\n\n{jpn_text_out}\n\n")
                    else:
                        out.write(f"{eng_text_out}\n{jpn_text_out}\n\n")
                        
            elif eng_has_content:
                out.write(f"{eng_text}\n\n")
                
            elif jpn_has_content:
                out.write(f"{jpn_text}\n\n")
                
            else:
                out.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="合并本地化文本，支持中英双语独立字号及 <CHAR> 标签智能处理。")
    parser.add_argument("basename", help="要合并的文件名主干。例如输入 'System'")
    
    # 新增参数：--flatten-eng
    parser.add_argument(
        "--flatten-eng", 
        action="store_true", 
        help="启用此项时，将英文的多行文本合并为单行（用空格连接）。"
    )
    
    args = parser.parse_args()
    
    base_name = re.sub(r'_(chS|chT|eng|fre|ger|ita|jpn|pol|por|rus|spa)', '', args.basename)
    
    eng_file = f"{base_name}_eng.txt"
    jpn_file = f"{base_name}_jpn.txt"
    output_file = f"{args.basename}_merged.txt"
    
    if os.path.exists(eng_file) and os.path.exists(jpn_file):
        print(f"正在合并: {eng_file} 和 {jpn_file} ...")
        merge_localization_files(eng_file, jpn_file, output_file, args.flatten_eng)
        print(f"✅ 合并完成！结果已保存为: {output_file}")
    else:
        print(f"❌ 错误：找不到指定的文件。")
        print(f"请确保以下两个文件都在当前目录下：\n- {eng_file}\n- {jpn_file}")