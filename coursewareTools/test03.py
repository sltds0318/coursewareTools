def is_alpha_start(string):
    # 判断字符串是否非空
    if string:
        # 使用 isalpha() 方法判断字符串开头是否为字母
        return string[0].isalpha()
    else:
        return False

# 测试代码
print(is_alpha_start("abc"))     # True
print(is_alpha_start("1abc"))    # False
print(is_alpha_start("哈哈"))        # False