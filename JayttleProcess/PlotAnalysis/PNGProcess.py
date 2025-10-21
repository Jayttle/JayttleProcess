from PIL import Image

def convert_to_grayscale(input_image_path, output_image_path):
    """
    将输入的PNG图像转换为灰度图像并保存。

    参数:
    - input_image_path: 输入的PNG图像文件路径。
    - output_image_path: 输出的灰度图像文件路径。
    """
    try:
        # 打开PNG图片
        input_image = Image.open(input_image_path)

        # 转换为灰度图
        gray_image = input_image.convert('L')

        # 保存灰度图
        gray_image.save(output_image_path)

        print(f"已将 {input_image_path} 转换为灰度图，并保存为 {output_image_path}")

    except Exception as e:
        print(f"转换过程中发生错误: {e}")

if __name__ =='__main__':
    # 示例用法：
    input_png = r"D:\Program Files (x86)\Software\OneDrive\PyPackages_img\索道坐标图_1.png"
    output_gray_png = 'output_gray.png'

    convert_to_grayscale(input_png, output_gray_png)