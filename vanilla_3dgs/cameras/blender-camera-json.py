"""
Convert Blender transforms_*.json to a camera JSON consumable by render.py.

Output format matches what render.py expects:
  [{img_name, width, height, fx, fy, rotation, tcw}, ...]

render.py reads `c['rotation']` and applies `.T`, so we store Rwc (= Rcw.T)
under that key — same convention as your COLMAP-side exporter.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--path", required=True, help="Blender scene root (e.g. data/blender/lego)")
    p.add_argument("--split", default="test", choices=["train", "test", "val"])
    p.add_argument("--out",   required=True, help="output camera json path")
    p.add_argument("--width",  type=int, default=800)
    p.add_argument("--height", type=int, default=800)
    args = p.parse_args()

    tf_path = Path(args.path) / f"transforms_{args.split}.json"
    with open(tf_path) as f:
        meta = json.load(f)

    W, H = args.width, args.height
    focal = 0.5 * W / np.tan(0.5 * meta["camera_angle_x"])

    cams = []
    for frame in meta["frames"]:
        c2w = np.array(frame["transform_matrix"], dtype=np.float32)
        c2w[:3, 1:3] *= -1                       # OpenGL -> OpenCV
        w2c = np.linalg.inv(c2w)
        Rcw = w2c[:3, :3]
        tcw = w2c[:3, 3]

        cams.append({
            "img_name": Path(frame["file_path"]).stem,
            "width":  W,
            "height": H,
            "fx": float(focal),
            "fy": float(focal),
            # render.py does: Rcw = np.array(c['rotation']).T
            # so store Rwc = Rcw.T here
            "rotation": Rcw.T.tolist(),
            "tcw": tcw.tolist(),
        })

    with open(args.out, "w") as f:
        json.dump(cams, f, indent=2)

    print(f"Wrote {len(cams)} cameras to {args.out}")


if __name__ == "__main__":
    main()