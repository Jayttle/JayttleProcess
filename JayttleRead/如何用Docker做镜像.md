场景目的：撰写了一个py脚本，配备着对应的requirements.txt；需要在服务器里一直运行执行任务；

**本地打包**

1. 准备好py脚本 + requrements.txt的库 版本号 + https://pypi.tuna.tsinghua.edu.cn/simple

2. 在py脚本文件夹下 准备Dockerfile：

   ```dockerfile
   FROM pj-xjt-python312:base
   ENV DEBIAN_FRONTEND=noninteractive
   WORKDIR /app
   ENV PYTHONDONTWRITEBYTECODE=1 \
       PYTHONUNBUFFERED=1 \
       TZ=Asia/Shanghai
   COPY . .
   EXPOSE 5000
   CMD ["python", "data_process_script.py"]
   ```

3. 上传至服务器：{名} = root {name}=xjt 

   1. 连接服务器：ssh {名}@xx.xx.xxx.xx  password:xxxxxx

   2. 创建自己的文件夹 mkdir {name}

   3. 在本地电脑中py文件脚本的 根目录新打开cmd，上传文件夹：scp -r .\\{project_name}@xx.xx.xxx.xx:/{名}/{name}

      ![image-20250923110622559](./assets/image-20250923110622559.png)

4. 在文件夹下执行：docker build -t nengyuan-ds:v0.0.1 . （创建了一个镜像）

5. 执行命令：docker run -it nengyuan-ds:latest /bin/bash  （进入容器可以执行的环境）

6. 执行脚本：python xxx.py 运行，查看是否正常运行；

7. 将镜像打包成.tar文件：docker save -o pj-xjt-nengyuan.tar nengyuan-ds:latest

其他语句：

- 删除docker多余的镜像：docker rmi -f b1dc6972547a（例子）
- 查看有哪些镜像：docker images
- 进入文件里面进行编辑：vi Dockerfile

**最终准备文件：**

1. 代码文件夹：用于作映射
2. docker-compose.yml
3. {镜像}.tar

**开始部署**

1. 在服务器里mkdir准备好文件夹：先是mkdir nengyuan-ds，在nengyuan-ds下mkdir下面两个：

   conf（存储代码文件夹与docker-compose.yml）和images（{镜像}.tar）

2. 利用scp上传文件 到指定文件夹

3. 进行docker load：[root@pintechs images]# docker load -i pj-xjt-nengyuan.tar

   ![image-20250924141539227](./assets/image-20250924141539227.png)

4. 进行compse做映射：将docker里面的代码映射到自己的代码文件夹中：

   [root@pintechs nengyuan-ds]# docker compose up -d

5. 查看docker是否运行：docker ps | grep nengyuan

6. 查看docker的日志：docker logs -f --tail 100 nengyuan-ds


**在烟厂服务器的相关操作：**

nengyuan-ds部署在【切丝服务器上】
\-------------------------------------------------------------------
文件夹路径：/mnt/sdc/nengyuan-ds
image镜像路径：/mnt/sdc/nengyuan-ds/images
代码路径：/mnt/sdc/nengyuan-ds/real_process_script
\-------------------------------------------------------------------
查看容器状态：docker ps | grep nengyuan-ds
查看容器日志：docker logs -f --tail 100 nengyuan-ds

重启容器：docker restart nengyuan-ds 	
docker compose -f docker-compose.yml down -d
docker compose -f docker-compose.yml up -d
docker run -it 082a6a9e4beb /bin/bash

**在烟厂服务器现有docker 新增/修改 库：**

本地进行下载准备whl文件：

```cmd
# 创建临时目录
mkdir numpy-offline
cd numpy-offline

# 下载指定版本的 NumPy wheel 文件
pip download numpy==1.26.4 --only-binary=:all: --platform manylinux2014_x86_64 -i https://mirrors.aliyun.com/pypi/simple/  
```

然后上传服务器 scp 命令

在服务器里面进入docker，对docker里面pip install，然后run；
