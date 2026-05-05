# re6-research
生化危机6游戏文本批处理工具。

## 使用说明

### extract_gmd.py

gmd2txt，导出格式示例：

```
[Line 0]
Yes

[Line 1]
No

[Line 2]
OK
```

### repack_gmd.py

txt2gmd。txt与原始gmd文件需在同路径下，原始gmd默认使用英语版`_eng`。

### merge_text.py

合并两种不同语言文本。默认为英语`_eng`和日语`_jpn`。

文本内容完全相同时，只保留一种，不重复合并。

有文本内容大于等于三行时（长文件），合并时在两种语言文本间增加一个空行。

合并后格式示例：

```
[Line 0]
English
日本語

[Line 1]
English
English
English

日本語
日本語
```

### merge_text_sizehack.py

在`merge_text.py`的基础上新增功能，合并时在每行文本开头增加内联代码`<SIZE>`定义字号。两种语言字号可分别定义。

合并后格式示例：

```
[Line 204]
<SIZE 18>Thank you.
<SIZE 18>ありがとう
```

### format_key_guide.py

精简合并后的键位引导文本。部分文本仍需手动调整。

```
# 优化前
[Line 2780]
<KEY 1> MAIN MENU
<KEY 1> メインメニュー

# 优化后
[Line 2780]
<KEY 1> MAIN MENU メインメニュー
```

## 致谢

99.9% 的代码由 Gemini Pro 编写 :)
