from mido import MidiFile, MidiTrack, Message, MetaMessage
import mido

# 定义乐器编号及名称对应关系
instruments = {
    '高音萨克斯': 64,
    '八音盒': 10,
    '合成特效5 (亮音)': 100,
    '弦乐合奏2': 49,
    '排笛': 75,
    '钟琴': 9,
    '合成特效1 (雨)': 96,
    '合成柔音 (暖音)': 89,
    '钢弦吉他': 25,
    '电贝斯 (指奏)': 33
}

# 简谱音符与 MIDI 音符的映射
note_mapping = {
    '1': 60,  '2': 62,  '3': 64,  '4': 65,  '5': 67,  '6': 69,  '7': 71,
    '1̇': 72, '2̇': 74, '3̇': 76, '4̇': 77, '5̇': 79, '6̇': 81, '7̇': 83,
    '1̨': 48, '2̨': 50, '3̨': 52, '4̨': 53, '5̨': 55, '6̨': 57, '7̨': 59,
    '0': None
}

# 全局参数
bpm = 72
beat_ticks = 480
mid = MidiFile(ticks_per_beat=beat_ticks)

def add_global_settings(track):
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

def parse_note_duration(sheet_music, i):
    duration = beat_ticks  # 默认一拍
    advance = 0
    if i+1 < len(sheet_music):
        next_char = sheet_music[i+1]
        if next_char == '.':
            duration = int(beat_ticks * 1.5)
            advance = 1
        elif next_char == '-':
            advance = 1
            while i+1+advance < len(sheet_music) and sheet_music[i+1+advance] == '-':
                advance += 1
            duration = beat_ticks * (advance + 1)
    return duration, advance

def parse_sheet_music(sheet_music, instrument_name, channel=0, volume=64):
    track = MidiTrack()
    mid.tracks.append(track)
    add_global_settings(track)
    track.append(Message('program_change', program=instruments[instrument_name], time=0, channel=channel))
    track.append(Message('control_change', control=7, value=volume, channel=channel))

    time_accumulator = 0
    i = 0
    while i < len(sheet_music):
        char = sheet_music[i]
        # 修复：添加缺失的右括号
        if char in note_mapping or (i+1 < len(sheet_music) and sheet_music[i+1] in ('̇', '̨')):
            if i+1 < len(sheet_music) and sheet_music[i+1] in ('̇', '̨'):
                note = char + sheet_music[i+1]
                i += 1
            else:
                note = char
                
            midi_note = note_mapping.get(note)
            duration, advance = parse_note_duration(sheet_music, i)
            
            if midi_note:
                track.append(Message('note_on', note=midi_note, velocity=volume, time=time_accumulator, channel=channel))
                track.append(Message('note_off', note=midi_note, velocity=volume, time=duration, channel=channel))
                time_accumulator = 0
                i += advance
            else:
                time_accumulator += duration
        elif char in (' ', '|'):
            pass
        elif char == '-':
            duration, advance = parse_note_duration(sheet_music, i)
            time_accumulator += duration
            i += advance
        i += 1
    return track

# ================= 完整歌曲结构（约4分钟）=================
# 前奏（8小节）
intro_sax = "3 5 6 5 3 2 1 1|2 3 5 5 3 2 2 2|1 1 2 3 5 3|2 2 1 2 3 2|"*2
intro_strings = "3̨ 3̨ 5̨ 5̨|6̨ 6̨ 5̨ 5̨|3̨ 3̨ 2̨ 2̨|1̨ 1̨ 2̨ 2̨|"*2

# 主歌部分（16小节）
verse_guitar = ("3 5 6 5 3 2 1 1|2 3 5 5 3 2 2 2|1 1 2 3 5 3|2 1 1 0 0 0|")*4
verse_bass = ("1̨ 1̨ 1̨ 1̨|2̨ 2̨ 2̨ 2̨|3̨ 3̨ 3̨ 3̨|5̨ 5̨ 5̨ 5̨|")*4

# 预副歌（8小节）
pre_chorus = "5 3 2 1 2 3 5 5|3 2 1 1 2 3 5 3|5 3 2 1 2 3 5 5|3 2 1 1 2 1 1 0|"*2

# 副歌（16小节）
chorus_flute = ("5̇ 3̇ 2̇ 1̇ 2̇ 3̇ 5̇ 5̇|3̇ 2̇ 1̇ 1̇ 2̇ 3̇ 5̇ 3̇|")*4
chorus_strings = ("3 3 5 5 6 6 5 5|3 3 2 2 1 1 2 2|")*8

# 间奏（8小节）
interlude_box = ("5 3 2 1 2 3 5 5|3 2 1 1 2 3 5 3|5 3 2 1 2 3 5 5|3 2 1 1 2 1 1 0|")*2

# 尾奏（8小节）
outro = "3 5 6 5 3 2 1 1|2 3 5 5 3 2 2 2|1 1 2 3 5 3|2 1 1 - - -|0 0 0 0|"*2

# ================= 音轨编排 =================
# 前奏
parse_sheet_music(intro_sax, '高音萨克斯', volume=90)
parse_sheet_music(intro_strings, '弦乐合奏2', volume=60)

# 主歌
parse_sheet_music(verse_guitar, '钢弦吉他', channel=1, volume=70)
parse_sheet_music(verse_bass, '电贝斯 (指奏)', channel=2, volume=80)

# 预副歌
parse_sheet_music(pre_chorus, '合成柔音 (暖音)', channel=3, volume=75)

# 副歌
parse_sheet_music(chorus_flute, '排笛', channel=4, volume=95)
parse_sheet_music(chorus_strings, '弦乐合奏2', channel=5, volume=85)

# 间奏
parse_sheet_music(interlude_box, '八音盒', channel=6, volume=88)

# 尾奏
parse_sheet_music(outro, '钟琴', channel=7, volume=70)
parse_sheet_music(outro.replace("3","5̇"), '合成特效1 (雨)', channel=8, volume=60)  # 高八度重复

# ================= 打击乐优化 =================
drum_instruments = {'低音鼓':35, '军鼓':38, '踩镲':42}
drum_track = MidiTrack()
mid.tracks.append(drum_track)
add_global_settings(drum_track)

# 简化节奏模式（每小节）
basic_beat = [
    ('低音鼓', [0]),          # 强拍
    ('军鼓', [beat_ticks*2]), # 第二拍后半
    ('踩镲', [beat_ticks*1, beat_ticks*3])  # 弱拍
]

for section in range(8):  # 全曲共8个段落
    for drum_type, positions in basic_beat:
        for pos in positions:
            # 添加段落间的过渡空拍
            if section > 0 and pos == 0:
                drum_track.append(Message('note_on', note=drum_instruments[drum_type], 
                                velocity=100, time=beat_ticks//2, channel=9))
            else:
                drum_track.append(Message('note_on', note=drum_instruments[drum_type], 
                                velocity=100, time=0, channel=9))
            drum_track.append(Message('note_off', note=drum_instruments[drum_type], 
                            velocity=100, time=beat_ticks//2, channel=9))

mid.save('hou_lai_de_wo_men_final.mid')