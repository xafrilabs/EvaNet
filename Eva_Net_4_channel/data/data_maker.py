import torch
import os
import re
import numpy as np
import math
from matplotlib import pyplot as plt
import sys

sys.path.append("../")
import config
from config import *

import shutil
import random

from tqdm import tqdm

def resize_data(input_data, factor, is_feature=False):
    """
    Resizes the height and width of input_data by dividing them by the given factor.

    Args:
        input_data (numpy array): The data to resize.
        factor (int): The factor by which height and width will be divided.
        is_feature (bool): If True, handles data with a channel dimension.

    Returns:
        numpy array: The resized data.
    """
    height = input_data.shape[0]
    width = input_data.shape[1]

    new_height = math.ceil(height / factor)
    new_width = math.ceil(width / factor)

    if is_feature:
        resized_data = input_data[::factor, ::factor, :]
    else:
        resized_data = input_data[::factor, ::factor]

    return resized_data

def pad_data(unpadded_data, is_feature = False):
    
    height = unpadded_data.shape[0]
    width = unpadded_data.shape[1]
    
    width_multiplier = math.ceil(width/SPATIAL_SIZE)
    height_multiplier = math.ceil(height/SPATIAL_SIZE)
    
    new_width = SPATIAL_SIZE*width_multiplier
    new_height = SPATIAL_SIZE*height_multiplier
    
    width_pad = new_width-width
    height_pad = new_height-height
        
    if width_pad%2 == 0:
        left = int(width_pad/2)
        right = int(width_pad/2)
    else:
        print("Odd Width")
        left = math.floor(width_pad/2)
        right = left+1
    
    if height_pad%2 == 0:
        top = int(height_pad/2)
        bottom = int(height_pad/2)
    else:
        print("Odd Height")
        top = math.floor(height_pad/2)
        bottom = top+1
    
        
    if is_feature:
        data_padded = np.pad(unpadded_data, pad_width = ((top, bottom),(left, right), (0, 0)), mode = 'reflect')

    else:
        data_padded = np.pad(unpadded_data, pad_width = ((top, bottom), (left, right)), mode = 'reflect')
        
    assert data_padded.shape[0]%SPATIAL_SIZE == 0, f"Padded height must be multiple of SPATIAL_SIZE: {SPATIAL_SIZE}"
    assert data_padded.shape[1]%SPATIAL_SIZE == 0, f"Padded width must be multiple of SPATIAL_SIZE: {SPATIAL_SIZE}"
    
    return data_padded


def crop_data(uncropped_data, filename, is_feature = False):
    
    output_path = "./cropped"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    height = uncropped_data.shape[0]
    width = uncropped_data.shape[1]
    
    print("crop input height: ", height)
    print("crop input width: ", width)
    
    vertial_patches = height//SPATIAL_SIZE
    horizontal_patches = width//SPATIAL_SIZE
    
    print("vertial_patches: ", vertial_patches)
    print("horizontal_patches: ", horizontal_patches)
    print(filename)
    
    cropped_data = []
    
    for y in range(0, vertial_patches):
        for x in range(0, horizontal_patches):
            
            if is_feature:
                new_name = filename[:8]+"_y_"+str(y)+"_x_"+str(x)+"_features.npy"
            else:
                new_name = filename[:8]+"_y_"+str(y)+"_x_"+str(x)+"_label.npy"
            
            # print("new_name: ", new_name)
            
            x_start = (x)*SPATIAL_SIZE
            x_end = (x+1)*SPATIAL_SIZE
            
            y_start = (y)*SPATIAL_SIZE
            y_end = (y+1)*SPATIAL_SIZE
            
            patch = uncropped_data[y_start: y_end, x_start:x_end]
            
            # print(patch.shape)
            
            np.save(os.path.join(output_path, new_name), patch)


def make_data(feature_files, data_path):
    
    for feature_file in tqdm(feature_files):
        ## Load feature data:
        feature_data = np.load(os.path.join(data_path, feature_file))
        # print("feature_data.shape: ", feature_data.shape)

        ## Load label data:
        label_file = feature_file[:8]+"_labels.npy"
        try:
            label_data = np.load(os.path.join(data_path, label_file))
            print(label_data.shape)
        except:
            print(f"No such files as {label_file}")

        ###########Resize data to desired size ######################################
        feature_data = resize_data(feature_data, factor=5, is_feature=True)
        label_data = resize_data(label_data, factor=5)
        
        ###########Padd data to fit SPATIAL_SIZE pathches######################################
        padded_feature = pad_data(feature_data, is_feature = True)
        padded_label = pad_data(label_data)

        # print("padded_feature.shape: ", padded_feature.shape)
        # print("padded_label.shape: ", padded_label.shape)

        ###########Crop data to SPATIAL_SIZE pathches######################################
        cropped_feature = crop_data(padded_feature, feature_file, is_feature = True)
        cropped_label = crop_data(padded_label, label_file)


def make_dir(feature_files):

    region_path_dict = dict()

    for feature_file in feature_files:
        region_num = int(feature_file.split("_")[1])

        if region_num == 1 and not os.path.exists("./Region_2_3_TRAIN_Region_1_TEST"):
            os.mkdir("./Region_2_3_TRAIN_Region_1_TEST")
            os.mkdir("./Region_2_3_TRAIN_Region_1_TEST/cropped_data_train")
            os.mkdir("./Region_2_3_TRAIN_Region_1_TEST/cropped_data_val_test")
        elif region_num == 2 and not os.path.exists("./Region_1_3_TRAIN_Region_2_TEST"):
            os.mkdir("./Region_1_3_TRAIN_Region_2_TEST")
            os.mkdir("./Region_1_3_TRAIN_Region_2_TEST/cropped_data_train")
            os.mkdir("./Region_1_3_TRAIN_Region_2_TEST/cropped_data_val_test")
        elif region_num == 3 and not os.path.exists("./Region_1_2_TRAIN_Region_3_TEST"):
            os.mkdir("./Region_1_2_TRAIN_Region_3_TEST")
            os.mkdir("./Region_1_2_TRAIN_Region_3_TEST/cropped_data_train")
            os.mkdir("./Region_1_2_TRAIN_Region_3_TEST/cropped_data_val_test")

    # Add directory for combined dataset
    if not os.path.exists("./Region_X_X_TRAIN_Region_X_TEST"):
        os.mkdir("./Region_X_X_TRAIN_Region_X_TEST")
        os.mkdir("./Region_X_X_TRAIN_Region_X_TEST/cropped_data_train")
        os.mkdir("./Region_X_X_TRAIN_Region_X_TEST/cropped_data_val_test")
        

def move_files(feature_files):

    all_files = os.listdir("./cropped")

    # Group feature and label files together
    grouped_files = {}
    for file in all_files:
        base_name = "_".join(file.split("_")[:-1])  # Exclude the last part ("features.npy" or "label.npy")
        if base_name not in grouped_files:
            grouped_files[base_name] = []
        grouped_files[base_name].append(file)

    grouped_files = list(grouped_files.values())
    random.shuffle(grouped_files)  # Shuffle groups to ensure randomness for the combined dataset

    for feature_file in feature_files:

        print("Processing: ", feature_file)
        region_num = int(feature_file.split("_")[1])

        for group in tqdm(grouped_files):
            file_region_num = int(group[0].split("_")[1])  # Assuming region number is consistent across files in the group
            for file in group:
                source = os.path.join("./cropped", file)

                if region_num == 1:
                    if region_num == file_region_num:
                        destination = os.path.join("./Region_2_3_TRAIN_Region_1_TEST/cropped_data_val_test", file)
                        shutil.copyfile(source, destination)
                    else:
                        destination = os.path.join("./Region_2_3_TRAIN_Region_1_TEST/cropped_data_train", file)
                        shutil.copyfile(source, destination)
                elif region_num == 2:
                    if region_num == file_region_num:
                        destination = os.path.join("./Region_1_3_TRAIN_Region_2_TEST/cropped_data_val_test", file)
                        shutil.copyfile(source, destination)
                    else:
                        destination = os.path.join("./Region_1_3_TRAIN_Region_2_TEST/cropped_data_train", file)
                        shutil.copyfile(source, destination)
                else:
                    if region_num == file_region_num:
                        destination = os.path.join("./Region_1_2_TRAIN_Region_3_TEST/cropped_data_val_test", file)
                        shutil.copyfile(source, destination)
                    else:
                        destination = os.path.join("./Region_1_2_TRAIN_Region_3_TEST/cropped_data_train", file)
                        shutil.copyfile(source, destination)

    # Handle combined dataset with 90:10 split
    train_dir = "./Region_X_X_TRAIN_Region_X_TEST/cropped_data_train"
    test_dir = "./Region_X_X_TRAIN_Region_X_TEST/cropped_data_val_test"

    train_split = int(len(grouped_files) * 0.9)
    train_groups = grouped_files[:train_split]
    test_groups = grouped_files[train_split:]

    for group in train_groups:
        for file in group:
            source = os.path.join("./cropped", file)
            destination = os.path.join(train_dir, file)
            shutil.copyfile(source, destination)

    for group in test_groups:
        for file in group:
            source = os.path.join("./cropped", file)
            destination = os.path.join(test_dir, file)
            shutil.copyfile(source, destination)


def main():
    
    data_path = "./repo/FloodNetData"
    
    data_files = os.listdir(data_path)

    ## only keep .npy file and features
    feature_files = [file for file in data_files if file.endswith(".npy") and re.match(".*Features.*", file) ]
    # print("Files Found: ", feature_files)
    
    ## Make directories for train_test regions 
    make_dir(feature_files)
    
    ## Pad and crop data
    make_data(feature_files, data_path)
    
    ## Move image crops to directory
    move_files(feature_files)
    

if __name__ == "__main__":
    main()
