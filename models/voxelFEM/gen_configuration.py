from PIL import Image
import numpy as np
import json
import os
import subprocess
import csv
from natsort import natsorted
import cv2

configuration_path = "models/voxelFEM/data/configuration_gen/"
chfem_gpu_path = "models/voxelFEM/chfem_gpu/chfem_gpu"
split_img_path = "models/voxelFEM/data/configuration_gen/split_img"
config_name = "upload"
upload_img_path = "models/voxelFEM/data/configuration_gen/upload.tif"
def cache_files(path):
    if os.path.exists(path):
        os.remove(path)    
    with open(path, 'w') as file:
        pass   
    # reorder the files in the folder in order of natural numbers
def get_sorted_files(dir_path):
    files = os.listdir(dir_path)
    sorted_files = natsorted(files)
    return [os.path.join(dir_path, file) for file in sorted_files]

def split_tif(input_file, split_img_path):
    if not os.path.exists(split_img_path):
        os.mkdir(split_img_path)
    # 读取tif文件
    upload = Image.open(input_file)
    upload.save(upload_img_path)
    img = cv2.imread(upload_img_path, cv2.IMREAD_UNCHANGED)
    # 拆分多张图像
    for i in range(img.shape[0]):
        output_file = os.path.join(split_img_path, f"image_{i}.tif")
        cv2.imwrite(output_file, img[i])
    tif_files = os.listdir(split_img_path)
    return tif_files

def export_raw(upload_file,type_of_analysis,config_name=config_name):
    # split the received 3d tif into individual image
    tif_files = split_tif(upload_file,split_img_path=split_img_path)
    # different computation gets different configuration path
    if type_of_analysis == 0:
        config_file_path = os.path.join(configuration_path,"thermal",config_name)
    elif type_of_analysis == 1:
        config_file_path = os.path.join(configuration_path,"elasticity",config_name)
    elif type_of_analysis == 2:        
        config_file_path = os.path.join(configuration_path,"fluid",config_name)    
    materials = {}
    dimensions = []
    vol = 0
    # Save image data in RAW format
    with open(config_file_path + '.raw', "bw") as file_raw:
        for filepath in tif_files:
            print(filepath)
            img = cv2.imread(os.path.join(split_img_path,filepath),0)
            m_data = np.array(img)
            mat_i, cmat_i = np.unique(m_data, return_counts=True)
            for i in range(len(mat_i)):
                if mat_i[i] in materials:
                    materials[mat_i[i]] += cmat_i[i]
                else:
                    materials[mat_i[i]] = cmat_i[i]
            # Save image data in binary format
            m_data.tofile(file_raw)
            dimensions = np.array([m_data.shape[1], m_data.shape[0], len(tif_files)], dtype=int)
            vol += m_data.shape[1] * m_data.shape[0]            
    materials = dict(sorted(materials.items(), key=lambda x: x[0]))
    mat = np.array(list(materials.keys()))  # used to generate properties
    return mat
    
def export_compute_config(upload_file,type_of_analysis,properties_dic,config_name=config_name):
    # split the received 3d tif into individual image
    tif_files = split_tif(upload_file,split_img_path=split_img_path)
    # different computation gets different configuration path
    if type_of_analysis == 0:
        config_file_path = os.path.join(configuration_path,"thermal",config_name)
    elif type_of_analysis == 1:
        config_file_path = os.path.join(configuration_path,"elasticity",config_name)
    elif type_of_analysis == 2:        
        config_file_path = os.path.join(configuration_path,"fluid",config_name)
    
    materials = {}
    dimensions = []
    vol = 0
    # Save image data in RAW format
    with open(config_file_path + '.raw', "bw") as file_raw:
        for filepath in tif_files:
            # print(filepath)
            img = cv2.imread(os.path.join(split_img_path,filepath),0)
            m_data = np.array(img)
            mat_i, cmat_i = np.unique(m_data, return_counts=True)
            for i in range(len(mat_i)):
                if mat_i[i] in materials:
                    materials[mat_i[i]] += cmat_i[i]
                else:
                    materials[mat_i[i]] = cmat_i[i]
            # Save image data in binary format
            m_data.tofile(file_raw)
            dimensions = np.array([m_data.shape[1], m_data.shape[0], len(tif_files)], dtype=int)
            vol += m_data.shape[1] * m_data.shape[0]            
    materials = dict(sorted(materials.items(), key=lambda x: x[0]))
    mat = np.array(list(materials.keys()))  # used to generate properties
    mat_copy = mat.copy()
    cmat = np.array(list(materials.values()))
    
    if type_of_analysis == 0 :
        mat = np.vstack((mat, np.zeros((mat.shape[0]), dtype=int))).T
    elif type_of_analysis == 1 :
        mat = np.vstack((mat, np.zeros((mat.shape[0]), dtype=int), np.zeros((mat.shape[0]), dtype=int))).T ### Elastic properties need 2 parameters
    elif type_of_analysis == 2:
        pass
    cmat = cmat * 100.0 / vol
    jdata = {}
    jdata["type_of_analysis"] = type_of_analysis
    jdata["type_of_solver"] = 0
    jdata["type_of_rhs"] = 1
    jdata["voxel_size"] = 1.0
    jdata["solver_tolerance"] = 1.0e-6
    jdata["number_of_iterations"] = 10000    
    jdata["image_dimensions"] = dimensions.tolist()
    jdata["refinement"] = 1
    jdata["number_of_materials"] = mat.shape[0]
    properties = mat.tolist()
    if type_of_analysis == 0:
        # THERMAL: color, conductivity
        for i in range(mat_copy.shape[0]):
            key = "thermal"+str(mat_copy[i])
            properties[i][1] = properties_dic[key]
    elif type_of_analysis == 1:
        # ELASTICITY: color, Young's modulus, Poisson's ratio
        for i in range(mat_copy.shape[0]):
            key_yong = "elastic"+str(mat_copy[i])+"Young's modulus"
            properties[i][1] = properties_dic[key_yong]
            key_poisson = "elastic"+str(mat_copy[i])+"Poisson's ratio"
            properties[i][2] = properties_dic[key_poisson]
    elif type_of_analysis == 2:
        # velocity fields only needs the porous color
        # properties = porous color
        pass
    # properties[0][1] = property_1_1
    # properties[0][2] = property_1_2
    # properties[1][1] = property_2_1
    # properties[1][2] = property_2_2
    # print(properties[0][1])
    jdata["properties_of_materials"] = properties
    jdata["volume_fraction"] = list(np.around(cmat, 2))
    jdata["data_type"] = "uint8"
    # Save image data in JSON format
    with open(config_file_path + ".json", 'w') as file_json:
        json.dump(jdata, file_json, sort_keys=False, indent=4, separators=(',', ': '))
    # Save image data in NF format
    with open(config_file_path + ".nf", 'w') as file_nf:
        sText = ''
        for k, v in jdata.items():
            sText += '%' + str(k) + '\n' + str(v) + '\n\n'
        sText = sText.replace('], ', '\n')
        sText = sText.replace('[', '')
        sText = sText.replace(']', '')
        sText = sText.replace(',', '')
        file_nf.write(sText)
    return config_file_path

def compute_thermal(config_file_path):
    file_raw = config_file_path + ".raw"
    file_nf = config_file_path + ".nf"
    output_csv = config_file_path + ".csv"
    record = config_file_path + "_w.txt"
    # matrix_log = config_file_path + "_xo"
    cache_files(output_csv)
    # cache_files(matrix_record)
    keyword_1 = "'/Homogenized Constitutive Matrix \\(Thermal Conductivity\\):/,/---/'"
    keyword_2 = "'NR>1 && NR<5'"
    command = f"{chfem_gpu_path} -i {file_nf} {file_raw} -m {record} | awk {keyword_1} | awk {keyword_2} | tr '\n' ',' | sed 's/,$/\\n/'"
    output = subprocess.check_output(command, shell=True)        
    # 首先将输出解码为字符串
    output_str = output.decode('utf-8') if isinstance(output, bytes) else output
    # 将输出分割成单个值
    values = output_str.split()
    # 将每个值作为一个元素写入.csv文件
    with open(output_csv, 'a') as f:
        writer = csv.writer(f)
        for i in range(0, len(values), 3):
            # remove trailing commas
            row = [val.rstrip(',') for val in values[i:i+3]]
            writer.writerow(row)
    return output_csv
    
def compute_elasticity(config_file_path):
    file_raw = config_file_path + ".raw"
    file_nf = config_file_path + ".nf"
    output_csv = config_file_path + ".csv"
    record = config_file_path + "_w.txt"
    # matrix_log = config_file_path + "_xo"
    cache_files(output_csv)
    keyword_1 = "'/Homogenized Constitutive Matrix \\(Elasticity\\):/,/---/'"
    keyword_2 = "'NR>1 && NR<8'"
    command = f"{chfem_gpu_path} -i {file_nf} {file_raw} -m {record} | awk {keyword_1} | awk {keyword_2} | tr '\n' ',' | sed 's/,$/\\n/'"
    output = subprocess.check_output(command, shell=True)
    # 首先将输出解码为字符串
    output_str = output.decode('utf-8') if isinstance(output, bytes) else output
    # 将输出分割成单个值
    values = output_str.split()
    # 将每个值作为一个元素写入.csv文件
    with open(output_csv, 'a') as f:
        writer = csv.writer(f)
        for i in range(0, len(values), 6):
            # remove trailing commas
            row = [val.rstrip(',') for val in values[i:i+6]]
            writer.writerow(row)
    return output_csv


# import os
# property_1_1 = 79.8 ### Young's modulus for the 0 materials 需调
# property_1_2 = 0.33  ### Poisson's ratio for the 0 materials 需调
# property_2_1 = 46.9 ### Young's modulus for the 255 materials 需调
# property_2_2 = 0.32  ### Poisson's ratio  for the 255 materials 需调
# 55.3 0.31
#     file_raw,file_nf,file_json = export_compute_config(tif_name, output_filename)