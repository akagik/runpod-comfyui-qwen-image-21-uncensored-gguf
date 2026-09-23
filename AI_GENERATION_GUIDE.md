# 別のAI向け完全ガイド: Qwen-Image-2.1 Uncensored GGUFをManagerから生成する

この文書は、別のAIエージェントがユーザーから画像生成指示と素材を受け取り、
RunPod Comfy Managerへ安全に投入し、PNGをローカルへ回収するための実行手順です。

## 0. 固定する対象

このスタックでは次だけを使用します。

```text
Model profile:
qwen-image-2.1-uncensored-gguf-q4km

T2I workflow:
qwen-image-2.1-uncensored-gguf-t2i v1

Image Edit workflow:
qwen-image-2.1-uncensored-gguf-edit v1

RunPod template:
d4detb1p14
```

モデル構成は以下です。

```text
Transformer: qwen-image-2.1-UC-Q4_K_M.gguf
Text encoder: qwen3vl_8b_int8_convrot.safetensors
VAE: qwen_image_2.1_vae_bf16.safetensors
```

`qwen-image-2.1-official-bf16`、旧Qwen、別GGUF、NVFP4へ置き換えないでください。
生成は必ずRunPod Comfy Managerを通します。ComfyUIの`/prompt`やRunPod APIへ
直接生成を投入しません。

## 1. 依頼を受けたAIが最初に確認すること

次をユーザーの依頼から確定します。

1. T2IかImage Editか
2. 縦横比または解像度
3. 生成枚数
4. seedを固定するか
5. 参照画像の役割と優先順位
6. 保存先

用途の選択基準:

| 目的 | workflow |
|---|---|
| テキストだけから新しい画像を作る | `qwen-image-2.1-uncensored-gguf-t2i` v1 |
| 1枚を指示で編集する | `qwen-image-2.1-uncensored-gguf-edit` v1 |
| キャラと衣装、背景、ポーズなど複数画像を参照する | `qwen-image-2.1-uncensored-gguf-edit` v1 |

Image Editでは1枚目が編集対象です。2枚目以降は追加参照です。

```text
referenceImages[0] = <image1> = 編集対象・出力比率の基準
referenceImages[1] = <image2> = 追加参照1
referenceImages[2] = <image3> = 追加参照2
...
referenceImages[9] = <image10>
```

各画像の役割をプロンプトに明記してください。「参照画像をいい感じに使う」のような
曖昧な指定は避けます。

## 2. CLIの場所

```bash
RCMCTL='/Applications/RunPod Comfy Manager.app/Contents/MacOS/rcmctl'
PROJECT='/Users/kohei/Projects/runpod-workspace/runpod-comfyui-qwen-image-21-uncensored-gguf'
```

以後の例ではこの2変数を設定済みとします。

## 3. Managerとworkflowの事前確認

### Manager health

```bash
"$RCMCTL" health --json
```

期待値:

```json
{"name":"runpod-comfy-manager","status":"ok","version":"0.20.5"}
```

接続できない場合はアプリを起動します。

```bash
open -a 'RunPod Comfy Manager'
```

### workflow定義

```bash
"$RCMCTL" workflow qwen-image-2.1-uncensored-gguf-t2i 1 --json
"$RCMCTL" workflow qwen-image-2.1-uncensored-gguf-edit 1 --json
```

両方の`modelProfile.id`が次であることを確認します。

```text
qwen-image-2.1-uncensored-gguf-q4km
```

見つからない場合だけ、組み込みworkflowを登録し、Managerアプリを再起動します。

```bash
"$RCMCTL" workflow-install-builtins --json
```

## 4. READY Podの確認

```bash
"$RCMCTL" pods --json
```

`comfy.status`が`READY`のPodを使います。現在のPod IDを固定情報として文書へ
書き込まないでください。Podを作り直すたびにIDが変わります。

候補だけを短く表示する例:

```bash
"$RCMCTL" pods --json | python3 -c '
import json, sys
data = json.load(sys.stdin)
pods = data if isinstance(data, list) else data.get("pods", [])
print(json.dumps([
    {"id": p.get("id"), "name": p.get("name"), "comfy": p.get("comfy")}
    for p in pods
    if p.get("comfy", {}).get("status") == "READY"
], ensure_ascii=False, indent=2))
'
```

互換Podが1台だけなら投入時の`--preferred-pod-id`は省略できます。特定Podへ確実に
送る場合は、毎回取得したIDを指定します。

Managerの自動レンタルはこのスタックでは設定していません。READY Podがない場合、
AIは勝手にPodを作成したりprovisioning policyを変更したりせず、最新GPU料金と保存費用を
提示してユーザーの明示承認を得ます。

## 5. Markdownの共通仕様

ファイルはUTF-8のMarkdownです。先頭のYAML front matterにworkflowとパラメータを置き、
本文の`## プロンプト`直下に`text`コードブロックを置きます。

````markdown
---
formatVersion: 1
workflowId: WORKFLOW_ID
workflowVersion: 1
outputRoot: ./outputs
values:
  parameter: value
---
# 人間が読める依頼名

## プロンプト

```text
ここに生成プロンプトを書く。
```
````

重要事項:

- `workflowId`と`workflowVersion`は必ず両方書く。
- `values`のキーはworkflow定義のキーと完全一致させる。
- `outputRoot`はCLIの`--output-root`で上書きできる。
- 参照画像の相対パスはMarkdownファイルのあるディレクトリを基準に解決される。
- AIによる自動実行では、出力先と参照画像に絶対パスを使うと取り違えが少ない。
- Markdownのファイル名が出力PNGの基本名になる。
- 同名出力がある場合は新しい名前を使う。意図的に置換する場合だけ
  `--overwrite-existing`を付ける。

## 6. T2I Markdown

### パラメータ

| key | 必須 | 既定値 | 意味 |
|---|---:|---:|---|
| `width` | yes | 1024 | 出力幅 |
| `height` | yes | 1024 | 出力高さ |
| `seed` | yes | 42 | 再現用seed |
| `steps` | yes | 25 | 推論steps |
| `cfg` | yes | 1 | baselineは1 |
| `negativePrompt` | no | 空 | 通常は省略または空 |

幅と高さは16の倍数を使います。検証済みの16:9は`1536x864`です。
高解像度とstep増加は生成時間とVRAMを増やします。最初は25 steps、CFG 1を使います。

### 完全な例

ファイル例: `requests/t2i/scene-cafe-001.md`

````markdown
---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-t2i
workflowVersion: 1
outputRoot: ./outputs
values:
  width: 1536
  height: 864
  seed: 42
  steps: 25
  cfg: 1
---
# Visual novel cafe character

## プロンプト

```text
Photorealistic visual novel character asset set in Japan.
An exceptionally beautiful adult Japanese woman, age 20, looking directly at the camera.
Frame her from head to mid-thigh. She stands naturally in a softly lit Tokyo cafe.
Realistic skin texture, detailed eyes, natural individual hair strands, cinematic window light.
No text, logo, watermark, subtitles, speech bubbles, borders, or game UI.
```
````

## 7. 1枚参照Image Edit Markdown

背景変更、衣装変更、表情、ポーズ変更など、元画像1枚を編集するときに使います。

ファイル例: `requests/edit/character-night-room.md`

````markdown
---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-edit
workflowVersion: 1
outputRoot: ./outputs
values:
  referenceImages:
    - /absolute/path/to/character.png
  resolution: 1024
  seed: 42
  steps: 25
  cfg: 1
---
# Character background edit

## プロンプト

```text
Use <image1> as the image to edit.
Keep the adult woman's identity, facial features, hairstyle, body proportions,
photographic style, and camera framing from <image1>.
Change the background to a luxurious nighttime hotel room with warm practical lighting.
No text, logo, watermark, subtitles, or game UI.
```
````

## 8. 複数参照Image Edit Markdown

`referenceImages`は1〜10枚です。1枚目が編集対象で、出力比率も1枚目を基準にします。

### キャラ + 衣装 + ポーズ + 背景の例

````markdown
---
formatVersion: 1
workflowId: qwen-image-2.1-uncensored-gguf-edit
workflowVersion: 1
outputRoot: ./outputs
values:
  referenceImages:
    - /absolute/path/to/base-canvas.png
    - /absolute/path/to/character.png
    - /absolute/path/to/outfit.png
    - /absolute/path/to/pose.png
    - /absolute/path/to/background.png
  resolution: 1024
  seed: 42
  steps: 25
  cfg: 1
---
# Multi-reference visual novel scene

## プロンプト

```text
Edit <image1> as the base canvas and preserve its aspect ratio.
Use the adult character identity, face, and hairstyle from <image2>.
Use the outfit design and fabric details from <image3>.
Use the body pose and camera framing from <image4>.
Use the location, lighting direction, and background design from <image5>.
Create one coherent photorealistic image with natural anatomy and consistent lighting.
No text, logo, watermark, subtitles, speech bubbles, borders, or game UI.
```
````

`resolution`は1枚目の比率を保つ総ピクセル予算で、既定1024、最大2048です。
出力ピクセル寸法はQwenの画像bucketへ調整される場合があります。検証では16:9入力に
`resolution: 1024`を指定した結果が`1376x768`になりました。

## 9. プロンプト設計

T2Iでは次の順序が安定します。

1. 用途と画風
2. 成人であること、人物属性
3. 構図とカメラ
4. ポーズと表情
5. 衣装
6. 場所と光
7. 禁止するUI・文字

Editでは各参照の役割を先に宣言します。

```text
Keep identity from <image1>.
Use the outfit from <image2>.
Use only the pose from <image3>; do not copy that person's identity.
Use the background and lighting from <image4>.
```

顔や人物を維持したい場合は、`identity`だけでなく`facial features`、`hairstyle`、
`body proportions`、`camera framing`のうち保持したいものを列挙します。

CFGは通常1です。negative promptを積極的に使う構成ではないため、最初の生成では
`negativePrompt`を省略します。

## 10. 生成前の検証

出力フォルダを先に作ります。

```bash
REQUEST_MD="$PROJECT/requests/t2i/scene-cafe-001.md"
OUTPUT_DIR="$PROJECT/results/manual/scene-cafe-001"
mkdir -p "$OUTPUT_DIR"
```

### 構文・ファイル存在確認

```bash
"$RCMCTL" validate "$REQUEST_MD" --json
```

`valid: true`、`failed: 0`を確認します。Editでは参照画像が解決できない場合、この段階で
修正します。

### 実行内容のプレビュー

プレビューは生成を行わず、課金も開始しません。

```bash
"$RCMCTL" markdown-preview \
  --source-path "$REQUEST_MD" \
  --output-root "$OUTPUT_DIR" \
  --preferred-pod-id CURRENT_POD_ID \
  --json
```

次を確認します。

- `status`が`READY`
- workflow IDとversion
- prompt全文
- width / heightまたはresolution
- seed / steps / cfg
- 参照画像の順番と絶対パス
- 出力先

## 11. 単発生成の投入

```bash
"$RCMCTL" markdown-submit \
  --source-path "$REQUEST_MD" \
  --output-root "$OUTPUT_DIR" \
  --preferred-pod-id CURRENT_POD_ID \
  --json
```

返されたJSONのジョブ`id`を記録します。投入後は再送信せず、そのIDを監視します。

```bash
"$RCMCTL" watch JOB_ID --interval 5 --json
```

`status: COMPLETED`になり、`localOutput`がPNGを指していれば完了です。

途中状態は次の順に進みます。

```text
QUEUED -> UPLOADING -> RUNNING -> DOWNLOADING -> COMPLETED
```

ジョブ単体の確認:

```bash
"$RCMCTL" job JOB_ID --json
```

`RUNNING`や`DOWNLOADING`中に同じ依頼を再投入しないでください。

## 12. seedやstepsを一時的に上書きする

Markdownを変更せず、一回だけ値を変える場合は`--set KEY=JSON`を使います。

```bash
"$RCMCTL" markdown-submit \
  --source-path "$REQUEST_MD" \
  --output-root "$OUTPUT_DIR" \
  --preferred-pod-id CURRENT_POD_ID \
  --set seed=43 \
  --set steps=40 \
  --json
```

文字列を上書きする場合、値はJSON文字列として引用します。

## 13. バリエーション生成

同じMarkdownから複数seedを生成します。

```bash
"$RCMCTL" markdown-preview \
  --source-path "$REQUEST_MD" \
  --output-root "$OUTPUT_DIR" \
  --preferred-pod-id CURRENT_POD_ID \
  --variations 4 \
  --json

"$RCMCTL" markdown-submit \
  --source-path "$REQUEST_MD" \
  --output-root "$OUTPUT_DIR" \
  --preferred-pod-id CURRENT_POD_ID \
  --variations 4 \
  --json
```

必ずpreviewに表示された4つの出力名を確認してからsubmitします。

## 14. フォルダ一括生成

`source-root`配下の`.md`を再帰的に処理します。

```bash
BATCH_ROOT="$PROJECT/requests/batch-001"
BATCH_OUTPUT="$PROJECT/results/batch-001"
mkdir -p "$BATCH_OUTPUT"

"$RCMCTL" batch-preview \
  --source-root "$BATCH_ROOT" \
  --output-root "$BATCH_OUTPUT" \
  --preferred-pod-id CURRENT_POD_ID \
  --json
```

previewの`invalid: 0`と全出力先を確認後に投入します。

```bash
"$RCMCTL" batch-submit \
  --source-root "$BATCH_ROOT" \
  --output-root "$BATCH_OUTPUT" \
  --preferred-pod-id CURRENT_POD_ID \
  --json
```

一部だけ実行する場合は、`source-root`からの相対パスを`--include`で指定します。

```bash
"$RCMCTL" batch-preview \
  --source-root "$BATCH_ROOT" \
  --output-root "$BATCH_OUTPUT" \
  --include chapter01/scene001.md \
  --include chapter01/scene002.md \
  --preferred-pod-id CURRENT_POD_ID \
  --json
```

## 15. モデル常駐の扱い

T2IとEditは同じモデルsignatureを使います。PodのComfyUIは`--cache-classic`で起動し、
同じPodが稼働している間はロード済みモデルを再利用します。

- ジョブごとにComfyUIを再起動しない。
- ジョブごとにモデルを解放しない。
- T2IとEditの切替だけでPodを再作成しない。
- 別モデルprofileへ切り替えるときはモデル入替が起き得る。

A40検証では生成後に約13.50GiBが常駐し、2枚参照Editのピークは19.11GiBでした。

## 16. よくある問題

### モデル一覧にGGUFがない

Manager APIでworkflowを確認します。

```bash
"$RCMCTL" workflow qwen-image-2.1-uncensored-gguf-t2i 1 --json
```

APIにはあるが画面にない場合、UIが古い一覧を保持しています。Managerアプリを再起動します。

### `READY` Podがない

自動レンタルは`mode: off`です。生成だけを依頼されたAIはPodを無断作成しません。
Pod作成依頼がある場合も、最新のGPU在庫、時間単価、ストレージ費用、自動停止条件を提示し、
ユーザーの明示承認を得てからTemplate `d4detb1p14`を使います。

### ジョブがQUEUEDのまま

`rcmctl pods --json`で互換Podの`comfy.status`を確認します。指定した
`--preferred-pod-id`が古いPod IDなら、現在のREADY Pod IDに直します。

### 参照画像が見つからない

相対パスの基準はMarkdownの場所です。`validate`と`markdown-preview`が表示する
絶対パスを確認します。

### 出力が既に存在する

Markdown名または出力フォルダを変えます。同じファイルを意図的に置き換える場合だけ
`--overwrite-existing`を使います。

### Editで人物が変わりすぎる

プロンプトに保持対象を具体的に書きます。

```text
Keep the identity, facial features, eye shape, hairstyle, body proportions,
photographic style, and camera framing from <image1>.
```

ポーズ参照の人物の顔を移したくない場合は次を加えます。

```text
Use only the pose and framing from <image2>. Do not copy that person's identity,
face, hairstyle, outfit, or background.
```

## 17. 完了報告に含める内容

別のAIは生成後、最低限次を報告します。

```text
Workflow ID / version:
Pod ID:
Resolution:
Steps / CFG / seed:
Reference image count and roles:
Job ID:
Status:
Generation time:
Absolute local output path:
```

失敗時は、工程、ジョブID、Managerの`errorJson`、再投入の有無を報告します。
原因を確認する前に同じジョブを繰り返し送信しません。

## 18. 別のAIへ渡す依頼テンプレート

以下を生成内容と一緒に渡せば、この文書に沿って実行できます。

```text
最初に次のガイドを全て読んでください:
/Users/kohei/Projects/runpod-workspace/runpod-comfyui-qwen-image-21-uncensored-gguf/AI_GENERATION_GUIDE.md

RunPod Comfy Managerを使い、
qwen-image-2.1-uncensored-gguf-q4kmだけで生成してください。
まずMarkdownを作成し、validateとmarkdown-previewの結果を確認してから投入してください。
生成を直接ComfyUI APIへ投入しないでください。
同じジョブを二重送信しないでください。
READY Podがない場合は勝手にPodを借りず、最新費用を提示してください。

依頼内容:
- 種別: T2I または Image Edit
- 画像の目的:
- 解像度または縦横比:
- 参照画像と各画像の役割:
- seed:
- 枚数:
- 保存先:
```
