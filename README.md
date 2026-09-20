# LatentSync API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=latentsync-dev&utm_content=readme-badge&utm_term=tier-a)

LatentSync is ByteDance's audio-conditioned latent diffusion model for lip synchronisation: give it a face and a speech track and it produces video whose mouth movements match the audio. This package is a LatentSync-class lip sync API client for Python: one `pip install` gives you audio-driven talking-head generation as an HTTPS call, with no diffusion checkpoints to download and no GPU to provision.

You get a blocking `run()` that returns the video URL, a submit-and-poll path for batches, webhook delivery on completion, and one runtime dependency (`httpx`). It is built for localisation, e-learning and marketing pipelines that need a speaking face from a portrait and an audio file without owning inference hardware.

> **Try it now:** [https://synexa.ai/explore/veed/fabric-1.0](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=latentsync-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About LatentSync](#about-latentsync)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No GPU to provision.** LatentSync denoises every frame with a Stable Diffusion U-Net conditioned on Whisper audio features; usable throughput needs a data-centre class card. The hosted endpoint runs on managed GPUs.
- **No environment to maintain.** No PyTorch/CUDA matching, no Whisper, VAE, U-Net and SyncNet checkpoints to fetch, no face-detection dependencies to compile. Install, set a key, call `run()`.
- **No cold starts on your side.** A lip sync pipeline loads several models before the first frame; keeping them warm costs money around the clock. Here you pay per prediction only.
- **Known price per clip.** `veed/fabric-1.0` is $0.08 per run; `heygen/avatar-4` is $0.10 per run. No idle GPU billing.

## Installation

```bash
pip install git+https://github.com/latentsync-dev/latentsync-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=latentsync-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import latentsync_api

output = latentsync_api.run({
    "image_url": "https://example.com/input.png",
    "audio_url": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from latentsync_api import Client

client = Client(api_key="sk-...")
output = client.run({"image_url": "https://example.com/input.png", "audio_url": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`veed/fabric-1.0`](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=latentsync-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Fabric 1.0 turns a photo plus an audio track into a talking-head video. | $0.08 |
| [`heygen/avatar-4`](https://synexa.ai/explore/heygen/avatar-4?utm_source=github&utm_medium=ugc&utm_campaign=latentsync-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Avatar 4 turns a photo into a talking avatar that speaks your text or lip-syncs to an audio file. | $0.1 |

The default model is **`veed/fabric-1.0`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `veed/fabric-1.0`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Portrait to animate (.jpg/.png/.webp). One clear, forward-facing face works best |
| `audio_url` | file | yes | — | — | Speech for the portrait to lip-sync to (.mp3/.wav/.flac/.m4a/.ogg) |
| `resolution` | string | no | `720p` | 720p, 480p | Output resolution of the talking-head video |

### `heygen/avatar-4`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Photo to animate (.jpg/.png/.webp). It must contain a clear face |
| `prompt` | string | no | `Hi - thanks for stopping by. Let me show…` | — | The text the avatar will speak |
| `voice` | string | no | — | — | Name of the voice to use for the avatar |
| `audio_url` | file | no | — | — | Optional speech for the avatar to lip-sync to (.mp3/.wav/.flac/.m4a/.ogg). When set, it overrides prompt and voice |
| `talking_style` | string | no | `stable` | stable, expressive | Talking style - 'stable' for minimal movement, 'expressive' for more animation |
| `expression` | string | no | — | — | Facial expression for the avatar to hold, e.g. friendly, serious, excited |
| `resolution` | string | no | `720p` | 360p, 480p, 540p, 720p, 1080p | Video resolution preset. Options: 360p, 480p, 540p, 720p, 1080p |
| `aspect_ratio` | string | no | `16:9` | 16:9, 9:16, 4:5, 5:4, 1:1, auto | Aspect ratio of the output video. Supported values: '16:9', '9:16', '4:5', '5:4', '1:1', and 'auto'. 'auto' preserves the source aspect ratio when HeyGen can read it, falling back to '16:9' otherwise. |
| `caption` | boolean | no | `False` | — | Whether to add captions to the video |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from latentsync_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About LatentSync

LatentSync is described in *LatentSync: Taming Audio-Conditioned Latent Diffusion Models for Lip Sync with SyncNet Supervision* from ByteDance, first released at the end of 2024 with follow-up 1.5 and 1.6 versions. Unlike earlier lip sync models that predict intermediate motion representations, it is end-to-end: the model edits the mouth region directly in the latent space of a diffusion model, conditioned on audio.

The pipeline uses a Stable Diffusion 1.5 U-Net operating on VAE latents, audio embeddings from Whisper, and a SyncNet loss during training that scores whether generated mouths match the speech. To fight the frame-to-frame flicker typical of diffusion video, the authors introduce TREPA (Temporal REPresentation Alignment), which aligns generated frames to a large self-supervised video model's temporal features. Later versions improved temporal consistency, added Chinese-speech performance and reduced memory use.

The input is an existing video plus an audio track; the output is that video with the mouth re-synchronised to the new audio, at the source resolution. Limits: it needs a mostly frontal face, it re-dubs rather than animates (a still photo has to be turned into video first), and inference is slower than real time on consumer GPUs.

The hosted endpoints used by this client are different models that provide the same lip sync capability. `veed/fabric-1.0` (the default) takes a portrait image and an audio file and returns a talking-head video at $0.08 per run; `heygen/avatar-4` animates a photo from either text plus a voice name or an audio file, with expression and talking-style controls, at $0.10 per run. Both animate a still image rather than re-dubbing an existing video. The original LatentSync weights are available at https://github.com/bytedance/LatentSync if you want to self-host.

**Official project:** https://github.com/bytedance/LatentSync

## Use cases

- **Dub a spokesperson into another language** — call `run({"image_url": portrait, "audio_url": translated_speech})` once per language and ship one video per market.
- **E-learning presenters** — pair an instructor photo with recorded narration to produce a talking head for each lesson.
- **Personalised sales videos** — generate a short greeting per prospect from a TTS clip, batched with `wait=False` and collected by webhook.
- **Script-to-avatar without recording** — switch to `model="heygen/avatar-4"` and pass `prompt` and `voice` so the avatar speaks the text directly.
- **Vertical social clips** — request `aspect_ratio="9:16"` and a 1080p `resolution` for short-form platforms.
- **Localised product explainers** — regenerate a product demo's presenter for each locale while keeping the same screen recording.

## FAQ

**Is there a LatentSync API?**

Not from ByteDance; LatentSync is released as open weights. This client exposes the same lip sync capability through hosted talking-head endpoints (`veed/fabric-1.0` and `heygen/avatar-4`) that you call over HTTPS.

**How much does the LatentSync API cost?**

The default `veed/fabric-1.0` model is $0.08 per run; `heygen/avatar-4` is $0.10 per run. Billing is per prediction; there is no hourly GPU charge.

**Can I run LatentSync without a GPU?**

With this client, yes: generation happens on the hosted service and your code only makes HTTP requests. Self-hosting LatentSync needs a CUDA GPU with enough memory for a diffusion U-Net, VAE and Whisper encoder.

**Does this client work with the original LatentSync repo or ComfyUI?**

No. It does not load the bytedance/LatentSync checkpoints and it is not a ComfyUI node. It is a network client for hosted endpoints. If you need LatentSync's video-to-video re-dubbing specifically, run the official repository locally.

**What input formats does it accept?**

For `veed/fabric-1.0`: `image_url` (a portrait in .jpg/.png/.webp with one clear, forward-facing face) and `audio_url` (.mp3/.wav/.flac/.m4a/.ogg), plus optional `resolution`. For `heygen/avatar-4`: `image_url` is required, and you supply either `prompt` plus `voice` or an `audio_url`, with optional `talking_style`, `expression`, `resolution`, `aspect_ratio` and `caption`. The output is a video URL.

**Is this the official LatentSync SDK?**

No. This is an independent, community-maintained client and is not affiliated with ByteDance, VEED or HeyGen. The official project lives at https://github.com/bytedance/LatentSync.

## Related

- [LatentSync (official repository)](https://github.com/bytedance/LatentSync) — paper, weights and inference code.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client this package wraps.
- [veed/fabric-1.0](https://synexa.ai/explore/veed/fabric-1.0) — the default hosted portrait-plus-audio talking-head model.
- [heygen/avatar-4](https://synexa.ai/explore/heygen/avatar-4) — hosted avatar model that speaks text or lip-syncs to audio.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of LatentSync. Model weights and trademarks belong to their respective owners.
