import requests
import parsel
import base64

'''
//***
常见搜索关键字
组播头
udproxy平台 Server: udpxy
单播
华为平台 Server: HMS Download Service
酒店
智慧光迅平台(广东公司) body="ZHGXTV"
/ZHGXTV/Public/json/live_interface.txt
http://ip:port/hls/1/index.m3u8
智慧桌面 智能KUTV(陕西公司) body="/iptv/live/zh_cn.js"
http://ip:port/tsfile/live/0001_1.m3u8
华视美达 华视私云(浙江公司) body="华视美达"
http://ip:port/newlive/live/hls/1/live.m3u8
地面波串流
Tvheadend平台 Server: HTS/tvheadend
***//
'''


# houzui = ['/ZHGXTV/Public/json/live_interface.txt','/iptv/live/1000.json?key=txiptv']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
}

result_url = 'https://fofa.info/result?qbase64='

# 地区字典
sheng_dic = {
    '北京':'BeiJing','上海':'ShangHai','天津':'TianJin','重庆':'ChongQing','安徽':'AnHui','福建':'FuJian',
    '广东':'GuangDong','广西':'GuangXi','贵州':'GuiZhou','甘肃':'GanSu',
    '海南':'HaiNan','河北':'HeBei','河南':'HeNan','黑龙江':'HeiLongJiang','湖北':'HuBei','湖南':'HuNan',
    '吉林':'JiLin','江苏':'JiangSu','江西':'JiangXi','辽宁':'LiaoNing','内蒙古':'NeiMengGu','宁夏':'NingXia',
    '青海':'QingHai','陕西':'ShaanXi','山西':'ShanXi','山东':'ShanDong','四川':'SiChuan','台湾':'TaiWan',
    '西藏':'XiZang','新疆':'XinJiang','云南':'YunNan','浙江':'ZheJiang',
}

# 提取有效地址
def get_url(shenfeng):
    tt = f'"iptv/live/zh_cn.js" && country="CN" && region="{sheng_dic[shenfeng]}"'
    dd = str(base64.b64encode(tt.encode("utf-8")), "utf-8")

    urls = [] # 创建一个空字典储存url

    response = requests.get(url=result_url+dd, headers=headers)
    selector = parsel.Selector(response.text)
    el_checkbox = selector.xpath('//div[@class="el-checkbox-group"]/div')
    print('===========***===========分**隔**行===========***===========')
    print(f'{shenfeng}从网页上获取到{len(el_checkbox)}个地址,开始验证有效性！！')
    for hsxa_meta in el_checkbox:
        url = hsxa_meta.xpath('div/div/span[@class="hsxa-host"]').css('a::attr(href)').get()
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 如果返回的状态码不是2xx，会抛出HTTPError异常
            print(f"{url} 可以访问，状态码: {response.status_code}")
            urls.append(url)
        except requests.RequestException as e:
            print(f"{url} 访问失败，错误信息: {e}")
            pass

    return urls

# 定义m3u获取函数
def get_m3u(shenfeng,index,url):
    file_path = f'./jiudian/{shenfeng}_{index}.m3u'
    link = '/iptv/live/1000.json?key=txiptv'

    m3u_lis =[]
    # 写入表头
    m3u_lis.append('#EXTM3U\n')

    response = requests.get(url=url+link, headers=headers)
    if response:
        if 'data' in response.text:
            json_data = response.json()['data']
            for index in range(len(json_data)):
                channel_name = json_data[index]['name']
                channel_url = url+json_data[index]['url']
                m3u_lis.append(f'#EXTINF:-1,{channel_name}\n{channel_url}\n')
            m3u_string =''.join(m3u_lis)

            with open(file_path,'w',encoding='utf-8')  as m3u:
                m3u.write(m3u_string)

            print(f'文件已保存至{file_path}')

def main():
    for shenfeng in sheng_dic:
        shenfeng_url = get_url(shenfeng)
        if shenfeng_url:
            print(f'共提取到{len(shenfeng_url)}个有效地址！！')
            for index in range(len(shenfeng_url)):
                get_m3u(shenfeng,index,shenfeng_url[index])
        else:
            print(f'{shenfeng}未提取到有效地址！！')

# =================================**代码测试区**================================= #
shenfeng = '江西'

shenfeng_url = get_url(shenfeng)
if shenfeng_url:
    print(f'共提取到{len(shenfeng_url)}个有效地址！！')
    for index in range(len(shenfeng_url)):
        get_m3u(shenfeng,index,shenfeng_url[index])
else:
    print(f'{shenfeng}未提取到有效地址！！')

exit()
# =================================**代码执行区**================================= #    
if __name__ == "__main__" :
    main()