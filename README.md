# 简介
这是一个用于识别出租车发票的OCR模型，使用的模型是PP-OCRv4；同时支持对图片进行分割，将图片中的发票筛选出来，使用的模型是yolov8

## 配置环境
以下配置是基于windows下cpu环境  
```
conda create --name paddle_env python=3.8 --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/  
activate paddle_env
pip install ultralytics
pip3 install torch torchvision torchaudio  
python -m pip install paddlepaddle==2.6.0 -i https://pypi.tuna.tsinghua.edu.cn/simple  
pip install "paddleocr>=2.0.1"   
pip install -r requirements.txt  
``` 

## 模型下载
[链接](https://drive.google.com/file/d/1XDW8pxMIA554Jr0K5txgZCKjRQly_jns/view?usp=drive_link)  
把下载后的文件夹ppocr4_det、ppocr4_rec、ch_ppocr_mobile_v2.0_cls、yolov8放置在model的文件夹下

## 测试
将需要进行识别的图片放在test_img文件夹下，运行main.py文件，结果将会生成在result文件夹下

## 参考 
https://github.com/PaddlePaddle/PaddleOCR  
https://github.com/ultralytics/yolov5
