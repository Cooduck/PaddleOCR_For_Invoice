from paddleocr import PaddleOCR, draw_ocr
from ultralytics import YOLO
from PIL import Image, ImageDraw
import os
import shutil
import time

def find_text(text, word_to_find):
    if word_to_find in text:
        return 1
    else:
        return 0

def ocr_predict(img_path):
    start_time = time.time()  # 记录开始时间

    img_name = os.path.basename(img_path)
    # 预测得到结果
    ocr = PaddleOCR(use_angle_cls=False, lang="ch")
    result = ocr.ocr(img_path, cls=False)
    result = result[0]

    # 提取图片参考点，用于文本分类
    image = Image.open(img_path)
    width, height = image.size
    points1 = []
    points2 = []
    for pic in result:
        if find_text(pic[1][0], '机打发票'):
            points1.append(pic[0][0])
            points1.append(pic[0][1])
            points1.append(pic[0][2])
            points1.append(pic[0][3])
        if find_text(pic[1][0], '手写无效'):
            points2.append(pic[0][0])
            points2.append(pic[0][1])
            points2.append(pic[0][2])
            points2.append(pic[0][3])

    base_height = 0.0
    for point in points1:
        base_height = max(base_height,point[1])
    for point in points2:
        base_height = max(base_height,point[1])

    base_width = width / 2

    # 提取预测结果中的发票代码和发票号码
    id = []
    number = []
    for pic in result:
        infor = pic[1][0]
        points = pic[0]
        if find_text(infor, '发票代码'):
            y1 = height
            y2 = 0
            x1 = width
            x2 = 0
            for point in points:
                x1 = min(x1, point[0])
                x2 = max(x2, point[0])
                y1 = min(y1, point[1])
                y2 = max(y2, point[1])

            # 若预测框不能将代码和文本框在一起，则需要特殊操作
            if (x2 - x1)/width < 0.7:
                base = (y1 + y2)/2

                for img in result:
                    points = img[0]
                    word_id = img[1][0]
                    y1 = height
                    y2 = 0
                    for point in points:
                        y1 = min(y1, point[1])
                        y2 = max(y2, point[1])
                    y_average = (y2 + y1)/2
                    if abs(y_average - base)/height < 0.02 and not find_text(word_id, '发票代码'):
                        id.append('发票代码' + word_id)
                        break
            else:
                id.append(infor)

        elif find_text(infor, '发票号码'):
            y1 = height
            y2 = 0
            x1 = width
            x2 = 0
            for point in points:
                x1 = min(x1, point[0])
                x2 = max(x2, point[0])
                y1 = min(y1, point[1])
                y2 = max(y2, point[1])

            # 若预测框不能将代码和文本框在一起，则需要特殊操作
            if (x2 - x1) / width < 0.7:
                base = (y1 + y2) / 2

                for img in result:
                    points = img[0]
                    word_id = img[1][0]
                    y1 = height
                    y2 = 0
                    for point in points:
                        y1 = min(y1, point[1])
                        y2 = max(y2, point[1])
                    y_average = (y2 + y1) / 2
                    if abs(y_average - base) / height < 0.02 and not find_text(word_id, '发票号码'):
                        number.append('发票号码' + word_id)
                        break
            else:
                number.append(infor)

    # 提取预测结果中的左栏信息
    cnt = 0
    word = []
    for pic in result:
        points = pic[0]
        x1 = width
        x2 = 0
        miny = height
        for point in points:
            x1 = min(x1, point[0])
            x2 = max(x2, point[0])
            miny = min(miny, point[1])
        if (x1+x2)/2 < base_width and miny > base_height and not(x1 < base_width and x2 > base_width):
            cnt += 1
            word.append(pic[1][0][0:3] if len(pic[1][0]) >= 3 else pic[1][0][0:2])
        elif x1 < base_width and x2 > base_width and miny > base_height and (x2 - x1)/width > 0.6:
            cnt += 1
            word.append(pic[1][0][0:3] if len(pic[1][0]) >= 3 else pic[1][0][0:2])
        if cnt == 9:
            break

    # 提取预测结果中的右栏信息
    cnt = 0
    information = []
    for pic in result:
        points = pic[0]
        x1 = width
        x2 = 0
        miny = height
        for point in points:
            x1 = min(x1, point[0])
            x2 = max(x2, point[0])
            miny = min(miny, point[1])
        if (x1+x2)/2 > base_width and miny > base_height and (x2 - x1)/width < 0.6:
            cnt += 1
            information.append(pic[1][0])
        elif x1 < base_width and x2 > base_width and miny > base_height and (x2 - x1)/width > 0.6:
            cnt += 1
            information.append(pic[1][0][3:])
        if cnt == 9 :
            break

    # 将上面提取到的信息写入txt
    try:
        txt = []
        txt.append(id[0].replace('发票代码', "发票代码:\t"))
        txt.append(number[0].replace('发票号码', "发票号码:\t"))
        for i in range(9):
            txt.append(word[i] + '\t' + information[i])

        if find_text(img_name, '.jpg'):
            with open('./result/' + img_name.replace('.jpg', ".txt"), "w", encoding='utf-8') as file:
                for line in txt:
                    file.write(line + '\n')
        elif find_text(img_name, '.png'):
            with open('./result/' + img_name.replace('.png', ".txt"), "w", encoding='utf-8') as file:
                for line in txt:
                    file.write(line + '\n')
    except IndexError:
        if find_text(img_name, '.jpg'):
            with open('./result/' + img_name.replace('.jpg', ".txt"), "w", encoding='utf-8') as file:
                file.write("该图片无法进行检测识别")
        elif find_text(img_name, '.png'):
            with open('./result/' + img_name.replace('.png', ".txt"), "w", encoding='utf-8') as file:
                file.write("该图片无法进行检测识别")
        print(f"{img_name}的检测与识别失败")
        print()
        return

    # 保存预测框于图片上
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    im_show = draw_ocr(image, boxes, font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('./result/' + img_name)

    end_time = time.time()  # 记录结束时间
    print(f"已完成{img_name}的检测与识别，用时{end_time - start_time}秒")
    print()

def yolov8_segment(img_paths):
    model = YOLO('model/yolov8/runs/segment/best.torchscript')

    for img_path in img_paths:
        start_time = time.time()    # 记录开始时间

        results = model(img_path)
        file_name = os.path.splitext(os.path.basename(img_path))[0]
        for result in results:
            boxes = result.boxes
            image = Image.open(img_path)
            draw = ImageDraw.Draw(image)
            box_color = "red"
            box_width = 3
            for box in boxes.xyxy:
                x1, y1, x2, y2 = box
                draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)
            image.save(f"result/{file_name}_with_boxes.jpg")

            crop_image(img_path, boxes.xyxy)

            end_time = time.time()  # 记录结束时间
            print(f"已完成{file_name}的分割，用时{end_time - start_time}秒")
            print()


def crop_image(image_path, box_coordinates):
    """
    根据给定的 box 坐标裁剪图片，并保存裁剪后的图片。
    参数：
    - image_path: 原始图片的文件路径。
    - box_coordinates: 包含左上角和右下角坐标的 box 列表，每个 box 由四个浮点数组成。
    """
    # 打开原始图片
    image = Image.open(image_path)
    file_name = os.path.splitext(os.path.basename(image_path))[0]

    # 遍历每个 box，并裁剪图片
    for i, box in enumerate(box_coordinates):
        # 提取左上角和右下角坐标
        x1, y1, x2, y2 = map(int, box)

        # 裁剪图片
        cropped_image = image.crop((x1, y1, x2, y2))

        # 如果裁剪下来的图片高小于宽，则旋转90度
        if cropped_image.height < cropped_image.width:
            cropped_image = cropped_image.transpose(Image.ROTATE_270)

        # 保存裁剪后的图片
        cropped_image.save(f"tmp_img/{file_name}_cropped_image_{i}.jpg")

if __name__ == '__main__':

    # 清空之前保存的结果
    if os.path.exists('./result'):
        shutil.rmtree('./result')
    os.makedirs('./result')

    if os.path.exists('./tmp_img'):
        shutil.rmtree('./tmp_img')
    os.makedirs('./tmp_img')

    # 分割
    print('#'*20,'开始分割图片','#'*20)
    folder_path = "./test_img"
    img_names = os.listdir(folder_path)
    img_paths = [folder_path + '/' + img_name for img_name in img_names]
    yolov8_segment(img_paths)
    print('#' * 20, '分割结束', '#' * 20)

    print()

    # 检测+识别
    print('#' * 20, '开始检测和识别图片', '#' * 20)
    folder_path = "./tmp_img"
    img_names = os.listdir(folder_path)
    img_paths = [os.path.join(folder_path, img_name) for img_name in img_names]
    for img_path in img_paths:
        ocr_predict(img_path)
    print('#' * 20, '检测和识别结束', '#' * 20)
    ocr_predict('tmp_img/picture2_cropped_image_0.jpg')