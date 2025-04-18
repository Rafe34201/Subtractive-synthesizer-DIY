import numpy as np
from scipy.signal import square, sawtooth, butter, filtfilt
import sounddevice as sd  # 發出聲音
from sounddevice import OutputStream
import tkinter as tk
from tkinter import ttk
import os.path
import mido
import queue
import threading
import os



_location = os.path.dirname(__file__)

_bgcolor = '#d9d9d9'
_fgcolor = '#000000'
wv = "squ" # 預設波形
filteryes = "no"  # 初始為 "no" 表示沒有啟用濾波器
form = None  # 默認無濾波器

if len(mido.get_input_names()) == 1:
    device = mido.get_input_names()[0]
   
#按下HP LP
def FR2_HLpass(f):
    global form, filteryes
    filteryes = "yes"

    form = f
    top.Label2_1.place(relx=0.725, rely=0.838, height=45, width=114)  #CUTOFF大標
    top.Label2_2.place(relx=0.5, rely=0.257, height=45, width=143)  ##SCOPE大標

 #slope
    top.Radiobutton6.place(relx=0.55, rely=0.365, relheight=0.042, relwidth=0.267)
    top.Radiobutton12.place(relx=0.55, rely=0.459, relheight=0.042, relwidth=0.267)
    top.Radiobutton18.place(relx=0.55, rely=0.554, relheight=0.042, relwidth=0.267)
    top.Radiobutton24.place(relx=0.55, rely=0.649, relheight=0.042, relwidth=0.267)
    top.Radiobutton30.place(relx=0.55, rely=0.743, relheight=0.042, relwidth=0.267)

#cutoff
    top.Scale2_2.place_forget()
    top.Scale2_1.place(relx=0.77, rely=0.216, relheight=0.603 , relwidth=1)
    

#按下Band
def FR2_bandPR(f):
    global form, filteryes
    filteryes = "yes"
    form = f
    top.Label2_1.place(relx=0.725, rely=0.838, height=45, width=114)  #CUTOFF大標
    top.Label2_2.place(relx=0.5, rely=0.257, height=45, width=143)  ##SCOPE大標

#slope
    top.Radiobutton6.place(relx=0.55, rely=0.365, relheight=0.042, relwidth=0.267)
    top.Radiobutton12.place(relx=0.55, rely=0.459, relheight=0.042, relwidth=0.267)
    top.Radiobutton18.place(relx=0.55, rely=0.554, relheight=0.042, relwidth=0.267)
    top.Radiobutton24.place(relx=0.55, rely=0.649, relheight=0.042, relwidth=0.267)
    top.Radiobutton30.place(relx=0.55, rely=0.743, relheight=0.042, relwidth=0.267)

#cutoff
    top.Scale2_1.place_forget()
    top.Scale2_2.place(relx=0.77, rely=0.216, relheight=0.603 , relwidth=1)

def FR2_off():
    global filteryes
    filteryes = "no"
    top.Label2_1.place_forget()
    top.Label2_2.place_forget()
    top.Radiobutton6.place_forget()
    top.Radiobutton12.place_forget()
    top.Radiobutton18.place_forget()
    top.Radiobutton24.place_forget()
    top.Radiobutton30.place_forget()
    top.Scale2_1.place_forget()
    top.Scale2_2.place_forget()


def update_cutoff(value):
    global cutoff
    cutoff = float(value)
    init_filter()


def update_S2_2(value):
    global cutoff
    f_low = value - (value / 2)
    f_high = value + (value / 2)    
    cutoff = [f_low / 22050, f_high / 22050]
    init_filter()


def init_filter():
    global filternumber1, filternumber2
    Wn = cutoff/22050 
    print(top.slope_value.get(), Wn, form)
    filternumber1, filternumber2 = butter(top.slope_value.get(), Wn, form, False)

#各種波型
waveform = {
    "sin": lambda f, t: np.sin(2 * np.pi * f * t),
    "squ": lambda f, t: square(2 * np.pi * f * t),
    "saw": lambda f, t: sawtooth(2 * np.pi * f * t),
    "tri": lambda f, t: sawtooth(2 * np.pi * f * t, width = 0.5),
    "noi": lambda f, t: np.random.uniform(-1.0, 1.0, size=t.shape)
}





amp_A = 0.0  # Attack
amp_D = 0.0  # Decay
amp_S = 1.0  # Sustain

#讀取ADS(R)的值
def update_A(value):
    global amp_A
    amp_A = float(value) * 0.001  #輸入 毫秒 換成 秒
def update_D(value):
    global amp_D 
    amp_D =  float(value) * 0.001  #輸入 毫秒 換成 秒
def update_S(value):
    global amp_S 
    amp_S =  float(value) * 0.01   #輸入 %   換成 0~1

tune = 1.0
gain = 1.0 

#讀取Master的值
def update_master(value):
    global gain
    gain = 10 ** (float(value)/20)



#微調音高
def fine_tune(value):
    global tune 
    tune = 2 ** (float(value) / 1200)


#改圖片和聲音
def show(wv):
    global wave

    t = np.linspace(0, 1, int(1000 * 1), endpoint=False)
    y = waveform[wv](3, t)
    
    # 將波形數據縮放到 Canvas 大小
    y = (y + 2) * (120 / 2)  # 將波形範圍從 [-1, 1] 變為 [0, canvas_height]
    x = np.linspace(0, 380, len(t))
    
    # 清除畫布
    top.Canvas0.delete("all")
    
    # 繪製波形
    for i in range(len(x) - 1):
        top.Canvas0.create_line(x[i], y[i], x[i + 1], y[i + 1], fill="red")

    wave = wv

def draw_adsr_curve():
    
    global amp_A, amp_D, amp_S
    top.Canvas1.delete("all")

    attack = np.logspace(-3, 0, int(amp_A * 44100))
    decay = np.linspace(1, amp_S, int(amp_D * 44100), False)
    sustain = np.ones(244100) * amp_S  # 固定長度的 sustain
    if len(attack) == 0 and len(decay) == 0:
        amp_ADS = sustain
    else:
        amp_ADS = np.concatenate([attack, decay, sustain])
    ads_Db = 20 * np.log10(amp_ADS + 1e-6)  # 避免 log(0)
    ads_t = np.linspace(0, len(amp_ADS) / 44100, len(amp_ADS))
    # 繪製曲線
    
    # 正規化數據到 canvas 尺寸
    x_vals = np.linspace(0, 450, len(ads_t))
    y_vals = amp_ADS / np.max(amp_ADS)
    y_vals = 150 - y_vals * 150

    # 在畫布上繪製直線
    for i in range(len(x_vals) - 1):
        top.Canvas1.create_line(x_vals[i], y_vals[i], x_vals[i+1], y_vals[i+1], fill="red")

    print("Attack:", amp_A, "Decay:", amp_D, "Sustain:", amp_S)

#確認裝置
def confirm_device():
    global device
    print(device_choice.get())
    if device_choice.get() in mido.get_input_names():
        device = device_choice.get()
    else :
        device = mido.get_input_names()[0]
    # 開啟監聽 thread
    threading.Thread(target=midi_listener, daemon=True).start()


#開始監聽
def midi_listener():       
    global device
    with mido.open_input(device) as port:
        for msg in port:
            if msg.type == "note_on" and msg.velocity > 0:
                if msg.note not in is_playing:

                    #按鍵變色
                    if msg.note in key_buttons:
                        key_buttons[msg.note].config(bg="chartreuse")

                    play_note(msg.note)

            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):    

                #按鍵變色                        
                if note_octaves[msg.note] in white_notes:
                    key_buttons[msg.note].config(bg="white")
                else:
                    key_buttons[msg.note].config(bg="gray")

                stop_note(msg.note)
            else:
                continue

#產生介面
top = tk.Tk()
top.geometry("1920x1080")
top.title("Waveform Selector")
top.configure(background=_bgcolor)

#確保有裝置

if len(mido.get_input_names()) == 0 :

    #沒裝置框架
    top.Frame0 = tk.Frame(top, background=_bgcolor, relief='groove', borderwidth=2)
    top.Frame0.place(relx=0.0, rely=0.0, relheight=1, relwidth=1)

    #沒裝置文字
    top.blabla = tk.Label(top.Frame0, text='There is currently no midi device connected', font=("UD Digi Kyokasho NP", 50, "bold"), background=_bgcolor)
    top.blabla.place(relx=0, rely=0, relheight=1, relwidth=1)

    #確認按鈕
    top.confirm = tk.Button(top.Frame0, text='confirm', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command = top.destroy)
    top.confirm.place(relx=0.45, rely=0.605, height=53, width=130)

    top.mainloop()


#框架1
top.Frame1 = tk.Frame(top, background=_bgcolor, relief='groove', borderwidth=2)
top.Frame1.place(relx=0.0, rely=0.0, relheight=0.685, relwidth=0.333)

#波形大標
top.Label1 = tk.Label(top.Frame1, text='OSCILLATOR', font=("UD Digi Kyokasho NP", 24, "bold"), background=_bgcolor)
top.Label1.place(relx=0.282, rely=0.095, height=45, width=283)

#正弦波按鈕
top.sin = tk.Button(top.Frame1, text='sin', background="#d9d9d9", font=("UD Digi Kyokasho NP", 24, "bold"), command=lambda: show("sin"))
top.sin.place(relx=0.140, rely=0.203, height=73, width=170)

#方波按鈕 
top.squ = tk.Button(top.Frame1, text='squ', background="#d9d9d9", font=("UD Digi Kyokasho NP", 24, "bold"), command=lambda: show("squ"))
top.squ.place(relx=0.532, rely=0.203, height=73, width=170)

#鋸齒波按鈕
top.saw = tk.Button(top.Frame1, text='saw', background="#d9d9d9", font=("UD Digi Kyokasho NP", 24, "bold"), command=lambda: show("saw"))
top.saw.place(relx=0.140, rely=0.351, height=73, width=170)

#三角波按鈕
top.tri = tk.Button(top.Frame1, text='tri', background="#d9d9d9", font=("UD Digi Kyokasho NP", 24, "bold"), command=lambda: show("tri"))
top.tri.place(relx=0.532, rely=0.351, height=73, width=170)

#噪音按鈕
top.noi = tk.Button(top.Frame1, text='noise', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), command=lambda: show("noi"))
top.noi.place(relx=0.42, rely=0.52, height=30, width=90)

#波形圖
top.Canvas0 = tk.Canvas(top.Frame1)
top.Canvas0.place(relx=0.140, rely=0.57, height=240, width=380)

#框架2
top.Frame2 = tk.Frame(top, background=_bgcolor, relief='groove', borderwidth=2)
top.Frame2.place(relx=0.333, rely=0.0, relheight=0.685, relwidth=0.333)

#過濾器大標
top.Label2 = tk.Label(top.Frame2, text='FILTERR', font=("UD Digi Kyokasho NP", 24, "bold"), background=_bgcolor)
top.Label2.place(relx=0.375, rely=0.095, height=45, width=163)

#CUTOFF大標
top.Label2_1 = tk.Label(top.Frame2, text='CUTOFF', font=("UD Digi Kyokasho NP", 15, "bold"), background=_bgcolor)

#SCOPE大標
top.Label2_2 = tk.Label(top.Frame2, text='SLOPE', font=("UD Digi Kyokasho NP", 24, "bold"), background=_bgcolor)

#Highpass按鈕
top.HP = tk.Button(top.Frame2, text='Highpass', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command=lambda: FR2_HLpass("highpass"))
top.HP.place(relx=0.109, rely=0.203, height=73, width=170)

#Lowpass按鈕
top.LP = tk.Button(top.Frame2, text='Lowpass', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command=lambda: FR2_HLpass("lowpass"))
top.LP.place(relx=0.109, rely=0.351, height=73, width=170)

#Bandpass按鈕
top.BP = tk.Button(top.Frame2, text='Bandpass', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command=lambda: FR2_bandPR("bandpass"))
top.BP.place(relx=0.109, rely=0.5, height=73, width=170)

#Bandreject按鈕
top.BR = tk.Button(top.Frame2, text='Bandreject', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command=lambda: FR2_bandPR("bandstop"))
top.BR.place(relx=0.109, rely=0.649, height=73, width=170)

#關閉按鈕
top.OFF = tk.Button(top.Frame2, text='OFF', background="#d9d9d9", font=("UD Digi Kyokasho NP", 24, "bold"), command=FR2_off)
top.OFF.place(relx=0.109, rely=0.797, height=73, width=170)

#把slope存到這裡
top.slope_value = tk.IntVar()
top.slope_value.set(value=1)

#6 dB/oct
top.Radiobutton6 = tk.Radiobutton(top.Frame2, anchor='w', justify='left', highlightcolor="#000000", highlightbackground="#d9d9d9", disabledforeground="#a3a3a3", compound='left', activeforeground="black", activebackground="#d9d9d9", text='''6 dB/oct''', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), variable=top.slope_value, value=1)

#12 dB/oct
top.Radiobutton12 = tk.Radiobutton(top.Frame2, anchor='w', justify='left', highlightcolor="#000000", highlightbackground="#d9d9d9", disabledforeground="#a3a3a3", compound='left', activeforeground="black", activebackground="#d9d9d9", text='''12 dB/oct''', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), variable=top.slope_value, value=2)

#18 dB/oct
top.Radiobutton18 = tk.Radiobutton(top.Frame2, anchor='w', justify='left', highlightcolor="#000000", highlightbackground="#d9d9d9", disabledforeground="#a3a3a3", compound='left', activeforeground="black", activebackground="#d9d9d9", text='''18 dB/oct''', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), variable=top.slope_value, value=3)

#24 dB/oct
top.Radiobutton24 = tk.Radiobutton(top.Frame2, anchor='w', justify='left', highlightcolor="#000000", highlightbackground="#d9d9d9", disabledforeground="#a3a3a3", compound='left', activeforeground="black", activebackground="#d9d9d9", text='''24 dB/oct''', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), variable=top.slope_value, value=4)

#30 dB/oct
top.Radiobutton30 = tk.Radiobutton(top.Frame2, anchor='w', justify='left', highlightcolor="#000000", highlightbackground="#d9d9d9", disabledforeground="#a3a3a3", compound='left', activeforeground="black", activebackground="#d9d9d9", text='''30 dB/oct''', background="#d9d9d9", font=("UD Digi Kyokasho NP", 15, "bold"), variable=top.slope_value, value=5)

top.slope_value = tk.IntVar(value=6)

#cutoff調整 highpass lowpass的
top.Scale2_1 = tk.Scale(top.Frame2, from_=20000, to=20, resolution=1.0, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9", font=("UD Digi Kyokasho NP", 9, "bold"), length="446", troughcolor="#c4c4c4", command=update_cutoff)

#cutoff調整band的
top.Scale2_2 = tk.Scale(top.Frame2, from_=20000, to=0, resolution=1.0, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9", font=("UD Digi Kyokasho NP", 9, "bold"), length="446", troughcolor="#c4c4c4", command=update_S2_2)

#框架3
top.Frame3 = tk.Frame(top, background=_bgcolor, relief='groove', borderwidth=2)
top.Frame3.place(relx=0.667, rely=0.0, relheight=0.685, relwidth=0.333)

#ADSR大標
top.Label3 = tk.Label(top.Frame3, text='ENVELOPE', font=("UD Digi Kyokasho NP", 24, "bold"), background=_bgcolor)
top.Label3.place(relx=0.344, rely=0.095, height=45, width=203)

#Attack
top.Attack = tk.Label(top.Frame3, text='Attack(ms)', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.Attack.place(relx=0.11, rely=0.203, height=73, width=170)

#Decay
top.Decay = tk.Label(top.Frame3, text='Decay(ms)', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.Decay.place(relx=0.11, rely=0.351, height=73, width=170)

#Sustain
top.Sustain = tk.Label(top.Frame3, text='Sustain(%)', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.Sustain.place(relx=0.11, rely=0.5, height=73, width=170)

#Attack調整
top.Scale3_1 = tk.Scale(top.Frame3, from_=0.0, to=5000, resolution=1.0, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9"
                        , font=("UD Digi Kyokasho NP", 9, "bold"), length="266", orient="horizontal", troughcolor="#c4c4c4", command=update_A)
top.Scale3_1.place(relx=0.423, rely=0.212, relheight=0.062, relwidth=0.416)

#Decay調整
top.Scale3_2 = tk.Scale(top.Frame3, from_=0.0, to=5000, resolution=1.0, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9"
                        , font=("UD Digi Kyokasho NP", 9, "bold"), length="266", orient="horizontal", troughcolor="#c4c4c4", command=update_D)
top.Scale3_2.place(relx=0.423, rely=0.360, relheight=0.062, relwidth=0.416)

#Sustain調整
top.Scale3_3 = tk.Scale(top.Frame3, from_=0.0, to=100.0, resolution=1.0, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9"
                        , font=("UD Digi Kyokasho NP", 9, "bold"), length="266", orient="horizontal", troughcolor="#c4c4c4", command=update_S)
top.Scale3_3.place(relx=0.423, rely=0.509, relheight=0.062, relwidth=0.416)
top.Scale3_3.set(100.0)

#圖表2
top.Canvas1 = tk.Canvas(top.Frame3, highlightbackground="#d9d9d9", highlightcolor="#000000", insertbackground="#000000", selectbackground="#d9d9d9", selectforeground="black", background="#F0F0F0", borderwidth="2", relief="groove")
top.Canvas1.place(relx=0.125, rely=0.635, relheight=0.270, relwidth=0.704)

#顯示圖表2按鈕
top.SHOW = tk.Button(top.Frame3, text='SHOW', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"), command=draw_adsr_curve)
top.SHOW.place(relx=0.36, rely=0.905, height=53, width=130)
show("squ")

#框架4
top.Frame4 = tk.Frame(top, background=_bgcolor, relief='groove', borderwidth=2)
top.Frame4.place(relx=0.0, rely=0.685, relheight=0.33, relwidth=1)

#master
top.Master = tk.Label(top.Frame4, text='Master(db)', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.Master.place(relx=0.05, rely=0, height=19, width=170)

#Master調整
top.Scale4_1 = tk.Scale(top.Frame4, from_ = -30.0, to=6, resolution=0.1, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9"
                        , font=("UD Digi Kyokasho NP", 9, "bold"), length="266", orient="horizontal", troughcolor="#c4c4c4", command=update_master)
top.Scale4_1.place(relx=0.03, rely=0.1, relheight=0.9, relwidth=0.15)

#Device
top.Device = tk.Label(top.Frame4, text='Device', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.Device.place(relx=0.77, rely=0, height=19, width=170)

#Device選擇
device_choice = ttk.Combobox(top.Frame4, values=mido.get_input_names())
device_choice.place(relx=0.75, rely=0.1, relheight=0.072, relwidth=0.15)

#Device確認
top.conf = tk.Button(top.Frame4, text = "confirm", background="#d9d9d9", font=("UD Digi Kyokasho NP", 16, "bold"), command=confirm_device)
top.conf.place(relx=0.905, rely=0.08, relheight=0.12, relwidth=0.05)

#Fine Tune
top.fine = tk.Label(top.Frame4, text='Fine tune(cents)', background="#d9d9d9", font=("UD Digi Kyokasho NP", 18, "bold"))
top.fine.place(relx=0.43, rely=0, height=19, width=170)

#FineTune調整
top.Scale4_2 = tk.Scale(top.Frame4, from_ = -50, to=50, resolution=1, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="#000000", activebackground="#d9d9d9", background="#d9d9d9"
                        , font=("UD Digi Kyokasho NP", 9, "bold"), length="266", orient="horizontal", troughcolor="#c4c4c4", command=fine_tune)
top.Scale4_2.place(relx=0.41, rely=0.1, relheight=0.9, relwidth=0.15)







#下方鍵盤
top.keyboard_frame = tk.Frame(top, background="black")
top.keyboard_frame.place(relx=0.00, rely=0.8148, relwidth=1, relheight=0.1852)

# 虛擬鍵盤按鈕字典
key_buttons = {}
note_octaves = {}

def create_virtual_keyboard(frame):
    key_width = 28.15
    start_note = 24   # MIDI Note 24 = C-1
    end_note = 108   # MIDI Note 108 = C8
    white_key_height = 200
    black_key_height = 100
    white_key_index = 0
    global white_notes
    white_notes = [0, 2, 4, 5, 7, 9, 11]  # C D E F G A B
    black_notes = [1, 3, 6, 8, 10]        # C# D# F# G# A#

    white_key_positions = {}
    
    # 先放白鍵
    for note in range(start_note, end_note+1):
        note_in_octave = note % 12
        note_octaves[note] = note_in_octave
        if note_in_octave in white_notes:
            x_pos = white_key_index * (key_width + 2)

            
            btn = tk.Frame(frame, bg='white', relief="flat", bd=10)
            btn.place(x=x_pos, y=0, width=key_width, height=white_key_height)
            key_buttons[note] = btn
            white_key_positions[note] = x_pos
            white_key_index += 1



    # 再放黑鍵（放在對應白鍵中間）
    for note in range(start_note, end_note+1):
        note_in_octave = note % 12
        if note_in_octave in black_notes:
            if note_in_octave == 1:   # C#
                left_note = note - 1
            elif note_in_octave == 3: # D#
                left_note = note - 1
            elif note_in_octave == 6: # F#
                left_note = note - 1
            elif note_in_octave == 8: # G#
                left_note = note - 1
            elif note_in_octave == 10:# A#
                left_note = note - 1
            else:
                continue

            if left_note in white_key_positions:
                x_pos = white_key_positions[left_note] + key_width * 0.7
                btn = tk.Frame(frame, bg='gray', relief="raised", bd=3.5)
                btn.place(x=x_pos, y=0, width=key_width*0.6, height=black_key_height)
                key_buttons[note] = btn

create_virtual_keyboard(top.keyboard_frame)



#製造聲音波形
def make_sound(note):
    #pitch改變
    f = (442 * 2 ** ((note - 69) / 12)) * tune
    AD_wave_T = np.linspace(0, (amp_A+amp_D),int((amp_A+amp_D) * 44100), False )    
    ad_wave = waveform[wave](f, AD_wave_T)
    attack = np.logspace(-3, 0, int(amp_A * 44100) ) 
    decay = np.linspace(1, amp_S, int(amp_D * 44100))
    amp_AD = np.concatenate([attack, decay])
    if len(ad_wave) != len(amp_AD):
        ad_wave = ad_wave[:min(len(ad_wave), len(amp_AD))]    
    ad_wave = ad_wave * amp_AD

    #處理sustain
    S_wave_T = np.linspace(0, 20, int(44100 * 20), False)
    S_wave =waveform[wave](f, S_wave_T) * amp_S
    sound = np.concatenate([ad_wave, S_wave])

    #加入濾波
    if filteryes == "yes" :
        sound = filtfilt(filternumber1, filternumber2, sound)

    #處理master
    sound = sound * gain
    return sound
    


#放開按鍵後逐漸消失的波
#之後有機會再修改，現在這個函示不會不呼叫

'''
def make_R_wave(note):
    f = 440 * 2 ** ((note - 69) / 12)
    R_wave_T = np.linspace(0, amp_R, int(44100 * amp_R), False)
    R_wave =waveform[wave](f, R_wave_T)
    if filteryes == "yes":
        R_wave = filtfilt(filternumber1, filternumber2, R_wave)
    release = np.logspace(0, -3, int(amp_R * 44100)) * amp_S
    return R_wave * release
'''
#創一個字典收錄正在按的按鍵



#創一個字典收錄正在按的按鍵
is_playing = {}

note_queues = {}

# 音訊 callback
def audio_callback(outdata, frames, time, status, q):
    try:
        data = q.get_nowait()
    except queue.Empty:
        outdata[:] = np.zeros((frames, 1), dtype=np.float32)
        return

    if len(data) < frames:
        out = np.zeros((frames, 1), dtype=np.float32)
        out[:len(data)] = data.reshape(-1, 1)
        outdata[:] = out
    else:
        outdata[:] = data[:frames].reshape(-1, 1)
        if len(data) > frames:
            q.put(data[frames:])

# 每個 note 的播放邏輯
def play_note(note):
    q = queue.Queue()
    audio = make_sound(note)
    q.put(audio.astype(np.float32))
    note_queues[note] = q
    stream = sd.OutputStream(callback=lambda *args: audio_callback(*args, q=q),
                             samplerate=44100, channels=1)
    stream.start()
    is_playing[note] = stream


# 停止播放
def stop_note(note):
    if note in is_playing:
        stream = is_playing[note]
        stream.stop()
        stream.close()
        del is_playing[note]
        del note_queues[note]

# GUI 主迴圈放最後一行
top.mainloop()
