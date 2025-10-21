import pyautogui
import os
from PIL import Image 
import time
import pytesseract
import chardet

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

def move_and_click( x, y):
    """移动鼠标到指定坐标并单击"""
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(0.5)

def move_and_Twoclick( x, y):
    """移动鼠标到指定坐标并双击"""
    pyautogui.moveTo(x, y)
    pyautogui.click()
    pyautogui.click()

def type_string( string):
    """输入字符串"""
    pyautogui.typewrite(string)

def move_and_click_with_shift( x, y):
    """按住 Shift 键的鼠标移动单击"""
    pyautogui.keyDown('shift')  # 按下 Shift 键
    pyautogui.moveTo(x, y)
    pyautogui.click()
    pyautogui.keyUp('shift')  # 释放 Shift 键

def press_delete_key():
    """按下键盘上的 Delete 键"""
    pyautogui.press('delete')

def press_ctrl_space():
    """按下键盘上的 Ctrl 和空格键"""
    pyautogui.hotkey('ctrl', 'space')

def right_click_and_press_D():
    """右键并按下键盘的D"""
    pyautogui.rightClick()  # 右键
    pyautogui.press('d')    # 按下键盘的D键   

def get_subdirectories_with_no_csv(folder_path):
    """获取目标文件夹中所有没有 CSV 文件的文件夹的名字"""
    subdirectories = []
    # 遍历目标文件夹中的所有文件和文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 检查是否为文件夹
        if os.path.isdir(item_path):
            # 检查文件夹内是否有 CSV 文件
            if not any(file.lower().endswith('.csv') for file in os.listdir(item_path)):
                subdirectories.append(item)
    return subdirectories

def get_subdirectories_with_no_csv_without03(folder_path):
    """获取目标文件夹中所有没有 CSV 文件的文件夹的名字，排除第5~6位是'03'的文件夹，并且文件夹内文件数等于6"""
    subdirectories = []
    # 遍历目标文件夹中的所有文件和文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 检查是否为文件夹
        if os.path.isdir(item_path):
            # 检查文件夹名是否满足条件
            if (len(item) >= 6) and (item[4:6] != '03'):
                # 检查文件夹内是否有 CSV 文件
                if not any(file.lower().endswith('.csv') for file in os.listdir(item_path)):
                    # 检查文件夹内文件数量是否为6
                    if len(os.listdir(item_path)) == 6:
                        subdirectories.append(item)
    return subdirectories

def get_csv_file_paths(folder_path):
    """获取目标文件夹中所有CSV文件的路径"""
    csv_file_paths = []

    # 遍历目标文件夹中的所有文件和文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                csv_file_paths.append(file_path)

    return csv_file_paths


def move_up_with_right_click(distance):
    """按住右键的鼠标向上移动一定距离"""
    pyautogui.mouseDown(button='right')  # 按住右键
    pyautogui.move(0, -distance, duration=0.5)  # 向上移动指定距离
    pyautogui.mouseUp(button='right')  # 松开右键

def move_right_with_right_click(distance):
    """按住右键的鼠标向右移动一定距离"""
    pyautogui.mouseDown(button='right')  # 按住右键
    pyautogui.move(distance, 0, duration=0.5)  # 向右移动指定距离
    pyautogui.mouseUp(button='right')  # 松开右键

def moveTo_up_with_right_click(x,y,distance):
    """移动到指定位置再按住右键的鼠标向上移动一定距离"""
    pyautogui.moveTo(x,y)
    move_up_with_right_click(distance)

def moveTo_right_with_right_click(x,y,distance):
    """移动到指定位置再按住右键的鼠标向右移动一定距离"""
    pyautogui.moveTo(x,y)
    move_right_with_right_click(distance)


def get_mouse_position():
    """获取鼠标位置"""
    x, y = pyautogui.position()
    # 返回鼠标位置
    return x, y

def list_folders(directory: str) -> list[str]:
    """获取目标文件夹下的所有文件夹folder名字"""
    folder_names = []
    for root, dirs, files in os.walk(directory):
        for folder in dirs:
            folder_names.append(os.path.join(root, folder))
    return folder_names

def list_files_in_folders(folder_names: list[str]) -> list[str]:
    """获取目标文件夹下的所有文件file名字"""
    file_paths = []
    for folder in folder_names:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_paths.append(os.path.join(root, file))
    return file_paths

def read_text_from_window(window_region: tuple[int, int, int, int]) -> str:
    """
    从指定的窗口区域中读取文本
    Args:
        window_region: 窗口区域的坐标 (x, y, width, height)
    Returns:
        识别到的文本
    """
    # 截取窗口区域的截图
    screenshot = pyautogui.screenshot(region=window_region)
    # 示例：灰度化和二值化
    screenshot = screenshot.convert('L')  # 转为灰度图
    threshold = 200  # 阈值，根据需要调整
    screenshot = screenshot.point(lambda p: p > threshold and 255)
    # 将截图保存为临时文件
    temp_image_path = "temp_screenshot.png"
    screenshot.save(temp_image_path)
    # 使用 pytesseract 识别文本
    text = pytesseract.image_to_string(Image.open(temp_image_path), lang='chi_sim')
    # # 删除临时文件
    # os.remove(temp_image_path)
    return text


def ensure_no_input_data():
    # 确保tbc输入的文件为空
    window_region_输入= (170, 284, 35, 16)
    while True:
        # 识别窗口中的文本
        recognized_text = read_text_from_window(window_region_输入)
        if recognized_text:
            move_and_click(190, 289) #单击第一个文件
            right_click_and_press_D() #删除文件
        else:
            break
    # 请替换为您希望识别的窗口区域的坐标
    window_region_输入= (170, 270, 35, 16)
    # 识别窗口中的文本
    recognized_text = read_text_from_window(window_region_输入)

    if recognized_text:
        move_and_click(205, 275) #单击第一个文件
        right_click_and_press_D() #删除文件


def auto_turn_off():
    move_and_click(27, 1572)#菜单
    move_and_click(582, 1500)#菜单
    time.sleep(1)
    move_and_click(592, 1433)#关机
    move_and_click(592, 1433)#关机


def check_data_points(folder_path: str):
    to_delete_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(folder_path, filename)
            # 使用 chardet 检测文件编码
            with open(csv_file_path, 'rb') as file:
                result = chardet.detect(file.read())
                encoding = result['encoding']
            # 使用检测到的编码打开文件
            with open(csv_file_path, 'r', encoding=encoding) as file:
                next(file)  # Skip the header row
                line = next(file)  # Read the second line
                data = line.strip().split('\t')
                if len(data) != 30:
                    print(f"Error:{csv_file_path} got:{len(data)}.")
                    to_delete_list.append(csv_file_path)
    for item in to_delete_list:
        os.remove(item)

def check_in_one_step():
    to_process_fold_list = [ 'R052_0407','R071_0407', 'R072_0407','R081_0407', 'R082_0407']
    # to_process_fold_list = [ 'R031_1215',"R032_1215",'R051_1215','R052_1215','R071_1215', 'R081_1215', 'R082_1215']
    root_csv_path = rf'D:\Program Files (x86)\Software\OneDrive\PyPackages_DataSave\new_data'

    for key in to_process_fold_list:
        data_save_path = os.path.join(root_csv_path, key)
        print(f"{key}: {data_save_path}")
        check_data_points(data_save_path)


def TBC_auto_Process(Merge_path , save_path):
    window_region_保存 = (1625, 567, 37, 20)
    window_region_输入= (1590, 950, 35, 16)
    # 目标文件夹路径
    # 获取目标文件夹中所有文件夹的名字
    subdirectories = get_subdirectories_with_no_csv_without03(Merge_path)
    for directory in subdirectories:
        exit_for_loop = False  # 标志，用于指示是否退出外部循环
        ensure_no_input_data()
        move_and_click(87, 31)#本地
        time.sleep(1) #等待
        move_and_click(39, 74)     #tbc-输入
        time.sleep(1) #等待
        move_and_click(2453, 233)     #导入文件夹
        time.sleep(1) #等待
        move_and_Twoclick(2424, 233)     #双击
        type_string(f"\\{directory}") # 输入文件夹名字
        move_and_click(2422, 323) #单击第一个文件
        move_and_click_with_shift(2422, 423) #拖动并点击最后一个文件
        move_and_click(2431, 1510) #输入
        start_time_input = time.time()  # 开始第一个循环的时间
         # 内部while循环
        while True:
            # 识别窗口中的文本
            recognized_text = read_text_from_window(window_region_输入)
            # 如果识别到的文本是"确定"
            if "确定" in recognized_text:
                move_and_click(1607, 961)  # 保存
                break  # 结束内部循环
            # 检查是否超过一分钟
            if time.time() - start_time_input > 60:
                print("第一个循环执行时间超过1分钟，终止程序。")
                exit_for_loop = True  # 设置标志，指示需要退出外部循环
                break  # 结束内部循环
            time.sleep(1)  # 等待

        # 检查是否需要退出外部循环
        if exit_for_loop:
            print("外部循环执行时间超过1分钟，终止程序。")
            break  # 退出外部循环

        time.sleep(1) #等待
        move_and_click(136, 40) #测量
        time.sleep(0.5) #等待
        move_and_click(675, 77) #基线解算
        start_time_save = time.time()  # 开始第二个循环的时间
        while True:
            # 识别窗口中的文本
            recognized_text = read_text_from_window(window_region_保存)
            # 如果识别到的文本是"保存"
            if "保存" in recognized_text:
                time.sleep(1)  # 等待
                move_and_click(1643, 575)  # 点击保存按钮
                break  # 结束循环
            # 检查是否超过一分钟
            if time.time() - start_time_save > 90:
                print("第二个循环执行时间超过1分钟，终止程序。")
                exit_for_loop = True  # 设置标志，指示需要退出外部循环
                break
        # 检查是否需要退出外部循环
        if exit_for_loop:
            print("外部循环执行时间超过1分钟，终止程序。")
            break  # 退出外部循环
        time.sleep(1.5) #等待
        move_and_click(84, 40)#本地
        time.sleep(0.5) #等待
        move_and_click(96, 73)#输出菜单
        time.sleep(1) #等待
        move_and_click(54, 244) #单击R031点
        move_and_click(2179, 449) #单击到文件名的初始
        time.sleep(1) #等待
        move_and_click_with_shift(2474, 447) #拖动并全选文件名
        time.sleep(1) #等待
        type_string(f"D:\\Ropeway\\{save_path}\\TBC\\{directory}.csv") # 输入文件夹名字
        time.sleep(1) #等待D
        move_and_click(2436, 1511)#输出栏里的保存
        time.sleep(1) #等待
        move_and_click(168, 290) #单击第一个文件
        time.sleep(0.5) #等待
        move_and_click_with_shift(147, 376) #拖动并点击最后一个文件
        time.sleep(0.5) #等待
        right_click_and_press_D() #删除文件
