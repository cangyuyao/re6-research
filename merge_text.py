import re
import os
import argparse

def parse_localization_file(filepath):
    """
    解析基于 [Line X] 格式的本地化文本文件。
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
        # 移除每个文本块末尾的空行
        while data[key] and data[key][-1] == '':
            data[key].pop()
        data[key] = '\n'.join(data[key])
        
    while header and header[-1] == '':
        header.pop()
    header_str = '\n'.join(header)
        
    return header_str, data

def merge_localization_files(eng_path, jpn_path, output_path):
    eng_header, eng_data = parse_localization_file(eng_path)
    _, jpn_data = parse_localization_file(jpn_path)
    
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
            
            # 判断内容是否存在（去除两端空白符后是否为空）
            eng_has_content = eng_text is not None and bool(eng_text.strip())
            jpn_has_content = jpn_text is not None and bool(jpn_text.strip())
            
            out.write(f"{key}\n")
            
            # 1. 双方都有实际文本内容
            if eng_has_content and jpn_has_content:
                if eng_text == jpn_text:
                    # 中英/日英文本相同，只保留一份
                    out.write(f"{eng_text}\n\n")
                else:
                    # 计算行数（通过计算换行符数量或分割列表的长度）
                    eng_lines = len(eng_text.split('\n'))
                    jpn_lines = len(jpn_text.split('\n'))
                    
                    # 任意一方大于等于3行，增加一个空行分隔
                    if eng_lines >= 3 or jpn_lines >= 3:
                        out.write(f"{eng_text}\n\n{jpn_text}\n\n")
                    else:
                        out.write(f"{eng_text}\n{jpn_text}\n\n")
                        
            # 2. 只有英文有实际内容
            elif eng_has_content:
                out.write(f"{eng_text}\n\n")
                
            # 3. 只有日文有实际内容
            elif jpn_has_content:
                out.write(f"{jpn_text}\n\n")
                
            # 4. 双方都没有实际内容（比如都只是占位的空行）
            else:
                out.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="合并游戏本地化文本，并根据行数智能排版。")
    parser.add_argument("basename", help="要合并的文件名主干。例如输入 'System'")
    
    args = parser.parse_args()
    
    base_name = re.sub(r'_(chS|chT|eng|fre|ger|ita|jpn|pol|por|rus|spa)', '', args.basename)
    
    eng_file = f"{base_name}_eng.txt"
    jpn_file = f"{base_name}_jpn.txt"
    output_file = f"{args.basename}_merged.txt"
    
    if os.path.exists(eng_file) and os.path.exists(jpn_file):
        print(f"正在合并: {eng_file} 和 {jpn_file} ...")
        merge_localization_files(eng_file, jpn_file, output_file)
        print(f"✅ 合并完成！结果已保存为: {output_file}")
    else:
        print(f"❌ 错误：找不到指定的文件。")
        print(f"请确保以下两个文件都在当前目录下：\n- {eng_file}\n- {jpn_file}")