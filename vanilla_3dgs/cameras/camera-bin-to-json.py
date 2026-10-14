import json
import numpy as np
import torch
from pathlib import Path

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from gsplat.utils import *
from gsplat.read_write_model import *
from PIL import Image

            
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--cam", help="the given camera data")
    args = parser.parse_args()
    
    if args.cam:
        fn = args.cam
        print("Try to load %s ..." % fn)
        camera_params, image_params = read_model(Path(fn, "sparse/0"), ext='.bin')
    else:
        print("not camera file.")
        
    cameras = []
    for image_param in image_params.values():
        i = image_param.camera_id
        camera_param = camera_params[i]
        
        im_path = str(Path(fn, "images", image_param.name))
        image = Image.open(im_path)
        
        fx = camera_param.params[0]
        fy = camera_param.params[1]
        Rcw = torch.from_numpy(image_param.qvec2rotmat())
        tcw = torch.from_numpy(image_param.tvec)
        pos = torch.mm(-Rcw.T, tcw.view(3, 1))
        
        # Store data in dictionary
        cam_data = {
            "id": i,  
            "img_name": image_param.name.split(".")[0],
            "width": image.width,
            "height": image.height,
            "position": pos.tolist(),
            "rotation": Rcw.T.tolist(),
            "fx": float(fx),
            "fy": float(fy),
            "tcw": tcw.tolist()
        }
    
        cameras.append(cam_data)
    
    cameras = sorted(cameras, key=lambda x: int(x["img_name"]))
    
    # Save to JSON file
    output_path = "camera_params.json"
    with open(output_path, "w") as f:
        json.dump(cameras, f, indent=4)
    print(f"Saved camera parameters to {output_path}")