import tkinter as tk
import cv2
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import sys
import os

# Initialize window
root = tk.Tk()
root.title("UVC Camera")
root.geometry("1700x700")

# Detect available cameras
camera_indexes = []
for i in range(10):
    cap = cv2.VideoCapture(i)
    if not cap.isOpened():
        continue
    camera_indexes.append(i)
    cap.release()

print("Available cameras:", camera_indexes)

# Show error message if no camera is available
if len(camera_indexes) == 0:
    messagebox.showerror("Error", "找不到摄像头")
    sys.exit(0)

# Show error message if camera cannot be opened
try:
    camera = cv2.VideoCapture(camera_indexes[0])  # Open the first detected camera by default
except:
    messagebox.showerror("Error", "摄像头打不开，设备损坏或接触不良")
    sys.exit(0)

# Detect available resolutions
res_options = []
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
res_options.append([width, height])

for j in range(30):
    old_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    old_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width+j*100)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height+j*100)
    new_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    new_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if new_width != old_width:
        res_options.append([new_width, new_height])

print("Available resolutions:", res_options)

# Set the lowest resolution as the default
camera.set(cv2.CAP_PROP_FRAME_WIDTH, res_options[0][0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, res_options[0][1])

# Button callback functions

def on_capture():
    home_dir = os.path.expanduser('~')
    cv2.imwrite(home_dir + "/capture.png", img)
    # Resize the image while maintaining the aspect ratio
    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    current_image = Image.fromarray(cv2image)
    w, h = current_image.size
    ratio = min(850.0 / w, 638.0 / h)
    current_image = current_image.resize((int(ratio * w), int(ratio * h)), Image.ANTIALIAS)
    imgtk = ImageTk.PhotoImage(image=current_image)
    photo_panel.imgtk = imgtk
    photo_panel.config(image=imgtk)
    messagebox.showinfo("Info", "拍照成功")

def on_switch_res(value):
    global camera
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, value[0])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, value[1])

def on_switch_cam(value):
    global camera
    # print("切换摄像头")
    # print("选择的值是: ", str(value))
    # 结束预览
    root.after_cancel(video_loop_id)
    camera.release()
    # 创建新的捕捉对象并打开摄像头
    camera = cv2.VideoCapture(value)
    if not camera.isOpened():
        messagebox.showerror("错误", "摄像头无法打开")
        sys.exit()
    on_video_loop()
           
def on_video_loop():
    global img,video_loop_id
    success, img = camera.read() # 从摄像头读取照片
    if success:
        cv2.waitKey(10)
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA) # 转换颜色从BGR到RGBA
        current_image = Image.fromarray(cv2image)        # 将图像转换成Image对象
        # 等比缩放照片
        w,h = current_image.size
        ratio = min(850.0/w, 600.0/h)
        current_image = current_image.resize((int(ratio * w), int(ratio * h)), Image.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(image=current_image)
        video_panel.imgtk = imgtk
        video_panel.config(image=imgtk)
        video_loop_id = root.after(1, on_video_loop)
        
video_panel = tk.Label(root)
photo_panel = tk.Label(root)

video_panel.grid( # 左上居中对齐
    row=0, column=0, columnspan=4, padx=20, pady=20, sticky=tk.NW
)

photo_panel.grid( # 右上居中对齐
    row=0, column=4, columnspan=2,sticky=tk.EW, padx=20, pady=20
)

# 摄像头标签+下拉框
label3 = tk.Label(root, text="选择摄像头")
label3.grid(row=1, column=0, sticky="E", padx=10, pady=10)

variable1 = tk.StringVar(root)
variable1.set(camera_indexes[0])
cam_dropdown = tk.OptionMenu(root, variable1, *camera_indexes, command=on_switch_cam)
cam_dropdown.grid(row=1, column=1, sticky="W", padx=10, pady=10)

# 分辨率标签+下拉框
label4 = tk.Label(root, text="选择分辨率")
label4.grid(row=1, column=2, sticky="E", padx=10, pady=10)

variable2 = tk.StringVar(root)
variable2.set(res_options[0])
res_dropdown = tk.OptionMenu(root, variable2, *res_options, command=on_switch_res)
res_dropdown.grid(row=1, column=3, sticky="W", padx=10, pady=10)

# 拍照和退出按钮
capture_button = tk.Button(root, text="拍照", command=on_capture)
capture_button.grid(row=1, column=4, padx=10, pady=10)

exit_button = tk.Button(root, text="退出", command=root.quit)
exit_button.grid(row=1, column=5, padx=10, pady=10)

# 一些页面设置
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=2)
root.grid_columnconfigure(5, weight=2)
root.grid_rowconfigure(0, weight=13)
root.grid_rowconfigure(1, weight=1)

on_video_loop()
root.mainloop()
