import tkinter as tk
from tkinter import messagebox
import pandas as pd
from tkinter import filedialog, messagebox
from PIL import ImageGrab
class ScheduleManager:
    def __init__(self, master):
        self.master = master
        self.master.title("课表管理器")
        self.schedule = pd.DataFrame(columns=["节次", "星期", "课程名称", "地点", "教师", "时间"])

        # 默认课程数据
        self.default_courses = [
            {"节次": "第1-2节", "星期": "周一", "课程名称": "云计算技术基础", "地点": "12-614", "教师": "邢老师", "时间": "8:00-9:30",
             "提醒时间": None},
            {"节次": "第3-4节", "星期": "周一", "课程名称": "云计算技术基础", "地点": "12-614", "教师": "邢老师", "时间": "9:40-11:10",
             "提醒时间": None},
            {"节次": "第5-6节", "星期": "周一", "课程名称": "python语言程序设计实践", "地点": "12-614", "教师": "张老师", "时间": "12:40-14:10",
             "提醒时间": None},
            {"节次": "第7-8节", "星期": "周一", "课程名称": "python语言程序设计实践", "地点": "12-614","教师": "张老师", "时间": "14:20-15:50",
             "提醒时间": None},
            {"节次": "晚上", "星期": "周一", "课程名称": "暂无课程安排", "地点": "", "教师": "", "时间": "18:40-20:55",
             "提醒时间": None},

            {"节次": "第1-2节", "星期": "周二", "课程名称": "信息安全概论", "地点": "12-510", "教师": "王老师", "时间": "8:00-9:30",
             "提醒时间": None},
            {"节次": "第3-4节", "星期": "周二", "课程名称": "云部署与维护", "地点": "9105", "教师": "官老师", "时间": "9:40-11:10",
             "提醒时间": None},
            {"节次": "第5-6节", "星期": "周二", "课程名称": "暂无课程安排", "地点": "","教师": "", "时间": "12:40-14:10",
             "提醒时间": None},
            {"节次": "第7-8节", "星期": "周二", "课程名称": "暂无课程安排", "地点": "","教师": "", "时间": "14:20-15:50",
             "提醒时间": None},
            {"节次": "晚上", "星期": "周二", "课程名称": "Linux操作系统", "地点": "12-614", "教师": "张老师", "时间": "18:40-20:55",
             "提醒时间": None},

            {"节次": "第1-2节", "星期": "周三", "课程名称": "Python语言程序设计", "地点": "12-308", "教师": "季老师", "时间": "8:00-9:30",
             "提醒时间": None},
            {"节次": "第3-4节", "星期": "周三", "课程名称": "Python语言程序设计", "地点": "12-308", "教师": "季老师", "时间": "9:40-11:10",
             "提醒时间": None},
            {"节次": "第5-6节", "星期": "周三", "课程名称": "云计算基础", "地点": "12-614", "教师": "邢老师", "时间": "12:40-14:10",
             "提醒时间": None},
            {"节次": "第7-8节", "星期": "周三", "课程名称": "暂无课程安排", "地点": "", "教师": "", "时间": "14:20-15:50",
             "提醒时间": None},
            {"节次": "晚上", "星期": "周三", "课程名称": "暂无课程安排", "地点": "", "教师": "", "时间": "18:40-20:55",
             "提醒时间": None},

            {"节次": "第1-2节", "星期": "周四", "课程名称": "大数据平台技术", "地点": "12-615", "教师": "郑老师", "时间": "8:00-9:30",
             "提醒时间": None},
            {"节次": "第3-4节", "星期": "周四", "课程名称": "大数据平台技术", "地点": "12-615", "教师": "郑老师", "时间": "9:40-11:10",
             "提醒时间": None},
            {"节次": "第5-6节", "星期": "周四", "课程名称": "创新创业训练", "地点": "12-614", "教师": "王老师", "时间": "12:40-14:10",
             "提醒时间": None},
            {"节次": "第7-8节", "星期": "周四", "课程名称": "暂无课程安排", "地点": "", "教师": "", "时间": "14:20-15:50",
             "提醒时间": None},
            {"节次": "晚上", "星期": "周四", "课程名称": "分布式数据库", "地点": "12-510", "教师": "范老师", "时间": "18:40-20:55",
             "提醒时间": None},

            {"节次": "第1-2节", "星期": "周五", "课程名称": "工程认知与创新素质培训2班", "地点": "12-501", "教师": "季老师", "时间": "8:00-9:30",
             "提醒时间": None},
            {"节次": "第3-4节", "星期": "周五", "课程名称": "工程认知与创新素质培训2班", "地点": "12-501", "教师": "季老师", "时间": "9:40-11:10",
             "提醒时间": None},
            {"节次": "第5-6节", "星期": "周五", "课程名称": "分布式数据库", "地点": "12-510", "教师": "范老师", "时间": "12:40-14:10",
             "提醒时间": None},
            {"节次": "第7-8节", "星期": "周五", "课程名称": "Hadoop部署实践", "地点": "12-510", "教师": "郑老师", "时间": "14:20-15:50",
             "提醒时间": None},
            {"节次": "晚上", "星期": "周五", "课程名称": "暂无课程安排", "地点": "", "教师": "", "时间": "18:40-20:55",
             "提醒时间": None},

        ]

        # 加载默认课程到日程安排
        self.create_widgets()
        self.load_default_courses()

    def create_widgets(self):
        # 创建日历视图
        self.create_calendar()

        # 按钮放置在中间
        self.add_course_button = tk.Button(self.master, text="添加课程", command=self.add_course)
        self.add_course_button.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

        self.delete_course_button = tk.Button(self.master, text="删除课程", command=self.delete_course)
        self.delete_course_button.grid(row=7, column=2, padx=10, pady=10, sticky="ew")

        self.update_course_button = tk.Button(self.master, text="修改课程", command=self.update_course)
        self.update_course_button.grid(row=7, column=3, padx=10, pady=10, sticky="ew")

        # 新增"课程提示"按钮
        self.set_reminder_button = tk.Button(self.master, text="课程提示", command=self.set_reminder)
        self.set_reminder_button.grid(row=7, column=4, padx=10, pady=10, sticky="ew")

        # 提醒信息栏，显示设置的提醒
        self.reminder_label = tk.Label(self.master, text="提醒信息：", font=('Arial', 12))
        self.reminder_label.grid(row=8, column=0, columnspan=5, padx=10, pady=10)

        self.reminder_text = tk.Text(self.master, height=5, width=60)
        self.reminder_text.grid(row=9, column=0, columnspan=5, padx=10, pady=10)
        self.reminder_text.config(state=tk.DISABLED)  # 不允许直接编辑提醒信息

        # 导出课表按钮
        self.export_button = tk.Button(self.master, text="导出课表为图片", command=self.export_to_image)
        self.export_button.grid(row=7, column=5, padx=10, pady=10, sticky="ew")

        # 让这些按钮在grid中占据更多的空间
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        self.master.grid_columnconfigure(4, weight=1)
    def export_to_image(self):
        """
        导出课表为图片
        schedule_data: 课表数据（例如Pandas DataFrame）
        root: 主窗口
        """
        # 设置屏幕截图区域的偏移值
        x_offset = 31  # 右移 31 像素
        y_offset = 0  # 上移 30 像素

        # 更新坐标
        x1 = root.winfo_rootx() + x_offset  # 左上角 X 坐标，右移 50 像素
        y1 = root.winfo_rooty() + y_offset  # 左上角 Y 坐标，上移 30 像素
        x2 = x1 + root.winfo_width() + 196  # 右下角 X 坐标
        y2 = y1 + root.winfo_height()-70  # 右下角 Y 坐标

        # 截取屏幕区域并保存为图片
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        # 弹出保存图片文件对话框
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not save_path:
            return

        # 保存截图为图片
        screenshot.save(save_path)
        messagebox.showinfo("导出成功", f"课表已成功导出为图片：{save_path}")

    def create_calendar(self):
        """创建一个显示课程安排的日历视图"""
        self.calendar_cells = {}  # 用于存储日历单元格的引用，便于更新

        for i in range(1, 6):  # 周一到周五
            day_label = tk.Label(self.master, text=f"周{i}")
            day_label.grid(row=0, column=i)

        # 修改节次段格式为第1-2节，第3-4节等
        times = [
            "第1-2节", "第3-4节", "第5-6节", "第7-8节", "晚上"
        ]

        for row, time in enumerate(times, start=1):  # 节次段 1-5
            time_label = tk.Label(self.master, text=time)
            time_label.grid(row=row, column=0)

            for col in range(1, 6):  # 周一到周五
                cell = tk.Label(self.master, text="空", width=20, height=3, relief="solid")
                cell.grid(row=row, column=col)
                self.calendar_cells[(row, col)] = cell  # 存储单元格引用


    def load_default_courses(self):
        """加载默认课程数据"""
        for course in self.default_courses:
            new_course = pd.DataFrame([course])
            self.schedule = pd.concat([self.schedule, new_course], ignore_index=True)

        # 更新课表显示
        self.update_calendar()

    def update_calendar(self):
        """更新日历视图显示课程安排"""
        for (row, col), cell in self.calendar_cells.items():
            cell.config(text="空")  # 清空所有单元格

        for index, row in self.schedule.iterrows():
            time_map = {
                "第1-2节": 1,
                "第3-4节": 2,
                "第5-6节": 3,
                "第7-8节": 4,
                "晚上": 5
            }

            day_map = {
                "周一": 1,
                "周二": 2,
                "周三": 3,
                "周四": 4,
                "周五": 5
            }

            time_index = time_map.get(row["节次"], None)
            day_index = day_map.get(row["星期"], None)

            if time_index and day_index:
                cell = self.calendar_cells.get((time_index, day_index))
                if cell:
                    cell.config(text=f"{row['课程名称']}\n{row['地点']}\n{row['教师']} {row['时间']}")

    def add_course(self):
        """添加课程弹窗"""
        course_window = tk.Toplevel(self.master)
        course_window.title("添加课程")

        # 输入框和按钮设置
        time_label = tk.Label(course_window, text="节次：")
        time_label.grid(row=0, column=0)
        time_entry = tk.Entry(course_window)
        time_entry.grid(row=0, column=1)

        day_label = tk.Label(course_window, text="星期：")
        day_label.grid(row=1, column=0)
        day_var = tk.StringVar(value="1")
        day_options = ["周一", "周二", "周三", "周四", "周五"]
        day_menu = tk.OptionMenu(course_window, day_var, *day_options)
        day_menu.grid(row=1, column=1)

        course_name_label = tk.Label(course_window, text="课程名称：")
        course_name_label.grid(row=2, column=0)
        course_name_entry = tk.Entry(course_window)
        course_name_entry.grid(row=2, column=1)

        location_label = tk.Label(course_window, text="地点：")
        location_label.grid(row=3, column=0)
        location_entry = tk.Entry(course_window)
        location_entry.grid(row=3, column=1)

        teacher_label = tk.Label(course_window, text="教师：")
        teacher_label.grid(row=4, column=0)
        teacher_entry = tk.Entry(course_window)
        teacher_entry.grid(row=4, column=1)

        def save_course():
            time = time_entry.get()
            day = day_var.get()
            course_name = course_name_entry.get()
            location = location_entry.get()
            teacher = teacher_entry.get()

            if not (time and course_name and location and teacher):
                messagebox.showerror("错误", "请填写完整的课程信息")
                return

            # 检查节次冲突
            if check_conflict(time, day):
                messagebox.showerror("错误", f"节次冲突：您在{day}的{time}已有课程")
                return

            # 存储课程信息到 DataFrame
            new_course = pd.DataFrame({
                "节次": [time],
                "星期": [day],
                "课程名称": [course_name],
                "地点": [location],
                "教师": [teacher],
                "提醒时间": [None]  # 默认为没有提醒
            })

            # 使用 pd.concat 来代替 append
            self.schedule = pd.concat([self.schedule, new_course], ignore_index=True)
            messagebox.showinfo("成功", "课程添加成功")
            course_window.destroy()

            # 更新课表显示
            self.update_calendar()

        save_button = tk.Button(course_window, text="保存课程", command=save_course)
        save_button.grid(row=5, column=0, columnspan=2)

        def check_conflict(time, day):
            """检查课程是否冲突"""
            conflicting_courses = self.schedule[
                (self.schedule["节次"] == time) & (self.schedule["星期"] == day)
                ]
            return not conflicting_courses.empty  # 如果冲突，返回 True
    def delete_course(self):
        """删除课程弹窗"""
        delete_window = tk.Toplevel(self.master)
        delete_window.title("删除课程")

        # 输入框和按钮设置
        time_label = tk.Label(delete_window, text="节次：")
        time_label.grid(row=0, column=0)
        time_entry = tk.Entry(delete_window)
        time_entry.grid(row=0, column=1)

        day_label = tk.Label(delete_window, text="星期：")
        day_label.grid(row=1, column=0)
        day_var = tk.StringVar(value="1")
        day_options = ["周一", "周二", "周三", "周四", "周五"]
        day_menu = tk.OptionMenu(delete_window, day_var, *day_options)
        day_menu.grid(row=1, column=1)

        def delete_selected_course():
            time = time_entry.get()
            day = day_var.get()

            # 检查节次是否符合规定格式
            valid_times = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "晚上"]
            if time not in valid_times:
                messagebox.showerror("错误", "请填写正确的节次格式")
                return

            # 查找并删除课程
            index_to_delete = self.schedule[
                (self.schedule["节次"] == time) & (self.schedule["星期"] == day)
            ].index

            if index_to_delete.empty:
                messagebox.showerror("错误", "该节次没有课程")
                return

            # 删除课程
            self.schedule.drop(index_to_delete, inplace=True)
            messagebox.showinfo("成功", "课程删除成功")
            delete_window.destroy()

            # 更新课表显示
            self.update_calendar()

        delete_button = tk.Button(delete_window, text="删除课程", command=delete_selected_course)
        delete_button.grid(row=2, column=0, columnspan=2)

    def update_course(self):
        """修改课程弹窗"""
        update_window = tk.Toplevel(self.master)
        update_window.title("修改课程")

        # 输入框和按钮设置
        time_label = tk.Label(update_window, text="节次：")
        time_label.grid(row=0, column=0)
        time_entry = tk.Entry(update_window)
        time_entry.grid(row=0, column=1)

        day_label = tk.Label(update_window, text="星期：")
        day_label.grid(row=1, column=0)
        day_var = tk.StringVar(value="1")
        day_options = ["周一", "周二", "周三", "周四", "周五"]
        day_menu = tk.OptionMenu(update_window, day_var, *day_options)
        day_menu.grid(row=1, column=1)

        course_name_label = tk.Label(update_window, text="课程名称：")
        course_name_label.grid(row=2, column=0)
        course_name_entry = tk.Entry(update_window)
        course_name_entry.grid(row=2, column=1)

        location_label = tk.Label(update_window, text="地点：")
        location_label.grid(row=3, column=0)
        location_entry = tk.Entry(update_window)
        location_entry.grid(row=3, column=1)

        teacher_label = tk.Label(update_window, text="教师：")
        teacher_label.grid(row=4, column=0)
        teacher_entry = tk.Entry(update_window)
        teacher_entry.grid(row=4, column=1)

        def update_selected_course():
            time = time_entry.get()
            day = day_var.get()
            course_name = course_name_entry.get()
            location = location_entry.get()
            teacher = teacher_entry.get()

            # 检查节次是否符合规定格式
            valid_times = ["第1-2节", "第3-4节", "第5-6节", "第7-8节", "晚上"]
            if time not in valid_times:
                messagebox.showerror("错误", "请填写正确的节次格式")
                return

            # 查找并修改课程
            course_to_update = self.schedule[
                (self.schedule["节次"] == time) & (self.schedule["星期"] == day)
            ]

            if course_to_update.empty:
                messagebox.showerror("错误", "该节次没有课程")
                return

            # 修改课程信息
            self.schedule.loc[course_to_update.index, ["课程名称", "地点", "教师"]] = [course_name, location, teacher]
            messagebox.showinfo("成功", "课程修改成功")
            update_window.destroy()

            # 更新课表显示
            self.update_calendar()

        update_button = tk.Button(update_window, text="修改课程", command=update_selected_course)
        update_button.grid(row=5, column=0, columnspan=2)

    def set_reminder(self):
        """设置课程提醒时间"""
        # 选择课程来设置提醒时间
        reminder_window = tk.Toplevel(self.master)
        reminder_window.title("设置课程提醒")

        # 显示所有课程
        course_listbox = tk.Listbox(reminder_window)
        course_listbox.grid(row=0, column=0, rowspan=5)

        for index, row in self.schedule.iterrows():
            course_listbox.insert(tk.END, f"{row['课程名称']} ({row['节次']}) - {row['星期']}")

        time_label = tk.Label(reminder_window, text="提醒时间（分钟）：")
        time_label.grid(row=0, column=1)

        reminder_time_entry = tk.Entry(reminder_window)
        reminder_time_entry.grid(row=1, column=1)

        def save_reminder():
            selected_course_index = course_listbox.curselection()
            if not selected_course_index:
                messagebox.showerror("错误", "请先选择一门课程")
                return

            selected_course = self.schedule.iloc[selected_course_index[0]]
            reminder_time = reminder_time_entry.get()

            if not reminder_time.isdigit():
                messagebox.showerror("错误", "请输入有效的节次（分钟）")
                return

            # 更新提醒时间
            self.schedule.at[selected_course.name, "提醒时间"] = int(reminder_time)
            self.update_reminder_info(f"{selected_course['课程名称']} 将会在开始前 {reminder_time} 分钟提醒你")
            reminder_window.destroy()

        save_button = tk.Button(reminder_window, text="保存提醒", command=save_reminder)
        save_button.grid(row=2, column=1)


    def update_reminder_info(self, reminder_message):
        """更新提醒信息栏"""
        self.reminder_text.config(state=tk.NORMAL)
        self.reminder_text.delete(1.0, tk.END)
        self.reminder_text.insert(tk.END, reminder_message)
        self.reminder_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleManager(root)
    root.mainloop()