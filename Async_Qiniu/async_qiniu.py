# -*- coding: utf-8 -*-
import asyncio
# 开启异步循环事件
import httpx
# 允许异步发送请求
import aiofiles
# 允许异步读取文件
import hmac
# python里不可逆的加密模块 使用msg进行加密
import json
# 用户转换JSON数据
import time
# 时间戳
from hashlib import sha1
# 加密方式
from base64 import urlsafe_b64encode
# 对类字节对象s进行安全的URL及文件系统Base64编码，替换标准Base64编码中的'+'为'-', '/'为'_'，返回编码后的字节序列


# 异步七牛云类
class Qiniu(object):

    def __init__(self , access_key , secret_key):
        self.__access_key = access_key
        self.__secret_key = secret_key.encode('utf-8')

    async def __token(self , data):
        hashed = hmac.new(self.__secret_key , data.encode('utf-8') , sha1)
        ret = urlsafe_b64encode(hashed.digest())
        return ret.decode('utf-8')

    async def token(self , data):
        return '{0}:{1}'.format(self.__access_key , await self.__token(data))

    async def token_with_data(self , data):
        ret = urlsafe_b64encode(data.encode('utf-8'))
        data = ret.decode('utf-8')
        return '{0}:{1}:{2}'.format(
            self.__access_key , await  self.__token(data) , data)

    async def __upload_token(self , policy):
        data = json.dumps(policy , separators=(',' , ':'))
        return await self.token_with_data(data)

    async def upload_token(self , bucket , key=None , expires=3600 , policy=None , strict_policy=True):
        """生成上传凭证

        Args:
            bucket:  上传的空间名
            key:     上传的文件名，默认为空
            expires: 上传凭证的过期时间，默认为3600s
            policy:  上传策略，默认为空

        Returns:
            上传凭证
        """
        if bucket is None or bucket == '':
            raise ValueError('invalid bucket name')

        scope = bucket
        if key is not None:
            scope = '{0}:{1}'.format(bucket , key)

        args = dict(
            scope=scope ,
            deadline=int(time.time()) + expires ,
        )

        return await self.__upload_token(args)

    async def put_file(self , up_token , key , district_url , file_path , mime_type='application/octet-stream' ,
                       params=None , file_name=None):
        """上传文件到七牛

        Args:
            up_token:                 上传凭证
            key:                      上传文件名
            district                  存储区域路径
            file_path:                上传文件的路径
            params:                   自定义变量，规格参考 http://developer.qiniu.com/docs/v6/api/overview/up/response/vars.html#xvar
            mime_type:                上传数据的mimeType
            file_name:                文件本地名称
        Returns:
            一个ResponseInfo对象
        """
        
        
        # 发送请求需要携带的变量
        fields = {}
        
        # 判断是否传参自定义变量
        if params:
            for k , v in params.items():
                fields[k] = str(v)

        # 文件名如果不为空则加入请求变量里
        if key is not None:
            fields['key'] = key
        
        # 将鉴权token加入请求变量
        fields['token'] = up_token

        # file_name 是该文件在本地的文件名
        f_name = file_name
        if not f_name or not f_name.strip():
            f_name = 'file_name'

        # 以二进制形式打开文件
        async with aiofiles.open(file_path , 'rb') as f:
            content = await f.read()
        
        # 使用with关键字调用httpx的异步发送请求方法
        async with  httpx.AsyncClient() as client:
            try:
                # 发送请求到具体存储区域上传地址，携带参数以及文件。files={文件在请求里的名字，并不是保存到空间时的名字；具体文件；文件类型(二进制数据类型)}
                r = await client.post(district_url , data=fields , files={'file': (f_name , content , mime_type)})
                return r
            except Exception as e:
                print(e)
                return '上传失败！'



