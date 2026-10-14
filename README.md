# ReparamGS-Palette

Official code for the SIGGRAPH Asia 2026 conference paper:

**Reparametrizing 3D Gaussian Splatting for Real-Time Palette-based Color and Luminance Editing**

[Cheng-Kang Ted Chao](https://mason.gmu.edu/~cchao8/) and [Yotam Gingold](https://cragl.cs.gmu.edu/)

**[Project page](https://cragl.cs.gmu.edu/palettegaussian/)**

This repo reparametrizes a trained 3D Gaussian Splatting scene into a palette-weight representation: each gaussian's color is expressed as weights over a small, automatically extracted color palette. Editing a palette color then re-colors the whole scene coherently in real time, enabling palette-based color and luminance editing (color grading) of 3DGS scenes.

The workflow has two stages:

1. **Train a vanilla 3DGS scene** — go to the [`vanilla_3dgs/`](vanilla_3dgs/) folder and follow its README to train a scene (or render an existing checkpoint for testing).
2. **Finetune into the palette-weight representation** — come back to this root folder and finetune the vanilla checkpoint with `finetune.py` for palette-based color grading (see below).

> **Note on rasterizers:** vanilla 3DGS and our reparametrized representation use **different CUDA rasterizers**. This root folder and `vanilla_3dgs/` each ship their own `gsplatcu`, and both build a Python package with the same name — installing one replaces the other. Install the rasterizer that matches the stage you are running (each stage's instructions include the install command).

## Installation

Install [conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda is fine), then create and activate the environment from the `environment.yml` in this repo:

```bash
conda env create -f environment.yml
conda activate colorfulgaussians
```

This provides Python 3.9, PyTorch, and all other Python dependencies. The CUDA rasterizers are *not* part of this step — each stage installs its own (see the note above).

## 1. Train a vanilla 3DGS scene

See [`vanilla_3dgs/README.md`](vanilla_3dgs/README.md). It covers installing the vanilla rasterizer, training a scene, generating camera paths, and rendering for testing. Training produces a checkpoint such as `data/statue_final.npy`, which is the input to the next stage.

## 2. Finetune into the palette-weight representation

Back in this root folder, install our rasterizer (this replaces the vanilla one):

```bash
pip3 install gsplatcu/.
```

This compiles CUDA sources, so it requires an NVIDIA GPU with the CUDA toolkit installed.

Then finetune a vanilla 3DGS checkpoint into the palette-weight representation. Example run:

```bash
python finetune.py --gs trained_models/3dgs/supersplats/statue_final.npy \
    --data dataset/supersplats/statue/ \
    --num_palette 3 --clamp_start 0.7 \
    --low_rank --reshape_P 5 --reshape_Q 15 \
    --convexhull_init --use_fast --epochs 50
```

where:

- `--gs` is the vanilla 3DGS checkpoint from stage 1 (required).
- `--data` is the same dataset the checkpoint was trained on (required).
- `--num_palette` sets the number of chromatic palette colors (black and white are always included in addition). Default: 4.
- `--convexhull_init` (optional) initializes the palette from a simplified convex hull of the scene's colors instead of the default even-hue initialization.
- `--low_rank` (optional, with `--reshape_P`/`--reshape_Q`) stores the view-dependent weights in a compact low-rank factorization — see the paper for details. `--use_fast` enables the fused CUDA path for the low-rank mode.
- `--clamp_start` sets the fraction of training after which the weights are clamped to non-negative and renormalized into a proper convex combination of the palette anchors (e.g. `0.7` starts clamping at 70% through training). Default: 1.0 (off).

Other optional flags:

- `--output` — output checkpoint path. Default: `data/<scene>_palette.npy`.
- `--epochs` — number of finetuning epochs. Default: 10.
- `--lambda_pos` — weight of the penalty on negative weights. Default: 0.5.
- `--lambda_compact`, `--compact_ramp_factor`, `--compact_schedule_start` — weight of the palette compactness loss and its ramp-up schedule. Defaults: 0.001, 5.0, 2/3.
- `--lambda_sep`, `--min_gap_fraction` — weight of the hue separation regularizer and the minimum hue gap (as a fraction of even spacing). Defaults: 1.0, 0.3.
- `--lambda_alpha` — weight of the alpha-channel supervision (Blender datasets only). Default: 1.0.
- `--resize_rate` — resolution multiplier on the training views. Default: 1.0.
- `--sh_order` — spherical harmonics order. Default: 3.
- `--dataset_type` — `auto` (default), `colmap`, or `blender`.

## Acknowledgements

The CUDA rasterizers in `gsplatcu/` and `vanilla_3dgs/gsplatcu/` are adapted from [EasyGaussianSplatting](https://github.com/scomup/EasyGaussianSplatting) by scomup (Liu Yang). See the license header in those source files for details.

## License

[![MIT License][mit-shield]][mit] [![CC BY 4.0][cc-by-shield]][cc-by]

The source code is licensed under the [MIT License][mit] (see [`LICENSE`](LICENSE)).

Everything else in this work (figures, renders, and other non-code assets) is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[mit]: LICENSE
[mit-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
