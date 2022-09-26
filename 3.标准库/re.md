## Python标准库: re

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---



| 正则表达式 | 描述                             | 示例                                           |
| ---------- | -------------------------------- | ---------------------------------------------- |
| ^          | 行首标记                         | ^imp匹配以imp起始的行                          |
| $          | 行尾标记                         | imp$匹配以imp结尾的行                          |
| .          | 匹配任意一个字符                 | linu. 匹配 linux 或 linus                      |
| []         | 匹配包含在 [字符] 之中的任意字符 | coo[kl] 匹配cool 或 cook                       |
| [^]        | 匹配不包含在 [字符] 中的任意字符 | 9[ ^01]匹配92, 93, … 但不能匹配90或91          |
| [ - ]      | 匹配[ - ]范围中的任意字符        | [1-5]匹配数字1到5、[a-z]匹配任意一个小些字母   |
| ?          | 匹配之前项的1次或0次             | hel?o匹配 hello 或 helo                        |
| +          | 匹配之前项的1次或多次            | hel+匹配hel、hell, 但不能匹配he                |
| *          | 匹配之前项的0次或多次            | hel*匹配he、hel、hell                          |
| {n}        | 匹配之前项n次                    | [0-9]{3}匹配一个任意三位数                     |
| {n,}       | 匹配之前项至少n次                | [0-9]{3,}匹配一个任意三位数或一个更多位的数    |
| {n, m}     | 匹配之前项至少n次, 至多m次       | [0-9]{2,5}匹配从两位数到五位数之间任意一个数字 |



```python
import re


# 正则表达式的切片功能
data = 'this is my house'
# result = data.split()
# print(result)
result = re.split(pattern='[ ]', string=data)
print(result)


# 寻找符合条件的数据
source = 'abc ABC INTER inter lines adc'
result = re.findall(pattern='a.c', string=source)
print(result)

# 正则表达式
# ^ $ []: [^] [ - ]  *  ()  |:或者 &:并且
# ? + {3, 5}

source = '39.200.110.135 [ERROR]: no such file or directory.'
result = re.findall(pattern='[1-9]+\.[0-9]+\.[0-9]+\.[0-9]+', string=source)
print(result)

# regular = '(?:[0-9]+\.[0-9]+\.?)'
# regular = '([0-9]+\.){3}'
# 精准匹配IP地址(符合规则)
regular = '(?:(?:[1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]?)\.(?:[0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]?)\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]?)?)'
result = re.findall(pattern=regular, string=source)
print(result)


# search: 寻找每行数据源中的符合条件的数据
# compile: 指定正则表达式
data = 'abc ABC abC'
pattern = re.compile('ab.')
result = pattern.search(data)
print(result)


# sub: 相当于shell中的sed -ri s/'被替换字符'/'替换字符'/g filename
data = 'abc ABC abc ABC abc'
pattern = re.compile('a.c')
result = pattern.sub(repl='CLOUD1901', string=data, count=2)
print(result)
```

