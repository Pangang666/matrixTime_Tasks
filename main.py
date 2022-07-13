import os
import json
import numpy as np
from tensorboardX import SummaryWriter
import matplotlib.pyplot as plt
import markdown
import pdfkit

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

class Statistical():
    def Convergence_Time(self, data, threshold, threshold_step, episodes, steps, nums, jsonPath, fileName):   # data：数据源，threshold：阈值，episodes：轨迹条数， steps：每条轨迹的步数，nums：数据点个数
        # 此函数返回是一个json字符串，其中最外层是17个数据的，中间层是每个数据点有8条轨迹，然后最里层是一个key-value，key表示索引，value表示值
        json_episode = []
        json_num = []
        json_done_episode = []
        json_done_num = []
        for i in range(nums):
            for j in range(episodes):
                res = []
                for k in range(steps):
                    res.append(data[j][k][i])
                # print(res)
                # 现在开始判断跟阈值的大小
                index = 0   # 用来记录第一次小于阈值的横坐标位置
                m = 0
                while m < len(res):
                    if abs(res[m]) <= float(threshold):
                        n = m + 1
                        index = m
                        while n < len(res):
                            if res[n] >= float(threshold):
                                m = n
                                break
                            else:
                                n += 1
                        if n == len(res):
                            break
                    else:
                        m += 1
                # 下面开始返回json数据
                if m == steps and index == 0:     # 这里表示所有轨迹都不符合条件
                    tmp = {}
                else:
                    tmp_done = {"index": index, "value": res[index]}    # 记录收敛索引和值
                    if index > threshold_step:    # 收敛时索引大于设置的索引限制时
                        tmp = {}
                    else:
                        tmp = {"index": index, "value": res[index]}
        ##############################################
                tmp_done_episode = {
                    'episode': j,
                    'value': tmp_done
                }
        ##############################################
                tmp_episode = {
                    'episode': j,
                    'value': tmp
                }
                json_episode.append(tmp_episode)
                json_done_episode.append(tmp_done_episode)    # 保存收敛点位置
            tmp_num = {
                'num': i,
                'value': json_episode
            }
            tmp_done_num = {
                'num': i,
                'value': json_done_episode
            }
            json_episode = []
            json_num.append(tmp_num)
            json_done_episode = []
            json_done_num.append(tmp_done_num)
        ##############################################

        f = open(jsonPath + 'Convergence_Time/' + fileName + '.json', 'w')
        b = json.dumps(json_num)
        f.write(b)
        f.close()
        f_done = open(jsonPath + 'Convergence_Time/' + fileName + '_done.json', 'w')
        b_done = json.dumps(json_done_num)
        f_done.write(b_done)
        f_done.close()
        return "返回结果以json格式成功保存至json/Convergence_Time文件目录"

    def Over_Shoot(self, data, threshold, episodes, steps, nums, jsonPath, fileName):
        # 此函数返回是一个json字符串，其中最外层是17个数据的，中间层是每个数据点有8条轨迹，然后最里层是一个key-value，key表示索引，value表示值
        json_episode = []
        json_num = []
        for i in range(nums):
            for j in range(episodes):
                res = []
                for k in range(steps):
                    res.append(data[j][k][i])
                over = []  # 用来存储波峰的下标
                for m in range(1, len(res) - 1):
                    if res[m] > res[m - 1] and res[m] > res[m + 1]:
                        over.append(m)
                r = []
                if len(over) != 0:
                    for o in over:
                        if float(res[o]) >= threshold:  # 轨迹的第一个波峰如果超过或者等于阈值
                            r.append(o)
                            break
                # 下面开始返回json数据
                if len(r) != 0:
                    tmp = {"index": r[0], "value": res[r[0]]}
                else:
                    tmp = {}
                tmp_episode = {
                    'episode': j,
                    'value': tmp
                }
                json_episode.append(tmp_episode)

            tmp_num = {
                'num': i,
                'value': json_episode
            }
            json_episode = []
            json_num.append(tmp_num)
        f = open(jsonPath + 'Over_Shoot/' + fileName + '.json', 'w')
        b = json.dumps(json_num)
        f.write(b)
        f.close()
        return "返回结果以json格式成功保存至json/Over_Shoot文件目录"

    def Data_to_tensorboard(self, data, episodes, steps, nums, curr_path, fileName):
        writer = SummaryWriter(curr_path + '/logs/' + fileName + '/')
        for i in range(nums):
            for j in range(episodes):
                res = []
                for k in range(steps):
                    res.append(data[j][k][i])
                for m in range(len(res)):
                    writer.add_scalars('nums'+str(i), {'episode' + str(j): res[m]}, m)
        writer.close()
        return "可视化完成！"

    def Save_img(self, data, imagePath, episodes, steps, nums):
        for i in range(nums):
            for j in range(episodes):
                res = []
                for k in range(steps):
                    res.append(data[j][k][i])
                plt.title('第' + str(i) + '个数据中' + str(episodes) + '条轨迹的图像')
                # label = 'Episode ' + str(j)
                # plt.plot(np.arange(len(res)), res, label=label)
                plt.plot(np.arange(len(res)), res)
                plt.xlabel('Number of Steps')
                plt.ylabel('Value')
            # plt.legend()
            # plt.show()   # 展示图像
            imageName = 'Nums' + str(i) + '.png'
            print("正在保存第" + str(i) + '数据点的图像')
            plt.savefig(imagePath + imageName)  # 保存至本地
            plt.close()
        return "图像保存成功！"

    def make_md_str(self, data, episodes, steps, nums, fileName, imagePath, markdownPath, jsonPath):
        md_info = ''                            # 定义一个空的字符串，用来存储markdown文本
        md_info += '<div align="center"><table style="border-collapse: collapse;">\n<thead style="border: 1px solid black;">\n<tr>\n<th align="center"><b>统计指标：收敛时间</b></th>\n<th align="center"></th>\n<th align="center"></th>\n<th align="center"></th>\n<th align="center"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td align="center"style="border: 1px solid black;">数据点编号</td>\n<td align="center"style="border: 1px solid black;">曲线总条数</td>\n<td align="center"style="border: 1px solid black;">合格条数</td>\n<td align="center"style="border: 1px solid black;">不合格率</td>\n<td align="center"style="border: 1px solid black;">不合格是哪几条</td>\n</tr>\n'
        # 收敛时间指标
        with open(jsonPath + 'Convergence_Time/' + fileName + '.json', 'r', encoding='utf8') as f:
            res = json.load(f)

        with open(jsonPath + 'Convergence_Time/' + fileName + '_done.json', 'r', encoding='utf8') as f:    # 这里是为了后面把不合格轨迹的具体位置在plot图上标出来
            res_done = json.load(f)

        for i in range(nums):      # 0-17
            qualified_num = 0  # 记录合格轨迹条数
            unqualified_str_ct = ''  # 记录不合格轨迹是哪几条
            for j in range(episodes):
                if len(res[i]['value'][j]['value']) != 0 and res[i]['value'][j]['value']['index'] != steps-1:    # 这里表示收敛时间点小于阈值并且索引值不为最大时，并且res不为空时，代表有合格轨迹
                    qualified_num += 1
                else:
                    unqualified_str_ct += str(j)
                    unqualified_str_ct += ' '

                    # 保存每个数据点中不合格的轨迹图像
                    plot_data = []
                    for k in range(steps):
                        plot_data.append(data[j][k][i])
                    plt.title('第' + str(i) + '个数据中不合格轨迹的图像')
                    plt.plot(np.arange(len(plot_data)), plot_data)
                    plt.xlabel('Number of Steps')
                    plt.ylabel('Value')
                    # 再把每条不合格轨迹的具体收敛点在什么位置给标出来
                    # print('res_done[i][j]:', res_done[i]['value'][j]['value'])
                    plt.scatter(res_done[i]['value'][j]['value']['index'], res_done[i]['value'][j]['value']['value'])
                    imageName = 'Nums' + str(i) + '.png'
                    plt.savefig(imagePath + 'unqualified/Convergence_Time/' + imageName)  # 保存至本地
            plt.close()

            if len(unqualified_str_ct) != 0:
                unqualified_str_ct = '轨迹:' + unqualified_str_ct
            else:
                unqualified_str_ct += '无'

            unqualified_per = round(((episodes - qualified_num)/episodes)*100, 2)    # 不合格率,保留两位小数
            md_info += '<tr>\n<td align="center"style="border: 1px solid black;">'+'nums'+str(i)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(episodes)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(qualified_num)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(unqualified_per)+'%</td>\n<td align="center"style="border: 1px solid black;">'+unqualified_str_ct+'</td>\n</tr>\n'
        md_info += '</tbody>\n</table></div>\n\n'

        md_info += '<div align="center" style="margin-top:5px;"><table style="border-collapse: collapse;">\n<thead style="border: 1px solid black;">\n<tr>\n<th align="center"><b>统计指标：过冲点</b></th>\n<th align="center"></th>\n<th align="center"></th>\n<th align="center"></th>\n<th align="center"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td align="center"style="border: 1px solid black;">数据点编号</td>\n<td align="center"style="border: 1px solid black;">曲线总条数</td>\n<td align="center"style="border: 1px solid black;">合格条数</td>\n<td align="center"style="border: 1px solid black;">不合格率</td>\n<td align="center"style="border: 1px solid black;">不合格是哪几条</td>\n</tr>\n'
        # 过冲点指标
        with open(jsonPath + 'Over_Shoot/' + fileName + '.json', 'r', encoding='utf8') as f:
            res = json.load(f)
        for i in range(nums):
            qualified_num = 0        # 记录合格轨迹条数
            unqualified_str_os = ''  # 记录不合格轨迹是哪几条
            for j in range(episodes):
                if len(res[i]['value'][j]['value']) != 0 and res[i]['value'][j]['value']['index'] != steps-1:
                    qualified_num += 1
                else:
                    unqualified_str_os += str(j)
                    unqualified_str_os += ' '

                    # 保存每个数据点中不合格的轨迹图像
                    plot_data = []
                    for k in range(steps):
                        plot_data.append(data[j][k][i])
                    plt.title('第' + str(i) + '个数据中不合格轨迹的图像')
                    plt.plot(np.arange(len(plot_data)), plot_data)
                    plt.xlabel('Number of Steps')
                    plt.ylabel('Value')
                    imageName = 'Nums' + str(i) + '.png'
                    plt.savefig(imagePath + 'unqualified/Over_Shoot/' + imageName)   # 保存至本地
            plt.close()


            if len(unqualified_str_os) != 0:
                unqualified_str_os = '轨迹:' + unqualified_str_os
            else:
                unqualified_str_os += '无'
            unqualified_per = round(((episodes - qualified_num)/episodes)*100, 2)    # 不合格率,保留两位小数
            md_info += '<tr>\n<td align="center"style="border: 1px solid black;">'+'nums'+str(i)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(episodes)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(qualified_num)+'</td>\n<td align="center"style="border: 1px solid black;">'+str(unqualified_per)+'%</td>\n<td align="center"style="border: 1px solid black;">'+unqualified_str_os+'</td>\n</tr>\n'
        md_info += '</tbody>\n</table></div>\n\n'

        # 所有数据点轨迹图像
        md_info += '# 所有数据点轨迹图像\n'
        datanames = os.listdir(imagePath)
        for i in range(len(datanames)-1):
            md_info += '## 第' + str(i) + '个数据点轨迹图\n'
            md_info += '<div align=center><img src="/home/qyw/PythonCodes/SecondTask/images/' + fileName + '/Nums' + str(i) + '.png' + '"> </div>\n\n'

        # 所有数据点不合格轨迹的图像
        datanames = os.listdir(imagePath + 'unqualified/Convergence_Time/')
        if len(datanames) != 0:
            md_info += '# 所有数据点收敛时间不合格轨迹的图像\n'
            index = []
            for i in range(len(datanames)):
                start = 4
                end = datanames[i].index('.')
                index.append(int(datanames[i][start:end]))
            index.sort()
            for i in range(len(index)):
                md_info += '## 第' + str(index[i]) + '个数据点收敛时间不合格轨迹的图像\n'
                md_info += '<div align=center><img src="' + imagePath + 'unqualified/Convergence_Time/Nums' + str(index[i]) + '.png' + '"> </div>\n\n'


        datanames = os.listdir(imagePath + 'unqualified/Over_Shoot/')
        if len(datanames) != 0:
            md_info += '# 所有数据点过冲指标不合格轨迹的图像\n'
            index = []
            for i in range(len(datanames)):
                start = 4
                end = datanames[i].index('.')
                index.append(int(datanames[i][start:end]))
            index.sort()
            for i in range(len(index)):
                md_info += '## 第' + str(index[i]) + '个数据点过冲指标不合格轨迹的图像\n'
                md_info += '<div align=center><img src="' + imagePath + 'unqualified/Over_Shoot/Nums' + str(index[i]) + '.png' + '"> </div>\n\n'

        # print(md_info)
        with open(markdownPath, 'w') as f:         # 将字符串写入md文件
            f.write(md_info)
        f.close()
        return "Markdown文件保存至markdown文件目录下"

    def markdown_to_pdf(self, markdownPath, htmlPath, pdfPath):
        str = "<meta charset='utf-8'>\n"
        with open(markdownPath, "r", encoding="utf-8") as f:
            text = f.read()
        html = markdown.markdown(text)
        with open(htmlPath, "w", encoding="utf-8") as f:
            f.write(str)
            f.write(html)
        f.close()
        pdfkit.from_file(htmlPath, pdfPath)
        return "pdf文件已保存至pdf文件目录"

if __name__ == '__main__':
    # 1. 先导入数据
    curr_path = os.path.dirname(__file__)
    fileName = 'trajs'
    data = np.load(curr_path + '/data/' + fileName + '.npy')
    jsonPath = curr_path + '/json/'
    imagePath = curr_path + '/images/' + fileName + '/'
    markdownPath = curr_path + '/markdown/' + fileName + '.md'
    htmlPath = curr_path + '/html/' + fileName + '.html'
    pdfPath = curr_path + '/pdf/' + fileName + '.pdf'

    print("*******************************************")
    print("1. 收敛时间\n2. 过冲点\n3. Tensorboard可视化\n4. 图像保存至本地\n5. 形成Markdown文档")
    print("*******************************************\n")
    print("请输入你要选择的操作:")
    choose = input()

    episodes = data.shape[0]
    steps = data.shape[1]
    nums = data.shape[2]

    if choose == '1':
        print("请输入阈值:")
        threshold = float(input())
        print("请输入收敛时间step:")
        threshold_step = int(input())
        result = Statistical().Convergence_Time(data, threshold, threshold_step, episodes, steps, nums, jsonPath, fileName)         # 统计收敛时间
    elif choose == '2':
        print("请输入阈值:")
        threshold = float(input())
        result = Statistical().Over_Shoot(data, threshold, episodes, steps, nums, jsonPath, fileName)               # 统计过冲点
    elif choose == '3':
        result = Statistical().Data_to_tensorboard(data, episodes, steps, nums, curr_path, fileName)                # Tensorboard可视化轨迹图像
    elif choose == '4':
        result = Statistical().Save_img(data, imagePath, episodes, steps, nums)  # 将轨迹图像保存至本地
    elif choose == '5':
        result = Statistical().make_md_str(data, episodes, steps, nums, fileName, imagePath, markdownPath,jsonPath)   # 形成规范的markdown文本
        print(result)
        result = Statistical().markdown_to_pdf(markdownPath, htmlPath, pdfPath)  # 将markdown形成pdf报告形式
    else:
        result = "您输入的值有误，请重新输入"

    print(result)
