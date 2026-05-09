import re

def get_visible_length(word):
    """
    计算去掉所有 <...> 标签后的实际可见字符长度。
    """
    clean_word = re.sub(r'<[^>]*>', '', word)
    return len(clean_word)

def wrap_english_text(text, max_len=150):
    """
    对英文文本进行重新换行，保证不打断单词、标点，并正确忽略标签长度。
    """
    # 核心修复点：使用正则匹配单词。
    # (?:<[^>]*>|\S)+ 意味着：要么匹配一个完整的 <...> 标签，要么匹配非空格字符。
    # 这样 <SIZE 15> 会被完整提取，如果它紧挨着单词（如 <SIZE 15>At），也会被视为同一个整体。
    words = re.findall(r'(?:<[^>]*>|\S)+', text)
    
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        word_vlen = get_visible_length(word)

        if not current_line:
            current_line.append(word)
            current_len = word_vlen
        else:
            # 判断加入下一个单词后是否超过最大长度 (+1 是因为单词之间拼接时会加一个空格)
            if current_len + 1 + word_vlen <= max_len:
                current_line.append(word)
                current_len += 1 + word_vlen
            else:
                # 超过长度，结算当前行
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = word_vlen

    # 处理最后剩下的一行
    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)

def is_japanese(text):
    """
    通过检测是否包含平假名、片假名或汉字来判断是否为日文段落。
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))

def process_translation_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    current_paragraph = []

    def flush_paragraph():
        if not current_paragraph:
            return

        text = " ".join(current_paragraph)

        if text.startswith('[Line '):
            output_lines.extend(current_paragraph)
        elif is_japanese(text):
            output_lines.extend(current_paragraph)
        else:
            wrapped_text = wrap_english_text(text, max_len=135)
            output_lines.extend(wrapped_text.split('\n'))

        current_paragraph.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            output_lines.append("") 
        elif stripped.startswith('[Line '):
            flush_paragraph()
            output_lines.append(line.rstrip('\n')) 
        else:
            current_paragraph.append(line.rstrip('\n'))

    flush_paragraph()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines) + "\n")

if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "output.txt"
    
    print("开始处理文本...")
    process_translation_file(input_file, output_file)
    print(f"处理完成！结果已保存至 {output_file}")