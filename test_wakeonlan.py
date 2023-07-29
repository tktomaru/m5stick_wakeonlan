from m5stack import *
import machine
import gc
import utime
import ure
import uos
import _thread
import wifiCfg
import ntptime

import socket
import struct

# 変数宣言

Disp_mode               = 3     # グローバル
lcd_mute                = False # グローバル
data_mute               = False # グローバル
m5type                  = 0     # グローバル [0:M5StickC、1: M5StickCPlus]

FONT_TYPE               = lcd.FONT_DejaVu40

MAC_ADRS                = None
WIFI                    = None
WIFI_PASS               = None
DEFAULT_PORT            = 7


# @cinimlさんのファーム差分吸収ロジック
class AXPCompat(object):
    def __init__(self):
        if( hasattr(axp, 'setLDO2Vol') ):
            self.setLDO2Vol = axp.setLDO2Vol
        else:
            self.setLDO2Vol = axp.setLDO2Volt

axp = AXPCompat()


# 表示OFFボタン処理スレッド関数
def buttonA_wasPressed():
    global lcd_mute

    if lcd_mute :
        lcd_mute = False
    else :
        lcd_mute = True

    if lcd_mute == True :
        axp.setLDO2Vol(0)   #バックライト輝度調整（OFF）
    else :
        axp.setLDO2Vol(2.7) #バックライト輝度調整（中くらい）


# 表示切替ボタン処理スレッド関数
def buttonB_wasPressed():    
    draw_lcd()

# 表示モード切替時の枠描画処理関数
def draw_lcd():
    lcd.clear()
    
    #try:
    # MAC_ADRS = "00:50:56:36:ED:D8"
    send_magic_packet(MAC_ADRS)
 
    #except BaseException:
    #    output_LCD("送信エラー")

# wisun_set_m.txtの存在/中身チェック関数
def wisun_set_filechk():
    global MAC_ADRS
    global WIFI
    global WIFI_PASS

    scanfile_flg = False
    for file_name in uos.listdir('/flash') :
        if file_name == 'wisun_set_m.txt' :
            scanfile_flg = True

    if scanfile_flg :
        print('>> found [wisun_set_m.txt] !')
        with open('/flash/wisun_set_m.txt' , 'r') as f :
            for file_line in f :
                filetxt = file_line.strip().split(':')
                if filetxt[0] == 'MACADRS' :
                    MAC_ADRS = str(filetxt[1])
                    print('- MAC_ADRS: ' + str(MAC_ADRS))
                elif filetxt[0] == 'WIFI' :
                    WIFI = str(filetxt[1])
                    print('- WIFI: ' + str(WIFI))
                elif filetxt[0] == 'WIFIPASS' :
                    WIFI_PASS = str(filetxt[1])
                    print('- WIFI_PASS: ' + str(WIFI_PASS))
                        
        if len(MAC_ADRS) == 17: # NGならプログラム停止
            scanfile_flg = True
        else :
            print('>> [wisun_set_m.txt] Illegal!!')
            scanfile_flg = False
            
    else :
        print('>> no [wisun_set_m.txt] !')
    return scanfile_flg

def output_LCD(text):
    print(text)
    lcd.clear()
    lcd.setRotation(Disp_mode)
    lcd.print(text, 0, 0, lcd.WHITE)
    # lcd.print(text)
 
def send_magic_packet(addr):
    # create socket
    output_LCD("0")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    output_LCD("1")
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    output_LCD("2")
    # parse address
    mac_ = addr.upper().replace("-", "").replace(":", "")
    output_LCD("3")
    if len(mac_) != 12:
        output_LCD("invalid MAC address format: {}".format(addr))
    buf_ = b'f' * 12 + (mac_ * 20).encode()
    # encode to magic packet payload
    magicp = b''
    for i in range(0, len(buf_), 2):
        magicp += struct.pack('B', int(buf_[i:i + 2], 16))
    output_LCD("4")

    # send magic packet
    s.sendto(magicp, ('255.255.255.255', DEFAULT_PORT))
    output_LCD(addr)
        
# メインプログラムはここから（この上はプログラム内関数）
try :                                               # ネットワーク不通発生などで例外エラー終了されない様に try except しとく
    # M5StickC/Plus機種判定
    if lcd.winsize() == (80,160) :
        m5type = 0
        # FONT_7seg  FONT_Arial12  FONT_Arial16  FONT_Comic  FONT_Default  FONT_DefaultSmall 
        # FONT_DejaVu18  FONT_DejaVu24  FONT_DejaVu40  FONT_DejaVu56  FONT_DejaVu72  
        # FONT_Minya  FONT_Small  FONT_Tooney  FONT_UNICODE  FONT_Ubuntu
        FONT_TYPE               = lcd.FONT_DejaVu40
        Disp_mode               = 1
        output_LCD('>> M5Type = M5StickC')
    if lcd.winsize() == (136,241) :
        m5type = 1
        FONT_TYPE               = lcd.FONT_DejaVu40
        Disp_mode               = 1
        output_LCD('>> M5Type = M5StickCPlus')
    utime.sleep(2)


    # 基本設定ファイル[wisun_set_m.txt]のチェック 無い場合は例外エラー吐いて終了する
    if not wisun_set_filechk() :
        lcd.print('err!! Check [wisun_set_m.txt] and restart!!', 0, 0, lcd.WHITE)
        raise ValueError('err!! Check [wisun_set_m.txt] and restart!!')

    output_LCD('Wifi start!!')
    utime.sleep(1)
    wifiCfg.doConnect(WIFI,WIFI_PASS)
    if wifiCfg.wlan_sta.isconnected():
        output_LCD('Wifi connect!!')
    else:
        machine.reset()
        
    utime.sleep(2)
    lcd.clear()
    output_LCD('>> WiFi init OK')

    print('heapmemory= ' + str(gc.mem_free()))

    # 画面初期化
    axp.setLDO2Vol(2.7) #バックライト輝度調整（中くらい）
    output_LCD('Disp init OK')
    utime.sleep(0.5)

    # ボタン検出スレッド起動
    btnA.wasPressed(buttonA_wasPressed)
    btnB.wasPressed(buttonB_wasPressed)
    output_LCD('Button Check thread ON')
    utime.sleep(0.5)

    # メインループ
    while True:
        utime.sleep(1)
        gc.collect()
except :
    output_LCD('wakeonlan  ERR!')
    machine.reset()
