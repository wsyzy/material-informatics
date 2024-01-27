import os
from stl import mesh
import subprocess      
import pumapy as puma
   
stl2tif_path = "models/voxelFEM/data/slice_rebuild/stl2tif.sh"     
   
def get_dimension(model_stl_path):
    stl_mesh = mesh.Mesh.from_file(model_stl_path)
    dims = [dim_max-dim_min for dim_max,dim_min in zip(stl_mesh.max_,stl_mesh.min_)]
    min_number = min(dims)
    if min_number < 1:
        for _ in range(10):
            min_number = min_number*10
            dims = [num*10 for num in dims]
            if min_number > 10:
                break
    return dims

def single_stl2tif(upload):
    filename = "upload"
    path = f'models/voxelFEM/data/slice_rebuild/upload_stl/{filename}.stl'
    with open(path,"wb") as f:
        f.write(upload.getbuffer())
    dims = get_dimension(path)
    # 定义命令和参数
    script_dir = os.path.dirname(stl2tif_path)
    # bash_stl_path is defined stl_path relative to the path of stl2tif.sh 
    # bash_stl_path = "../../model/stl" 
    command = "bash"
    input_file = f"upload_stl/{filename}.stl"
    output_file = filename+"_"+"_".join(str(int(dim)) for dim in dims)
    print(input_file)
    args = [stl2tif_path.split("/")[-1], "-i", input_file, "-o", output_file, "-x", str(int(dims[0])+1), "-y",str(int(dims[1])+1), "-z",str(int(dims[2])+2)]
    subprocess.run([command] + args,cwd=script_dir)
    d3_tif = f'models/voxelFEM/data/slice_rebuild/3d_tif/{output_file}.tif'
    return d3_tif

def rebuild(upload,minValue,maxValue,flag_closed_edges,flag_gaussian):
    filename = "upload"
    path = f'models/voxelFEM/data/slice_rebuild/upload_3d_tif/{filename}.tif'
    with open(path,"wb") as f:
        f.write(upload.getbuffer())
    ws = puma.import_3Dtiff(path)
    save_path = f"models/voxelFEM/data/slice_rebuild/export_stl/export_{minValue}_{maxValue}.stl"
    puma.export_stl(save_path,
                    ws,
                    cutoff=(minValue,maxValue),
                    flag_closed_edges=flag_closed_edges,
                    flag_gaussian=flag_gaussian,
                    binary=True)
    puma.render_contour(ws,cutoff=(minValue,maxValue))
    return save_path