import cv2
from PIL import Image
import os

def simple_binary(uploads,thresh,maxval,threashold_type):
    downloads = []
    for file in uploads:
        path = f'models/voxelFEM/data/image_process/upload_img/{file.name}'
        # print("******print the path:",file,file.name)
        img = Image.open(file)
        img.save(path)
        img = cv2.imread(path,0)
        _,bin_img = cv2.threshold(img,thresh,maxval,getattr(cv2,threashold_type))
        # current_path = os.getcwd()
        # print("******imwrite_current_path",current_path)
        process_path = f'models/voxelFEM/data/image_process/simple_binary/{file.name}'
        cv2.imwrite(process_path,bin_img)
        downloads.append(process_path)
    return downloads


def adaptive_binary(uploads,threashold_algrithom,threashold_type,blockSize,c_value):
    downloads = []
    # current_path = os.getcwd()
    # print("******current_path",current_path)
    for file in uploads:
        path = f'models/voxelFEM/data/image_process/upload_img/{file.name}'
        # print("******print the path:",file,file.name)
        img = Image.open(file)
        img.save(path)
        img = cv2.imread(path,0)
        bin_img = cv2.adaptiveThreshold(img,255,getattr(cv2,threashold_algrithom), getattr(cv2,threashold_type),blockSize,c_value)
        # current_path = os.getcwd()
        # print("******imwrite_current_path",current_path)
        process_path = f'models/voxelFEM/data/image_process/adaptive_binary/{file.name}'
        cv2.imwrite(process_path,bin_img)
        downloads.append(process_path)
    return downloads
