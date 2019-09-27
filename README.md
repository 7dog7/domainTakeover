# domainTakeover
## 简介
域名接管检测工具  
没什么好说的就是获取域名cname解析,进行判断是否域名能购买  

如果乱码请把  # -*- coding:utf-8 -*-替换为 # -*- encoding:gb2312 -*-  
## 使用说明

1. domain.txt文件
    >www.baidu.com  
    >baidu.com  
2. TakeoverResult.txt (检测到生成)
    >www.baidu.com|True  
    >baidu.com|False  
3. 扫描启动
   >python domainTakeover.py(输出的内容不用管,就是怕你感觉他没动静,才输出)
