# 安装
``` 
pip install httpx
pip install aiofiles
```


# 如何使用
进入main.py文件

```python
import asyncio
from async_qiniu import Qiniu

q = Qiniu('输入你的access_key' , '输入你的secret_key')

# 生成上传token凭证
token = asyncio.run(q.upload_token(bucket='请输入空间名称' , key='请输入文件名称'))

# 上传文件
# 存储区域的上传地址，详情:https://developer.qiniu.com/kodo/1671/region-endpoint-fq'
# 注意！ 存储区域的上传地址里请吧s去掉，否则会上传失败  例：http(s)://upload.qiniup.com => http://upload.qiniup.com。
r = asyncio.run(q.put_file(up_token=token ,key='请输入文件名称' ,district_url='请输入空间存储区域的上传路径' ,file_path='文件的本地路径'))

print(r)
```

直接运行

