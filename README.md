# m5stick_wakeonlan
m5stickcでWake On Lanを行いPCを起動させる

# <概要>

![WakeOnLan概要](https://github.com/tktomaru/m5stick_wakeonlan/doc/Slide.jpg)

# <実行に必要なファイル>

## プログラム本体「test_wakeonlan.py」**※必須**
M5StickC・M5StickCPlus用です。（プログラム内で機種自動判別させてます）<br>
M5StickCのプログラム選択モード「APP.List」から起動させる為、親機のM5StickCの「Apps」配下に保存して下さい。<br>

<br>

## 設定ファイル「wakeonlan_set_m.txt」**※必須**

* 起動させたいPCの「MACアドレス」を、「MACADRS:」以降に追記して下さい。※必須です！
* m5stickが接続する、「Wifiの名前」を「WIFI:」以降に、「Wifiのパスワード」を「WIFIPASS:」以降に追記して下さい。※必須です！

<br>

※全てにおいて、空白文字、"などは含まない様にして下さい<br>
修正後、親機のM5StickCのルートに保存して下さい。<br>

<br>

# <使い方>

## 基本動作

- プログラム起動させると、M5StickCの画面に状態が表示されます。「Button Check thread ON」で起動完了です。
- ボタン（電源ボタンじゃない方の側面ボタン）でWake On Lanのパケットを送信します
- Aボタン（M5ロゴの有るボタン）で画面のOn/Offを行います

<br>
