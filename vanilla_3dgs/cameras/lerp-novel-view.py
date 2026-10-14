import json
import numpy as np


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--cam", help="the given camera json data")
    args = parser.parse_args()
    
    # Load camera info
    with open(args.cam, "r") as file:
        camera = json.load(file)
    
    iter = 5    # interpolator
    ind = iter - 2  # cut head and tail
    ext_cameras = []
    for i in range( len(camera)-1 ):
        width = int(camera[i]["width"])
        height = int(camera[i]["height"])
        fx = camera[i]["fx"]
        fy = camera[i]["fy"]
        
        # always append the i-th one
        camera[i]["img_name"] = str((ind+1)*i)
        ext_cameras.append(camera[i])
        
        # i-th camera info
        pos_i = np.array(camera[i]['position'])
        tcw_i = np.array(camera[i]['tcw'])
        Rcw_i = np.array(camera[i]['rotation'])
        
        # (i+1)-th camera info
        pos_i1 = np.array(camera[i+1]['position'])
        tcw_i1 = np.array(camera[i+1]['tcw'])
        Rcw_i1 = np.array(camera[i+1]['rotation'])
        
        # find linearly interpolated views
        pos_i_inter = np.linspace(pos_i, pos_i1, num=iter)
        tcw_i_inter = np.linspace(tcw_i, tcw_i1, num=iter)
        Rcw_i_inter = np.linspace(Rcw_i, Rcw_i1, num=iter)
        
        for j in range(ind):
            # Store data in dictionary
            cam_data = {
                "id": i,  
                "img_name": str((ind+1)*i+j+1),
                "width": width,
                "height": height,
                "position": pos_i_inter[j+1].tolist(),
                "rotation": Rcw_i_inter[j+1].tolist(),
                "fx": float(fx),
                "fy": float(fy),
                "tcw": tcw_i_inter[j+1].tolist()
            }
            ext_cameras.append(cam_data)
        
    # append the last view
    camera[-1]["img_name"] = str((ind+1)*(len(camera)-1))
    ext_cameras.append(camera[-1])
    
    # Save to JSON file
    output_path = "camera_params_w_tcw_ext.json"
    with open(output_path, "w") as f:
        json.dump(ext_cameras, f, indent=4)
    print(f"Saved camera parameters to {output_path}")