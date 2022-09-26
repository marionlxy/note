## Python标准库: random

-Author: bavdu

-Email: bavduer@163.com

-GitHub: https://github.com/bavdu

---





```python
import random


print(random.random())					# 随机产生一个0到1之间的小数

print(random.uniform(0,9))			# 随机产生一个0到9之间的小数

print(random.randint(1, 9))     # 随机输出一个1到9之间的整数

element = [1, 2, 3, [4, 5, 6], 'ABC', 'employee']
print(random.choice(element))   # 随机输出列表中的某个元素

number = [1, 2, 34, 57, 81, 99]
random.shuffle(number)          # 打乱给定列表中的元素
print(number)
```

- 验证码生成器

```python
# coding: utf8
# author: bavduer
# usage: study random


import random


def verificationCode(number):
    """
    product verification code of user input number
    :param number: verification code's number
    :return: verification code
    """
    vCode = ''
    for n in range(number):
        nums = random.randint(0, 9)
        word = chr(random.randint(65, 90))
        middle = random.choice([nums, word])
        vCode += str(middle)
    return vCode


verCode = verificationCode(4)
print(verCode)
userInput = input('Please input verification code: ')
if userInput.lower() != verCode.lower():
    print('your Stupid !')
else:
    print('please load...')
```

