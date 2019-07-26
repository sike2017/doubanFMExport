# doubanFMExport
豆瓣电台红心音乐下载命令行工具
> 依赖于 python3 requests库
> 可通过 pip install requests安装

> 需在python3下运行


> 默认会下载到脚本目录下的download目录下
> 可在config/config.json中通过更改downloadPath或-od参数控制脚本下载目录

使用方式:

  > -od参数和-Du参数不可同时使用

  python doubanFMExport.py -Du "你的豆瓣电台用户名"
  
  python doubanFMExport.py -od "下载路径"
