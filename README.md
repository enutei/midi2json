# MIDI to JSON Converter
MIDIファイル（.mid）から一部の情報を整列したjsonを作成する。
# 実行方法
``` python midi2json.py <.midファイルのパス>```
# 出力ファイルの構成
## ヘッダーjson
全てのトラックに共通するテンポの情報`tempo_data`、拍子の情報`beat_data`を持つ。

例：
```json
{
    "tempo_data": [
        {"time": 0.0, "bpm": 120.0, "tick": 0},
        {"time": 5.0, "bpm": 140.0, "tick": 960}
    ],
    "beat_data": [
        {"time": 0.0, "beat": [4, 4], "tick": 0},
        {"time": 10.0, "beat": [3, 4], "tick": 1920}
    ]
}
```
`tempo_data`,`beat_data`に共通して、timeはそのテンポ、拍子が設定される時刻を表す。トラック初めからの時間で表され、単位は秒。  
tickは、トラックの初めからその情報が設定されるまでの累積のtickを表す。
tickとはmidoで取得される1拍あたりの分解能。  
`beat_data`のbeatは、これが[n,m]であるときn/m拍子であることを表す。

# トラックごとのjson
`note_data`、`CC_data`、`pitch_bend_data`の３つの情報を持つ。
## note_data
例
```json
"note_data": [
        {
            "time": 0.0,
            "note_length": 2.0,
            "note": "C4",
            "velocity": 70,
            "text": "do1",
            "beat_position": 1.0
        },
        {
            "time": 0.0,
            "note_length": 0.5,
            "note": "G4",
            "velocity": 70,
            "text": "so1",
            "beat_position": 1.0
        }
],
```
- `time`
  そのノートの開始位置を、トラックの初めから数えた時間で表す。単位は秒。
- `note_length`
  そのノートの開始から終了までの長さを表す。単位は秒。
- `note`
  押されたノートを表す。
- `velocity`
  ベロシティを表す。
- `text`
  ノートに添えられたテキストを表す。  
  Cubase上でノートに書きこんだテキストのみ反映されることを確認している。他のDAWで編集されたMIDIデータでの挙動は不明。  
  ![image](https://github.com/user-attachments/assets/9a446171-5d50-4633-8d96-2d1a4d1deea1)
- `beat_position`
  小節内において、そのノートの開始位置が何拍目であるかを示す。  
  小節の開始位置を1拍目とする。拍子がn/mであるとき、最大でn+1を越えない値を取る。
  
## CC_data
例
```json
   "CC_data": {
        "2": [
            {
                "time": 0.0,
                "value": 72
            },
            {
                "time": 0.0,
                "value": 72
            }
        ],
        "7": [
            {
                "time": 0.25,
                "value": 73
            },
            {
                "time": 0.3,
                "value": 75
            }
        ]
  }
```
Control Changeのイベントが、コントロールナンバーごとに管理されている。  
`time`はトラック開始から数えたイベントの時間。単位は秒。  
`value`はCCの値。
## pitch_bend_data
例
```json
    "pitch_bend_data": [
        {
            "time": 0.0,
            "value": -5255
        },
        {
            "time": 0.0,
            "value": -5255
        },
        {
            "time": 0.00625,
            "value": -5145
        },
        {
            "time": 0.0125,
            "value": -5034
        }
```
ピッチベンドのデータを表す。
`time`はトラック開始から数えたイベントの時間。単位は秒。  
`value`はピッチベンドの値。
