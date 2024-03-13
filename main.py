from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os
def find_text(text, word_to_find):
    if word_to_find in text:
        return 1
    else:
        return 0

def ocr_predict(img_path):
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
        if pic[1][0] == '机打发票':
            points1.append(pic[0][0])
            points1.append(pic[0][1])
            points1.append(pic[0][2])
            points1.append(pic[0][3])
        if pic[1][0] == '手写无效':
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
            word.append(pic[1][0][0:3])
        elif x1 < base_width and x2 > base_width and miny > base_height and (x2 - x1)/width > 0.6:
            cnt += 1
            word.append(pic[1][0][0:3])
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
    txt = []
    txt.append(id[0].replace('发票代码', "发票代码:\t"))
    txt.append(number[0].replace('发票号码', "发票号码:\t"))
    for i in range(9):
        txt.append(word[i] + '\t' + information[i])

    if find_text(img_name, '.jpg'):
        with open('./result/' + img_name.replace('.jpg',".txt"), "w", encoding= 'utf-8') as file:
            for line in txt:
                file.write(line + '\n')
    elif find_text(img_name, '.png'):
        with open('./result/' + img_name.replace('.png',".txt"), "w", encoding= 'utf-8') as file:
            for line in txt:
                file.write(line + '\n')

    # 保存预测框于图片上
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    im_show = draw_ocr(image, boxes, font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('./result/' + img_name)

if __name__ == '__main__':
    folder_path = "./test_img"
    img_names = os.listdir(folder_path)
    img_paths = [os.path.join(folder_path, img_name) for img_name in img_names]

    for img_path in img_paths:
        ocr_predict('test_img/test6.png')

    print("预测结束")