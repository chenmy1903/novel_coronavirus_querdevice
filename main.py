import requests
import time
import webbrowser
import json
import sys
import tkinter.messagebox as tkMessageBox
import tkinter as tk
from tkinter import ttk
DEBUG = False  # 是否启用DEBUG
ShowTraceback = True  # 是否显示错误


class get_InFo(object):
    """爬虫类"""

    def __init__(self):
        super().__init__()
        self.data = {}

    def get_all(self, get_fo="中国"):
        number = format(time.time() * 100, '.0f')  # 当前日期时间戳
        url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%s' % number
        self.datas = json.loads(requests.get(url=url).json()['data'])
        self.UpdateTime = self.datas['lastUpdateTime']  # 更新时间
        self.get_fo = get_fo
        self.all_confirm = {}
        self.all_dead = {}
        self.all_heal = {}
        for contry in self.datas['areaTree']:
            if contry['name'] == self.get_fo:
                for province in contry['children']:
                    self.data[province['name']] = {}  # 省份名称
                    for city in province['children']:
                        self.data[province['name']][city['name']] = {
                            '确诊': str(city['total']['confirm']),
                            '死亡':
                            str(city['total']['dead']), '治愈':
                            str(city['total']['heal'])}
                        self.all_confirm[province['name']] = \
                            self.all_confirm.get(province['name'], 0) + \
                            int(city['total']['confirm'])
                        self.all_dead[province['name']] = \
                            self.all_dead.get(province['name'], 0) + \
                            city['total']['dead']
                        self.all_heal[province['name']] = \
                            self.all_heal.get(province['name'], 0) + \
                            city['total']['heal']
        self.alls = {"确诊": self.all_confirm,
                     "死亡": self.all_dead,
                     "治愈": self.all_heal}
        # 市的名称，确诊、死亡、治愈的人数
        return self.UpdateTime, self.data, self.alls


InFo = get_InFo()


class MainWindow(object):
    """主窗口类"""

    def __init__(self):
        """初始化"""
        super().__init__()
        self.InFo = get_InFo().get_all()
        self.root = tk.Tk()  # 初始化屏幕
        self.root.protocol("WM_DELETE_WINDOW", self.ExitWarning)
        self.root.title("疫情信息")  # 设置题目
        self.root.minsize(400, 365)
        self.Frame = tk.Frame(self.root)
        self.updateTime = tk.Label(self.Frame)
        self.message = ""
        self.message1 = []
        self.reloadButton = ttk.Button(
            self.Frame, text="更新数据", command=self.get_fo)
        self.countFrame = tk.LabelFrame(self.Frame, text='请输入要查询的地区:')
        self.countScrollbar = tk.Scrollbar(self.root)
        self.countEntry = tk.Entry(self.countFrame)
        self.countButton = ttk.Button(
            self.Frame, text="确认", command=self.get_message)
        self.InFoList = ttk.Treeview(self.root)  # 设置列表
        self.openHtmlButton = ttk.Button(
            self.root, text="打开原网址", command=self.openHtml)

    def get_fo(self, event=0):
        """获取信息"""
        f = open("疫情数据.csv", 'w')
        self.updateTime.config(text="上一次腾讯更新时间:{}".format(self.InFo[0]))
        self.delButton(self.InFoList)
        self.InFo = get_InFo().get_all()
        f.write(self.InFo[0]+'\n')
        for x in self.data:
            for y in self.data[x]:
                self.InFoList.insert("", tk.END, text=x, values=(y, self.data[x][y]["确诊"],
                                                                 self.data[x][y]["治愈"],
                                                                 self.data[x][y]["死亡"]))
                f.write("省/直辖市:{},地区:{},确诊:{},治愈:{},死亡:{}\n".format(x, y, self.data[x][y]["确诊"],
                                                                    self.data[x][y]["治愈"],
                                                                    self.data[x][y]["死亡"]))
        f.close()

    def openHtml(self):
        """打开原网址"""
        webbrowser.open("https://news.qq.com/zt2020/page/feiyan.htm#/global")

    def get_message(self, event=0):
        """获取信息"""
        self.message = self.countEntry.get()
        try:
            self.message_confirm = self.InFo[2]['确诊'][self.message]
            self.message_dead = self.InFo[2]['死亡'][self.message]
            self.message_heal = self.InFo[2]['治愈'][self.message]
        except KeyError:
            tkMessageBox.showwarning(
                '提示', '没有叫\"{}\"的省/直辖市。'.format(self.message))
        else:
            tkMessageBox.showinfo("{}的人数".format(self.message),
                                  "确诊:{}\n治愈:{}\n死亡:{}\n".format(self.message_confirm,
                                                                 self.message_heal,
                                                                 self.message_dead))

    def ExitWarning(self):
        res = tkMessageBox.askokcancel("提示", "要退出吗？")
        if res:
            sys.exit()
        return

    def delButton(self, tree):
        x = tree.get_children()
        for item in x:
            tree.delete(item)

    def get_start(self):
        """准备开始"""
        self.data = self.InFo[1]
        self.updateTime.pack()
        self.InFoList.config(columns=(
            "省/直辖市", "地区", "确诊人数", "治愈人数", "死亡人数"))
        self.InFoList.heading("#0", text="省/直辖市")
        self.InFoList.heading("#1", text="地区")
        self.InFoList.heading("#2", text="确诊人数")
        self.InFoList.heading("#3", text="治愈人数")
        self.InFoList.heading("#4", text="死亡人数")
        self.InFoList.config(yscrollcommand=self.countScrollbar.set)
        self.countScrollbar.config(command=self.InFoList.yview)
        self.get_fo()
        self.Frame.pack(fill=tk.X, anchor=tk.N)
        self.reloadButton.pack()
        self.openHtmlButton.pack(fill=tk.X, anchor=tk.S, side=tk.BOTTOM)
        self.countScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.countFrame.pack(fill=tk.X, anchor=tk.NW)
        self.countEntry.pack(fill=tk.X, anchor=tk.NW)
        self.countButton.pack(fill=tk.X, anchor=tk.S)
        self.countEntry.bind("<Return>", self.get_message)
        self.InFoList.pack(fill=tk.BOTH, expand=True)

    def mainloop(self, n: int = 0):
        """进入主循环"""
        self.root.mainloop(n)


class tests(object):
    """测试类"""

    def __init__(self):
        """初始化"""
        super().__init__()

    def main(self):
        """主函数的拓展"""
        self.Window = MainWindow()
        self.Window.get_start()
        self.Window.mainloop()

    def debug(self):
        """启动DEBUG"""
        try:
            try:

                from ptpython.repl import embed
            except:
                pass
            else:
                embed(globals(), locals())
                return
            try:
                import ipdb
            except:
                pass
        except:
            import pdb
            pdb.set_trace()
        else:
            ipdb.set_trace()


def main():
    """主函数"""
    test = tests()
    if DEBUG:
        test.debug()
    else:
        test.main()


if __name__ == "__main__":
    """运行主函数"""
    if ShowTraceback:
        main()
    else:
        try:
            main()  # 错误检测
        except:
            pass
