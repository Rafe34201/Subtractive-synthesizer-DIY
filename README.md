# Subtractive-synthesizer-DIY


Project: Subtractive synthesizer DIY
Author: 洪睿甫 
Version: 1.0.0

這是一台減法軟體合成器
全程使用python開發，無需安裝VST Plugin等插件即可使用



## Description:

使用midi訊號輸入音源

請先將 MIDI 控制器接上電腦，開啟程式後即可透過圖形化介面，以滑鼠操作參數控制器進行聲音調整。


- 支援五種波形：
  -  Sin / Square / Saw / Triangle / noise

- 內涵四種濾波器：
  - highpass / lowpass / bandpass / bandreject
  - 可調整filtr slope 以及 cutoff 值


- 含有基本Envelope功能：
  - Attack / Decay / Sustain 

 
- 含有 Master 音量調整** 與 Fine Tune 音高微調
 
- 支援 **波形圖** 與 **ADS音量曲線**

*UI預覽:*
<a href="https://ibb.co/LDsz0tn5"><img src="https://i.ibb.co/kVPgG8Q1/2025-04-16-5-20-01.png" alt="2025-04-16-5-20-01" border="0"></a>

---

## 安裝與開啟：

安裝之前需下載以下必要套件，接著直接執行程式就行了：

```python

pip install  numpy  sounddevice  mido  python-rtmidi  matplotlib  scipy

```


**建議在 macOS / Linux 環境執行**，Windows 可能會有聲音延遲的問題

如需使用windows即時播放，建議安裝 ASIO 驅動（如 ASIO4ALL）

---

## 注意事項與使用建議:

1. **請在開啟程式前插入 MIDI 裝置**，程式啟動後再插入裝置將無法識別。
2. 如果變更filter時cutoff滑桿並未顯示，點擊滑桿位置即可。
3. 目前部分參數不支援演奏同時調整，建議調整完參數後再進行彈奏

- 在選擇完裝置後，記得點擊confirm確認裝置
- ADS音量曲線的顯示可能需要幾秒的時間顯示

*Windows 用戶首次安裝 sounddevice / python-rtmidi 套件時，若遇到編譯錯誤，請安裝 Visual C++ Build Tools。*

[安裝網址]：(https://visualstudio.microsoft.com/visual-cpp-build-tools/)




