#!/usr/bin/env python
# coding: utf-8

# ### Hola!
# 
#  This document contains the Python code for the Image Analysis for the Grinding Operation Project, a project brought forth by the MASTeR Lab; Prof. Barbara Linke, Associate Professor in Mechanical and Aerospace Engineering, University of California, Davis.
# 
# 
# This document was authored by Abdul-Hakeem Omotayo, Xiancheng Lin, and Xuezhen Li

# ### **How To Use This File**
# 
# Please follow the instructions below to set up Python and all dependencies
# 
# 1. Download and install the latest version of Python here https://www.python.org/downloads/
# 
# 2. Install PIP https://pip.pypa.io/en/stable/installation/.
#
#   if you installed python from step 1, you should have PIP automatically installed too.
#   Then install all dependencies by running th code below in your terminal
#   pip install --upgrade pip
#   pip install numpy pandas opencv-python scikit-image scikit-learn statsmodels
#
# 3. Install any of Jupyterlab or Jupyter Notebook https://jupyter.org/install.
#
#    You can as well run the raw python script after installing all dependencies
# 
# 4. Download Linke_Data_shared from Dropbox. The folder containing the data must be named Linke_Data_shared.
# 
# 5. Choose or create a folder you want all project artefact to be stored in, say, Favorite Folder Location. Then, set up a folder structure as below.
# 
# 
# ![folder_structure_img.png](attachment:folder_structure_img.png)
# 
# <!-- Favorite Folder Location/
# │ 
# ├── Linke_Data_shared/
# │   ├── INITIAL_3D printed_Photos_50X/
# │   ├── INITIAL_3D printed_Photos_200X/
# │   ├── INTERMEDIATE_PHOTOS/ 
# │   ├── Post_Test_Photos/
# │   ├── INITIAL_PROFILOMETER_READINGS/
# │   ├── INTERMEDIATE_PROFILOMETER_READINGS/ 
# │   ├── POST_PROFILOMETER_READINGS/
# │ 
# ├── Image_Analysis_MASTeR_Lab.ipynb
# │ 
# ├── Linke_Prediction/
#  -->
# 
# 
# Note: Data folder i.e Linke_Data_shared must be at the same level as Image_Analysis_MASTeR_Lab.ipynb
# 
# 6. Any new set of images that would be used in model building should be saved in the appropriate folder. The default folder is Linke_Prediction.
# 
# 7. To predict response on new images, the last cell in this notebook contain an example
# 
# 

# #### **Load Modules**

# In[4]:


##get_ipython().run_cell_magic('capture', '', '################################################################################\n############           Install dependecies for the project              ########\n################################################################################\n\n\n# pip install --upgrade pip\n# pip install numpy pandas opencv-python rpy2 openpyxl matplotlib gitpython requests scikit-image scikit-learn statsmodels lightgbm')


# In[ ]:


################################################################################
############           Install dependecies for the project              ########
################################################################################


# import Python modules

import gzip, os

import numpy as np
import pandas as pd


from os import walk
from glob import glob


# In[5]:


##get_ipython().run_cell_magic('capture', '', '\n# import Python modules\n\nimport gzip, os\n\nimport numpy as np\nimport pandas as pd\n\n\nfrom os import walk\nfrom glob import glob')


# #### **Download and Unpack Files Using**

# In[6]:


######  %%capture # capture all output. Nothing will be displayed. Uncomment to display cell output


################################################################################
############           Download files from Google Drive Using R         ########
################################################################################


###### Uncomment cell if Linke_Data_shared folder is not available
###### The folder will be downloaded from google drive as a zip file
######  The content downloaded only contains all the files provided by MASTeR Lab as of 03-13-2022


# %load_ext rpy2.ipython # load R into Python

# %%R

# h = install.packages("pacman")
# h = library(pacman)
# p_load("tidyverse", "googledrive")

# downloading data

# drive_deauth()
# drive_user()
# public_file = drive_get(as_id("17TsDWM-Ug8mQuSqEp-6zn_W1raMdNgiV"))
# drive_download(public_file, overwrite = T)


# #### **Unzipping File**

# In[7]:


# %%capture

# if on google colab
# !unzip "/content/Linke_Data_shared.zip" -d "/content/"

# !unzip "Linke_Data_shared.zip"
# not_reading = glob("Linke_Data_shared/*.txt")
# if os.path.exists(not_reading[0]):
#   os.remove(not_reading[0])
# else:
#   print("Can not delete the file as it doesn't exists")


# #### **Data Preprocessing**

# In[8]:



def extract_excel(file):
    
    """
    
    Task: Extract the profilometer readings from a .xlsx file.
    
    Argument:
            file: filepath to excel file.
            
    Return:
            entry_dict: dataframe of file metadata and values the extracted from excel file
            
    """
    
    profilometer_xlsx = pd.read_excel(io = file, sheet_name=1, header=None)
    entry_dict = {}
    for row in profilometer_xlsx.iloc[0:23,0]:
        val_vec = [item for item in row.split(" ") if item != ''][0:2]

        try:
            entry_dict[val_vec[0]] = [float(val_vec[1])]
        except:
            entry_dict[val_vec[0]] = [float("nan")] # For those with errors, set to NaN

    entry_dict  = pd.DataFrame.from_dict(entry_dict)
    meta_data_df = profilometer_metadata_namer(file)
    entry_dict = meta_data_df.join(entry_dict)
    return(entry_dict)


# In[9]:



def extract_txt(file):
    
    """
    
    Task: Extract the profilometer readings from a .txt file.
    
    Argument:
            file: filepath to text file.
            
    Return:
            entry_dict: dataframe of file metadata and values the extracted from text file
            
    """
    
    profilometer_txt = pd.read_table(file)
    entry_dict = {}
    
    for pos,val in enumerate(profilometer_txt.iloc[16:39,0]):
        val_vec = [item for item in val.split(";") if item != ''][0:2]
        if pos == 12: # fixing double occurence of Rmr(c)
          val_vec[0] += "2"

        try:
            entry_dict[val_vec[0]] = [float(val_vec[1])]
        except:
            entry_dict[val_vec[0]] = [float("nan")]
  
    entry_dict  = pd.DataFrame.from_dict(entry_dict)
    meta_data_df = profilometer_metadata_namer(file)
    entry_dict = meta_data_df.join(entry_dict)
    return(entry_dict)


# In[10]:



def profilometer_metadata_namer(file):
    
    """
    
    Task:   Create metadata for file.
    
    Argument:
            file: filepath.
            
    Return:
            meta_data_df: dataframe of file metadata
            
    """

    file_id = file.split("/")[-1].split(".")[0].split("_")
    file_snap_time = file.split("/")[1].split("_")[0]
    if file_snap_time == "INTERMEDIATE":
        if file_id[0] == "01":
          file_id[0] = "0"
        meta_data_df = pd.DataFrame({"Capturetime": file_snap_time, "Buildangle":[file_id[0]], "Facenumber": [file_id[1]], "Measurementnum": [file_id[2]]})
    else:
        meta_data_df = pd.DataFrame({"Capturetime": file_snap_time, "Buildangle":[file.split("/")[-2].split("_")[0]], "Facenumber": [file_id[0]], "Measurementnum": [file_id[1]]})
    return(meta_data_df)


# In[11]:


################################################################################
####### Read all profilometer readings found in the Linke_Data_shared   ########
################################################################################


prof_filenames = glob("Linke_Data_shared/**/*.TXT", recursive=True) + glob("Linke_Data_shared/**/*.xlsx", recursive=True)
print("{} TXT and XLSX files matched".format(len(prof_filenames)))
img_profilometer_data =[]
processed = 0
alternates = 0
pd_file = []
for pos,file in enumerate(prof_filenames):

  if "Alternate" in file: # ignoring profilometer filenames that has alternate
    alternates += 1
    continue
  if ".TXT" in file:
    profile_readings = extract_txt(file)
    profile_readings.rename(columns={"Rku": "Rkmu", "Rmr(c)": "Rmr(c)1"}, inplace=True)
    processed += 1
  else:
    profile_readings = extract_excel(file)
    profile_readings.rename(columns={"Rkµ": "Rkmu"}, inplace=True)
    processed += 1
  if pos > 0:
    img_profilometer_data = pd.concat([img_profilometer_data,profile_readings])
  else: 
    img_profilometer_data = profile_readings
  pd_file.append(file)
  if ((pos+1) % 20  == 0 or pos == len(prof_filenames) - 1):
    print("Processed {0} out of {1} profilometer readings. File id: {2}".format(processed, len(prof_filenames), file.split("/")[-1]))
img_profilometer_data["ProfileFilepath"] =  pd_file   
print()
print()
print("Finished processing all {} profilometer readings excluding {} alternates".format(processed, alternates))


# In[12]:


################################################################################
#######         Read all images found in the Linke_Data_shared          ########
################################################################################


img_filenames = glob("Linke_Data_shared/**/*.jpg", recursive=True)
print("{} JPG images matched".format(len(prof_filenames)))
magnif, buildangle, facenumber, file_snap_times, filepaths = [], [], [], [], []
for pos,img_file in enumerate(img_filenames):
  if ((pos+1) % 10  == 0 or pos == len(img_filenames) - 1):
    print("Processing {0} out of {1} Grinding tool image. Filepath: {2}".format(pos + 1, len(img_filenames), img_file))
  file_snap_time = img_file.split("/")[1].split("_")[0].upper()
  try:
    if file_snap_time == "INITIAL":
      file_id = img_file.split("/")[-1].split(".")[0].split("_")
      if "A" in file_id[1]: # ignoring images that are alternate
            continue
      else:
          facenumber.append(file_id[1])
      buildangle.append(file_id[0])
      magnif.append(img_file.split("/")[1].split("_")[-1][:-1]) 
      filepaths.append(img_file)
      file_snap_times.append(file_snap_time)
    elif  file_snap_time == "INTERMEDIATE":
      file_id = img_file.split("/")[-1].split(".")[0].split("_")
      if "A" in file_id[1]: # ignoring images that are alternate
            continue
      else:
          facenumber.append(file_id[1])    
      magnif.append(file_id[3])
      buildangle.append(file_id[2])
      filepaths.append(img_file)
      file_snap_times.append(file_snap_time)       
    elif  file_snap_time == "POST":
      file_id = img_file.split("/")[-1].split(".")[0].split("_")
      if "A" in file_id[1]: # ignoring images that are alternate
            continue
      else:
          facenumber.append(file_id[1])
      magnif.append(file_id[2])
      buildangle.append(file_id[0])
      filepaths.append(img_file)
      file_snap_times.append(file_snap_time)
    else:
      print("Error: Bad file: {}".format(img_file))
  except:
      print("Something went wrong while processing file: {}".format(img_file))
    
print("\n\n\nFinished processing all files")
img_metadata = pd.DataFrame({"Capturetime": file_snap_times, "Buildangle":buildangle, "Facenumber": facenumber, "Zoom": magnif, "ImgFilepath": filepaths})
print("\n{} images were succesfully read by the program and is ready to be used\n".format(img_metadata.shape))


# In[13]:



def aggregate_by_img(df):
    
    """
    
    Task:   Aggregate profilometer readings for each image.
            Mean is computed for continuous variable.
            Number (count) of entries is computed for categorical variable
    
    Argument:
            df: dataframe containing profilometer readings and the metadata for each profilometer.
            
    Return:
            df_agg: dataframe of aggregated data for each image
            
    """    
    
    agg_arg = {}
    col_names = df.columns[3:]
    for col in col_names:
        agg_arg[col] = 'mean'
        if col == 'Measurementnum' :
           agg_arg[col] = "count"
        if col == "ProfileFilepath":
           agg_arg[col] = "first"       

    df_agg = df.groupby(["Capturetime", "Buildangle", "Facenumber"]).agg(agg_arg)
    print('Aggregated dataframe from {} to {}'.format(df.shape, df_agg.shape))
    return df_agg


# In[14]:


################################################################################
#######             Display  some images metadata                       ########
################################################################################


##display(img_metadata.head())
##print(img_metadata.shape)


################################################################################
#######             Display  some profilometer metadata                 ########
################################################################################

##display(img_profilometer_data.head())
##print(img_profilometer_data.shape)


# In[15]:


################################################################################
####      Aggregate the profilometer reading into a new dataframe          #####
################################################################################

##img_profilometer_data_agg = aggregate_by_img(img_profilometer_data)

##display(img_profilometer_data_agg.head())
##print(img_profilometer_data_agg.shape)


# In[16]:



##########################################################################################################
#### Merge (only intersection) profilometer dataset with corresponding images. One reading per image #####
####                Dispay merged dataset including number of rows and columns                       #####
##########################################################################################################

##grinding_img_dataset = pd.merge(left = img_profilometer_data, right = img_metadata, how = "inner", on= ["Capturetime", 'Buildangle','Facenumber'], indicator = True)

##display(grinding_img_dataset)
##print(grinding_img_dataset.shape)

##########################################################################################################################
####   Merge (only intersection) aggregated profilometer dataset with corresponding images. One reading per image    #####
####                          Dispay merged dataset including number of rows and columns                             #####
##########################################################################################################################

##grinding_img_agg_dataset = pd.merge(left = img_profilometer_data_agg, right = img_metadata, how = "inner", on= ["Capturetime", 'Buildangle','Facenumber'], indicator = True)
##
##display(grinding_img_agg_dataset)
##print(grinding_img_agg_dataset.shape)


# #### **Descriptive Statistics**

# In[17]:


################################################################################
####          Descriptive statistics of unaggregated dataframe             #####
################################################################################

##display(grinding_img_dataset.describe())


# In[18]:


################################################################################
####           Descriptive statistics of aggregated dataframe              #####
################################################################################

##display(grinding_img_agg_dataset.describe())


# #### **Load Sample Image**

# In[19]:


################################################################################
####                        Import Python modules                          #####
################################################################################


##from matplotlib import pyplot as plt
##from skimage.io import imread
##import cv2


# In[55]:


################################################################################
####                        Show sample image                              #####
################################################################################

##img_test = imread(grinding_img_dataset.loc[:,"ImgFilepath"][90])
##plt.figure(figsize=(5,5))
##print(img_test.shape)
##plt.imshow(img_test)


# In[21]:


###########################################################################################
####        Download fast GLCM from https://github.com/tzm030329/GLCM/#readme         #####
####   code based on the algorithm in  https://ieeexplore.ieee.org/document/8803652   #####
###########################################################################################

##import requests
##import re

##def getFilename_fromCd(cd):
##    
##    """
##    Task: Get filename from content-disposition
##    
##    Argument: content-disposition
##    
##    Return: content filename
##    """
##    
##    if not cd:
##        return None
##    fname = re.findall('filename=(.+)', cd)
##    if len(fname) == 0:
##        return None
##    return fname[0]
##
##glcm_master = "GLCM-master.zip"
##
##if os.path.exists(glcm_master):
##    print("GLCM already exist exists")
##else:
##    url = 'https://github.com/tzm030329/GLCM/archive/refs/heads/master.zip'
##    r = requests.get(url, allow_redirects=True)
##    filename = getFilename_fromCd(r.headers.get('content-disposition'))
##    print(filename)
##    open(filename, 'wb').write(r.content)
##    get_ipython().system('unzip GLCM-master.zip ')
##    get_ipython().system('cp GLCM-master/fast_glcm.py fast_glcm.py')
    
    
######### if google colab is being used, uncomment the next two lines    

# !git clone https://github.com/tzm030329/GLCM.git
# !cp /content/GLCM/fast_glcm.py fast_glcm.py
 


# #### **Plot Some GLCM Extraction**

# In[22]:


################################################################################
####                  Show sample GLCM images                              #####
################################################################################

##from fast_glcm import *
##
##plt.figure(num=1,figsize=(13,15))
##glcm_functs = {"mean":fast_glcm_mean, "contrast":fast_glcm_contrast, "std":fast_glcm_std, "dissimilarity":fast_glcm_dissimilarity,
##                  "homogeneity":fast_glcm_homogeneity, "max": fast_glcm_max, "entropy": fast_glcm_entropy }
##plt.subplot(3,3,1)
##plt.title("Original")
##plt.imshow(img_test)
##plot_count = 2
##for key in glcm_functs.keys():
##    plt.subplot(3,3,plot_count)
##    plt.imshow(glcm_functs[key](np.resize(img_test,(img_test.shape[0],img_test.shape[1]))))
##    plt.title(key)
##    plot_count += 1
##    
##plt.show()    
    


# #### **Denoise image**

# In[23]:


##from skimage.restoration import denoise_nl_means, estimate_sigma
##from skimage.metrics import peak_signal_noise_ratio


# In[24]:


################################################################################
####                      Denoise GLCM images                              #####
################################################################################

##patch_kw = dict(patch_size=5,      # 5x5 patches
##                patch_distance=6,  # 13x13 search area
##                channel_axis=-1)
##
##sigma_est = np.mean(estimate_sigma(img_test, channel_axis=-1))
##print(f'estimated noise standard deviation = {sigma_est}')
##
##
##denoise2_fast = denoise_nl_means(img_test, h=0.6 * sigma_est, sigma=sigma_est,
##                                 fast_mode=True, **patch_kw)
##plt.imshow(denoise2_fast)


# In[25]:


################################################################################
####                Show denoised GLCM images                              #####
################################################################################

##plt.imshow(fast_glcm_std(np.resize(denoise2_fast,(denoise2_fast.shape[0],denoise2_fast.shape[1]))))
##plt.title("Std")


# #### **Lightening Image**

# In[26]:


##import skimage.exposure as skie


# In[27]:


########################################################################################
####     Brighten images using Contrast Limited Adaptive Histogram Equalization    #####
########################################################################################

##plt.imshow(skie.equalize_adapthist(img_test))


# #### **Prepare Dataset**

# In[28]:


########################################################################################
#############     Utility function used for generating datasets tion     ##############
########################################################################################


##def generate_design_matrix(df, magnifs = False, response_var = "Ra"):
##        
##    """
##    
##    Task:   Generate the design matrix for regression.
##               
##    Argument:
##            df: dataframe containing merged profilometer reading, metadata, and image data.
##            magnifs: Choose magnification to focus on. Default to false for all magnification,
##                    50 for 50X magnification and 200 for 200X magnification
##            response_var: the response variable to be predicted. Defaults to Ra values
##            
##    Return: A tuple of response variable (target) and predictors (dataset).
##            target: dataframe of response
##            dataset: the X matrix
##            
##    """    
## 
##    
##    if magnifs == 200 or magnifs == 50:
##        df = df[df["Zoom"] == str(magnifs)]
##        
##    df = df.loc[:,[response_var,"ImgFilepath"]]
##    dataset = pd.DataFrame()
##    for pos, file in enumerate(df["ImgFilepath"]):
##        if ((pos+1) % 10  == 0 or pos == len(file) - 1):
##            print("Processing {0} out of {1} Grinding tool image. Filepath: {2}".format(pos + 1, df.shape[0], file))  
##        if pos == 0:
##            dataset = feature_extractor(file)
##        else:
##            f_df = feature_extractor(file)
##            dataset = pd.concat([dataset,f_df], axis=0)
##    print("Processed all image file and generated design matrix")
##    target = df[response_var]
##    return (target, dataset)


# In[113]:


########################################################################################
#############     Utility functions used for generating datasets tion     ##############
########################################################################################


def img_splitter(file, num_slice_height, num_slice_width, expose): 
            
    """
    
    Task:   Split image into num_slice_height x num_slice_width.
               
    Argument:
            file: image filepath.
            num_slice_height: Number of division accros image height (vertical)
            num_slice_width: Number of division accros image width (horizontal)
            
    Return: Sliced_img_dict: A dictionary (key-value pair) of sliced image.
            key: Index of image running from 1 to num_slice_height x num_slice_width
            value: corresponding image tensor for the chosen key
            
    """ 
    
    img = imread(file)

    if expose == True: 
        img = skie.equalize_adapthist(img)
    
    (img_height, img_width, num_channels) = img.shape
    height_coord = [ii * img_height//num_slice_height for ii in range(0, num_slice_height + 1)] # generate the cutting point for the img. 
    width_coord = [ii * img_width//num_slice_width for ii in range(0, num_slice_width + 1)]
    sliced_img_dict = {}
    indx = 1
    
    for ii in range(len(height_coord)): 
        if ii == len(height_coord)-1: # dont try index index out of range
            continue
        for jj  in range(len(width_coord)):
            if jj == len(width_coord)-1:
                continue
            else:
                sliced_img_dict[indx] = img[ height_coord[ii]:height_coord[ii+1], width_coord[jj]:width_coord[jj+1], : ]
                indx += 1
    return(sliced_img_dict) 






def img_splitter_response_matcher(df, response_var, file, expose, num_slice_height = 3, num_slice_width = 4):
                
    """
    
    Task:   Match splitted image to response. If the number of unique response is less than the
            number of images, the responses is repeated until the dimension matches
               
    Argument:
            df: dataframe containing merged profilometer reading, metadata, and image data.
            response_var: the response variable to be predicted. 
            file: image filepath.
            num_slice_height: Number of division accros image height (vertical). Defaults to 3
            num_slice_width: Number of division accros image width (horizontal)). Defaults to 4
            
    Return: A tuple of response variable (target) and predictors (dataset).
            target: dataframe of response
            dataset: the X matrix
            
    """ 

    new_df = df[df["ImgFilepath"] == file]
    splitted_imgs = img_splitter(file, num_slice_height, num_slice_width, expose)
    target = np.resize(new_df[response_var], num_slice_height * num_slice_width)

    for pos in range(num_slice_height * num_slice_width):
        if pos == 0:
            dataset = GLCM_feature_extractor(splitted_imgs[pos+1], "image", expose)
        else:
            f_df = GLCM_feature_extractor(splitted_imgs[pos], "image", expose)
            dataset = pd.concat([dataset,f_df], axis=0)
    return (target, dataset)
     
    
    
    
def generate_design_matrix_using_img_split(df, magnifs = False, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = False):
    
    """
    
    Task:   Generate the design matrix for regression using splitted images with oprion to brighten.
               
    Argument:
            df: dataframe containing merged profilometer reading, metadata, and image data.
            magnifs: Choose magnification to focus on. Default to false for all magnification,
                    50 for 50X magnification and 200 for 200X magnification
            response_var: the response variable to be predicted. Defaults to Ra values
            num_slice_height: Number of division accros image height (vertical). Defaults to 3
            num_slice_width: Number of division accros image width (horizontal)). Defaults to 4
            light_exposure: boolean to brighten 50% of the images.
            
    Return: A tuple of response variable (target) and predictors (dataset).
            target: dataframe of response
            dataset: the X matrix
            
    """   
        
    if magnifs == 200 or magnifs == 50:
        df = df[df["Zoom"] == str(magnifs)]
 
        
    df = df.loc[:,[response_var,"ImgFilepath"]]
    dataset = pd.DataFrame()
    df1 = df.loc[:,["ImgFilepath"]] # isolating only file names so we can select unique one for loop
    df1.drop_duplicates(subset=["ImgFilepath"], inplace = True)
    if light_exposure == True:
        to_expose_files = df1.sample(frac=0.5)
    else:
        to_expose_files = pd.DataFrame({"ImgFilepath":["Nothing to do"]})
        
    expose_list = []
    targets = []
    for pos, file in enumerate(df1["ImgFilepath"]):
        if to_expose_files["ImgFilepath"].str.contains(file).any():
            expose = True
        else:
            expose = False
        expose_unrolled = [expose]  * num_slice_height * num_slice_width
        if ((pos+1) % 10  == 0 or pos == len(file) - 1) or len(df) < 20 :
            print("Processing {0} out of {1} Grinding tool image. Filepath: {2}".format(pos + 1, df1.shape[0], file))  
        if pos == 0:
            res, dataset = img_splitter_response_matcher(df, response_var, file, expose)
        else:
            res, f_df = img_splitter_response_matcher(df, response_var, file, expose)
            dataset = pd.concat([dataset,f_df], axis=0)
        targets.extend(res)
        expose_list.extend(expose_unrolled)
    print("Processed all image file and generated design matrix")
    targets = pd.DataFrame({"y": targets})
    dataset["Exposure"] = expose_list
    return (targets, dataset)


            


# #### **GLCM Feature Extraction**

# In[30]:


# importing GLCM modules
from skimage.feature import graycomatrix, graycoprops
from skimage.measure import shannon_entropy


# In[31]:


########################################################################################
#############       Utility functions for extracting GLCM feature.        ##############
########################################################################################

def GLCM_feature_extractor(img, imgOrFile = "file", expose = False):
        
    """
    
    Task:   Extract GLCM features from an image.
               
    Argument:
            img: Image tensor or image filepath.
            imgOrFile: Boolean for img is image or file. Defaults to file
            expose: Boolean to brighten image or not
            
    Return: 
           df: dataframe containing extracted GLCM features for the image.
            
    """   
        
        
    df = pd.DataFrame()
    if imgOrFile == "file":
        img = imread(img)
    else:
        pass
    if expose == True:
        img = np.resize(img, (img.shape[0], img.shape[1])).astype(np.uint8)
    else:
        img = np.resize(img, (img.shape[0], img.shape[1]))
    distance_list = [[1], [3], [5], [1], [3], [5], [1], [3], [5],[1], [3], [5]]
    angle_list = [[0],[0],[0], [np.pi/4], [np.pi/4], [np.pi/4], [np.pi/2], [np.pi/2], [np.pi/2], [np.pi*3/4], [np.pi*3/4], [np.pi*3/4]]
    glcm_features = ['energy', 'correlation', 'dissimilarity', 'homogeneity', 'contrast', 'ASM']

    for pos, val in enumerate(zip(distance_list, angle_list)):
        distance, angle = val[0], val[1]
        for feature in glcm_features:
            GLCM = graycomatrix(img, distance, angle)  
            GLCM_feature = graycoprops(GLCM, feature)[0]
            feature = feature.title() + str(pos)
            df[feature] = GLCM_feature
    entropy = shannon_entropy(img)
    df['Entropy'+ str(pos)] = entropy
            
    return df    


# In[32]:


########################################################################################
#############       Generating unaggregated dataset with no exposure        ############
########################################################################################


# y,X = generate_design_matrix_using_img_split(df = grinding_img_dataset, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = False)


########################################################################################
#############       Generating unaggregated dataset with exposure           ############
########################################################################################


# y,X = generate_design_matrix_using_img_split(df = grinding_img_dataset, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = True)


########################################################################################
#############       Generating aggaggregated dataset with no exposure       ############
########################################################################################


##y,X = generate_design_matrix_using_img_split(df = grinding_img_agg_dataset, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = False)


########################################################################################
#############       Generating aggaggregated dataset with exposure          ############
########################################################################################


# y,X = generate_design_matrix_using_img_split(df = grinding_img_agg_dataset, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = True)


# In[33]:



########################################################################################
#############             Function for plotting GLCM features               ############
########################################################################################

##def EDA_plotter(X, y = 0, method = "histogram"):
##            
##    """
##    
##    Task:   Generate histograms or scatter plot of features from an image.
##               
##    Argument:
##            X: Dataset of all extracted GLCM features.
##            y: Response variable
##            method: Type of plot. Defaults to histogram
##            
##    Return: 
##           None, however, plots are displayed
##            
##    """   
##        
##        
##    len_X_cols = len(X.columns)
##
##    for i in range(0, len_X_cols,4):
##
##        if (i+4) >= len_X_cols:
##            continue
##        plt.figure(figsize=(12, 3), dpi=80)
##
##        for j in range(4):
##            if method == "histogram":
##                plt.subplot(1,4,j+1).hist(X[X.columns[i + j]])
##            elif method == "scatter":
##                plt.subplot(1,4,j+1).scatter(X[X.columns[i + j]], y)
##            else:
##                pass
##            plt.title("{} of {}{} ".format(method, X.columns[i + j][0:3],X.columns[i + j][-1]))
##        plt.show()


# In[34]:



########################################################################################
#############             Plotting GLCM features Scatter Plots              ############
########################################################################################

##EDA_plotter(X,y, method = "scatter")


# In[35]:



########################################################################################
#############               Plotting GLCM features Histograms               ############
########################################################################################

##EDA_plotter(X, method = "histogram")   


# In[36]:



########################################################################################
#####         Summary statistics for GLCM features and response variable          ######
########################################################################################

##display(X.describe())
##display(y.describe())


# In[52]:


from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import random
from sklearn.utils import shuffle


# In[38]:



def get_index(y, frac = 0.7):
    
    """
    
    Task:   Generate indices for subsetting data in such a way that if X50 in in test, then X200 is also in test
            Generating this way to avoid data leaking.
               
    Argument:
            y: Response variable
            frac: the percentage of data to put in the training set
            
    Return: 
           train_indx: Indices for trainin set
           test_indx: Indices for test set
            
    """   
        
        
    all_indx = [i for i in range(0,len(y))]
    even_indx = [i for i in range(0,len(y)-1,2)]
    frac_indx = round(len(even_indx) * frac)

    train_indx = random.sample(even_indx, frac_indx)
    train_indx = train_indx + [ i+1 for i in train_indx]
    test_indx = np.delete(all_indx, train_indx)
    
    return train_indx, test_indx


# In[39]:




########################################################################################
#####                Removing columns with only one value                         ######
########################################################################################

##print(X.shape)
cols = X.select_dtypes([np.number]).columns
std = X[cols].std()
cols_to_drop = std[std==0].index # if column has the same number then SD is 0
X = X.drop(cols_to_drop, axis=1)
##print(cols_to_drop)
##print(X.shape)
##
##print(len(y))


# #### **Principal Component Regression & Partial Least Squares**

# In[40]:



########################################################################################
#####                Fixing randomness for reproduciblitity                       ######
########################################################################################

random_state = random.sample([i for i in range(0,100)], 1)[0] ## comment out line if you want results to be fixed
##random_state


# In[41]:



#####################################################################################
#####    Training a Principal Component Regression & Partial Least Squares     ######
#####    Regression  model using the training set with possibility of leaks    ######
#####################################################################################

##n_components = 30
##
##y = y["y"]
##
##X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=random_state)
##
##X_train, y_train = shuffle(X_train, y_train, random_state=random_state)
##
##X_test, y_test = shuffle(X_test, y_test, random_state=random_state)
##
##
##pcr = make_pipeline(StandardScaler(), PCA(n_components, whiten=True), LinearRegression())
##pcr.fit(X_train, y_train)
##pca = pcr.named_steps["pca"]  # retrieve the PCA step of the pipeline
##
##pls = PLSRegression(n_components)
##pls.fit(X_train, y_train)


# In[42]:



##########################################################
#####                   Scree Plot                  ######
##########################################################


##PC_values = np.arange(pca.n_components_) + 1
##plt.plot(PC_values, pca.explained_variance_ratio_, 'o-', linewidth=2, color='blue')
##plt.title('Scree Plot')
##plt.xlabel('Principal Component')
##plt.ylabel('Variance Explained')
##plt.show()


# In[43]:



#######################################################################
#####   Plotting PCR and PLS projections onto first Component   #######
#######################################################################


##fig, axes = plt.subplots(1, 2, figsize=(10, 3))
##axes[0].scatter(pca.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[0].scatter(
##    pca.transform(X_test)[:,0], pcr.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[0].set(
##    xlabel="Projected data onto first PCA component", ylabel="y", title="PCR / PCA"
##)
##axes[0].legend()
##axes[1].scatter(pls.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[1].scatter(
##    pls.transform(X_test)[:,0], pls.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[1].set(xlabel="Projected data onto first PLS component", ylabel="y", title="PLS")
##axes[1].legend()
##plt.tight_layout()
##plt.show()
##
##
##
##print(f"PCR out-of-sample R-squared {pcr.score(X_test, y_test):.3f}")
##print(f"PLS out-of-sample R-squared {pls.score(X_test, y_test):.3f}")
##
##print()
##y_pred = pcr.predict(X_test)
##print("PCR out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##y_pred = pls.predict(X_test)
##print("PLS Forest out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))


# In[44]:



#####################################################################################
#####    Training a Principal Component Regression & Partial Least Squares     ######
#####      Regression  model using the training set without any leaks          ######
#####################################################################################


##train_indx, test_indx = get_index(y, frac = 0.7)
##X_train, y_train = X.iloc[train_indx], y.iloc[train_indx]
##X_test, y_test = X.iloc[test_indx], y.iloc[test_indx]
##
##X_train, y_train = shuffle(X_train, y_train, random_state= random_state)
##
##X_test, y_test = shuffle(X_test, y_test, random_state = random_state)
##
##
##pcr = make_pipeline(StandardScaler(), PCA(n_components = 30, whiten=True), LinearRegression())
##pcr.fit(X_train, y_train)
##pca = pcr.named_steps["pca"]  # retrieve the PCA step of the pipeline
##
##pls = PLSRegression(n_components = 30)
##pls.fit(X_train, y_train)


# In[45]:




#######################################################################
#####   Plotting PCR and PLS projections onto first Component   #######
#######################################################################

##fig, axes = plt.subplots(1, 2, figsize=(10, 3))
##axes[0].scatter(pca.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[0].scatter(
##    pca.transform(X_test)[:,0], pcr.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[0].set(
##    xlabel="Projected data onto first PCA component", ylabel="y", title="PCR / PCA"
##)
##axes[0].legend()
##axes[1].scatter(pls.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[1].scatter(
##    pls.transform(X_test)[:,0], pls.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[1].set(xlabel="Projected data onto first PLS component", ylabel="y", title="PLS")
##axes[1].legend()
##plt.tight_layout()
##plt.show()
##
##
##print(f"PCR out-of-sample R-squared {pcr.score(X_test, y_test):.3f}")
##print(f"PLS out-of-sample R-squared {pls.score(X_test, y_test):.3f}")
##
##print()
##
##y_pred = pcr.predict(X_test)
##print("PCR out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##y_pred = pls.predict(X_test)
##print("PLS Forest out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))


# In[46]:



#######################################################
#####                 LASSO Model               #######
#######################################################

from sklearn.linear_model import Lasso
##
##LASSOreg = Lasso(random_state = random_state, max_iter=10000, tol=0.1, selection = 'cyclic').fit(X_train, y_train)
##
##
##print("LASSO out-of-sample R-squared is {} ".format(LASSOreg.score(X_test, y_test)))
##y_pred = LASSOreg.predict(X_test)
##print("\nLASSO out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##Lasso_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, LASSOreg.coef_) if val != 0]
##
##print(f"\nLASSO selected {len(Lasso_selected_features)} variables. They are:")
##for i in Lasso_selected_features:
##    print(i)


# In[47]:



###############################################################
#####          Decision Tree Model [CART] MODEL         #######
###############################################################

from sklearn.tree import DecisionTreeRegressor
##
##DTreg = DecisionTreeRegressor(max_depth = 5, random_state=random_state).fit(X_train, y_train)
##
##print("Decision tree out-of-sample R-squared is {} ".format(DTreg.score(X_test, y_test)))
##y_pred = DTreg.predict(X_test)
##print("\nDecision tree out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##DT_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, DTreg.feature_importances_) if val != 0]
##
##print(f"\nDecision Tree selected {len(DT_selected_features)} variables. They are:")
##for i in DT_selected_features:
##    print(i)


# In[48]:



#######################################################################
#####           Light Gradient Boosted Tree Model               #######
#######################################################################

##from sklearn.model_selection import RandomizedSearchCV
##
##from sklearn.ensemble import GradientBoostingRegressor
##
##from lightgbm import LGBMRegressor
##
##
##LGBMreg = LGBMRegressor(max_depth = 5, random_state=random_state).fit(X_train, y_train)
##
##print("Light Gradient boosted tree out-of-sample R-squared is {} ".format(LGBMreg.score(X_test, y_test)))
##y_pred = LGBMreg.predict(X_test)
##print("\nLight Gradient boosted tree out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##LGBM_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, LGBMreg.feature_importances_) if val != 0]
##
##print(f"\nLight Gradient boosted tree selected {len(LGBM_selected_features)} variables. They are:")
##print(LGBM_selected_features)
##

# In[49]:



#######################################################################
#####                 Gradient Boosted Tree Model               #######
#######################################################################

from sklearn.model_selection import RandomizedSearchCV

from sklearn.ensemble import GradientBoostingRegressor


##
##GBRreg = GradientBoostingRegressor(max_depth = 5, random_state=random_state).fit(X_train, y_train)
##
##print("Gradient boosted tree out-of-sample R-squared is {} ".format(GBRreg.score(X_test, y_test)))
##y_pred = GBRreg.predict(X_test)
##print("\nGradient boosted tree out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##GBR_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, GBRreg.feature_importances_) if val != 0]
##
##print(f"\nGradient boosted tree selected {len(GBR_selected_features)} variables. They are:")
##print(GBR_selected_features)


# In[50]:



#######################################################################
#####                  Random Forest Model                      #######
#######################################################################


from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV

##n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 4)]
##
##max_features = ['auto', 'sqrt']
##
##max_depth = [int(x) for x in np.linspace(10, 110, num = 3)]
##max_depth.append(None)
##
##min_samples_split = [5, 10]
##
##min_samples_leaf = [ 2, 4]
##
##bootstrap = [True, False]
##
##random_grid = {'n_estimators': n_estimators,
##               'max_features': max_features,
##               'max_depth': max_depth,
##               'min_samples_split': min_samples_split,
##               'min_samples_leaf': min_samples_leaf,
##               'bootstrap': bootstrap}
##
##RFreg = RandomForestRegressor()
##
##RFreg = RandomizedSearchCV(estimator = RFreg, param_distributions = random_grid, n_iter = 100,
##                               cv = 5, verbose=0, random_state=random_state, n_jobs = -1).fit(X_train, y_train)
##
##
##print("Random Forest out-of-sample R-squared is {} ".format(RFreg.score(X_test, y_test)))
##y_pred = RFreg.predict(X_test)
##print("\nRandom Forest out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##RFreg_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, RFreg.best_estimator_.feature_importances_) if val != 0]
##
##print(f"\nRandom Forest tree selected {len(RFreg_selected_features)} variables. They are:")
##print(RFreg_selected_features)


# In[51]:



#######################################################################
#####                  Stacked Regression                       #######
#######################################################################

from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV
##
##estimators = [
##    ("pls", pls),
##    ("Decision Tree", DTreg),
##    ("Gradient Boosting", GBRreg),
##    ("Light Gradient Boosting", LGBMreg),
##    ("Random Forest", RFreg.best_estimator_)
##]
##
##stacking_regressor = StackingRegressor(estimators = estimators, final_estimator = RidgeCV()).fit(X_train, y_train)
##
##
##print("Stacked Regressor out-of-sample R-squared is {} ".format(stacking_regressor.score(X_test, y_test)))
##y_pred = stacking_regressor.predict(X_test)
##print("\nStacked Regressor out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))


# #### Outliers
# 
# We sought for outliers in the model and it appears there are a couple of them. The rows from 12  to 23 with all coming from the build angle of 15. We exclude these images will redo the analysis.

# In[68]:


##grinding_img_dataset[grinding_img_dataset["Ra"]>17]


# In[72]:


###################################################################################################
####      Aggregate the profilometer reading excluding outliers into a new dataframe          #####
###################################################################################################

img_profilometer_data_agg = aggregate_by_img(img_profilometer_data[img_profilometer_data["Ra"]<20])

##display(img_profilometer_data_agg.head())
##print(img_profilometer_data_agg.shape)


# In[73]:


##########################################################################################################################
####   Merge (only intersection) aggregated profilometer dataset with corresponding images. One reading per image    #####
####                          Dispay merged dataset including number of rows and columns                             #####
##########################################################################################################################

grinding_img_agg_dataset = pd.merge(left = img_profilometer_data_agg, right = img_metadata, how = "inner", on= ["Capturetime", 'Buildangle','Facenumber'], indicator = True)

##display(grinding_img_agg_dataset)
##print(grinding_img_agg_dataset.shape)


# In[75]:


################################################################################
####           Descriptive statistics of aggregated dataframe              #####
################################################################################

##display(grinding_img_agg_dataset.describe())


# In[78]:


########################################################################################
#############       Generating aggaggregated dataset with no exposure       ############
########################################################################################


y,X = generate_design_matrix_using_img_split(df = grinding_img_agg_dataset, num_slice_height = 3, num_slice_width = 4, response_var = "Ra", light_exposure = False)


# In[77]:



########################################################################################
#############             Plotting GLCM features Scatter Plots              ############
########################################################################################

# EDA_plotter(X,y, method = "scatter")


# In[83]:



#####################################################################################
#####    Training a Principal Component Regression & Partial Least Squares     ######
#####      Regression  model using the training set without any leaks          ######
#####################################################################################

y = y["y"]
train_indx, test_indx = get_index(y, frac = 0.7)
X_train, y_train = X.iloc[train_indx], y.iloc[train_indx]
X_test, y_test = X.iloc[test_indx], y.iloc[test_indx]

X_train, y_train = shuffle(X_train, y_train, random_state= random_state)

X_test, y_test = shuffle(X_test, y_test, random_state = random_state)


pcr = make_pipeline(StandardScaler(), PCA(n_components = 30, whiten=True), LinearRegression())
pcr.fit(X_train, y_train)
pca = pcr.named_steps["pca"]  # retrieve the PCA step of the pipeline

pls = PLSRegression(n_components = 30)
pls.fit(X_train, y_train)



#######################################################################
#####   Plotting PCR and PLS projections onto first Component   #######
#######################################################################

##fig, axes = plt.subplots(1, 2, figsize=(10, 3))
##axes[0].scatter(pca.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[0].scatter(
##    pca.transform(X_test)[:,0], pcr.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[0].set(
##    xlabel="Projected data onto first PCA component", ylabel="y", title="PCR / PCA"
##)
##axes[0].legend()
##axes[1].scatter(pls.transform(X_test)[:,0], y_test, alpha=0.3, label="ground truth")
##axes[1].scatter(
##    pls.transform(X_test)[:,0], pls.predict(X_test), alpha=0.3, label="predictions"
##)
##axes[1].set(xlabel="Projected data onto first PLS component", ylabel="y", title="PLS")
##axes[1].legend()
##plt.tight_layout()
##plt.show()
##
##
##print(f"PCR out-of-sample R-squared {pcr.score(X_test, y_test):.3f}")
##print(f"PLS out-of-sample R-squared {pls.score(X_test, y_test):.3f}")
##
##print()
##
##y_pred = pcr.predict(X_test)
##print("PCR out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##y_pred = pls.predict(X_test)
##print("PLS Forest out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))


# In[84]:



#######################################################
#####                 LASSO Model               #######
#######################################################

from sklearn.linear_model import LassoCV, Lasso

LASSOreg = LassoCV(random_state = random_state, max_iter=10000, tol=0.1, selection = 'cyclic').fit(X_train, y_train)


##print("LASSO out-of-sample R-squared is {} ".format(LASSOreg.score(X_test, y_test)))
##y_pred = LASSOreg.predict(X_test)
##print("\nLASSO out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##Lasso_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, LASSOreg.coef_) if val != 0]
##
##print(f"\nLASSO selected {len(Lasso_selected_features)} variables. They are:")
##for i in Lasso_selected_features:
##    print(i)


# In[85]:



###############################################################
#####          Decision Tree Model [CART] MODEL         #######
###############################################################

from sklearn.tree import DecisionTreeRegressor

DTreg = DecisionTreeRegressor(max_depth = 5, random_state=random_state).fit(X_train, y_train)

##print("Decision tree out-of-sample R-squared is {} ".format(DTreg.score(X_test, y_test)))
##y_pred = DTreg.predict(X_test)
##print("\nDecision tree out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##DT_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, DTreg.feature_importances_) if val != 0]
##
##print(f"\nDecision Tree selected {len(DT_selected_features)} variables. They are:")
##for i in DT_selected_features:
##    print(i)


# In[92]:



#######################################################################
#####                 Gradient Boosted Tree Model               #######
#######################################################################

max_depth = [int(x) for x in np.linspace(10, 110, num = 3)]
max_depth.append(5)

random_grid = {
    "n_estimators": [int(x) for x in np.linspace(start = 200, stop = 2000, num = 4)],
    "max_depth": max_depth,
    "min_samples_split": [5, 10],
    "learning_rate": [0.01],
    "loss": ["squared_error"],
}



GBRreg = RandomizedSearchCV(estimator = GradientBoostingRegressor(), param_distributions = random_grid, n_iter = 1000,
                               cv = 5, verbose=0, random_state=random_state, n_jobs = -1).fit(X_train, y_train)


##print("Gradient boosted tree out-of-sample R-squared is {} ".format(GBRreg.score(X_test, y_test)))
##y_pred = GBRreg.predict(X_test)
##print("\nGradient boosted tree out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##GBR_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, GBRreg.best_estimator_.feature_importances_) if val != 0]
##
##print(f"\nGradient boosted tree selected {len(GBR_selected_features)} variables. They are:")
##print(GBR_selected_features)


# In[88]:



#######################################################################
#####                  Random Forest Model                      #######
#######################################################################


n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 4)]

max_features = ['auto', 'sqrt']

max_depth = [int(x) for x in np.linspace(10, 110, num = 3)]
max_depth.append(None)

min_samples_split = [5, 10]

min_samples_leaf = [ 2, 4]

bootstrap = [True, False]

random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

RFreg = RandomForestRegressor()

RFreg = RandomizedSearchCV(estimator = RFreg, param_distributions = random_grid, n_iter = 100,
                               cv = 5, verbose=0, random_state=random_state, n_jobs = -1).fit(X_train, y_train)


##print("Random Forest out-of-sample R-squared is {} ".format(RFreg.score(X_test, y_test)))
##y_pred = RFreg.predict(X_test)
##print("\nRandom Forest out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))
##
##RFreg_selected_features = [key for key,val in zip(LASSOreg.feature_names_in_, RFreg.best_estimator_.feature_importances_) if val != 0]
##
##print(f"\nRandom Forest tree selected {len(RFreg_selected_features)} variables. They are:")
##print(RFreg_selected_features)


# In[93]:



#######################################################################
#####                  Stacked Regression                       #######
#######################################################################

from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import RidgeCV

estimators = [
    ("pls", pls),
    ("Decision Tree", DTreg),
    ("Gradient Boosting", GBRreg.best_estimator_),
    ("Random Forest", RFreg.best_estimator_)
]

stacking_regressor = StackingRegressor(estimators = estimators, final_estimator = RidgeCV()).fit(X_train, y_train)


##print("Stacked Regressor out-of-sample R-squared is {} ".format(stacking_regressor.score(X_test, y_test)))
##y_pred = stacking_regressor.predict(X_test)
##print("\nStacked Regressor out-of-sample mean squared error is {} ".format(mean_squared_error(y_test, y_pred)))


# In[123]:



#######################################################################
#####                  Prediction Endpoint                       ######
#######################################################################


def get_prediction(folder_path = "Linke_Prediction", method = stacking_regressor):
        
    """
    
    Task:   Predict the response for image (jpg) in folder_path .
               
    Argument:
            folder_path (str): The folder containing the images for prediction.
                               Defaults to Linke_Prediction.
            
    Return: 
            df (pd Dataframe): dataframe of filepath and the corresponding prediction

            
    """ 
    folder_path += "/*.jpg"
    
    filepaths = glob(folder_path, recursive=True)
    fake_response = [i for i in range(len(filepaths))]
    img_metadata = pd.DataFrame({"ImgFilepath": filepaths, "fakeResponse": fake_response})
    top_level = folder_path.split("/")[0]
    print(f"\nFound {len(img_metadata)} files for prediction in {top_level} folder\n")
    
    
    num_slice_height = 3
    num_slice_width = 4
    indx,new_X = generate_design_matrix_using_img_split(df = img_metadata, num_slice_height = num_slice_height,
                                                 num_slice_width = num_slice_width, response_var = "fakeResponse", light_exposure = False)
    y_pred = stacking_regressor.predict(new_X)
    final_pred = []
    for count, filepath in enumerate(filepaths):
        
        if len(filepaths) == 1:
            
            final_pred.append(np.mean(y_pred))         

        start_indx = num_slice_height * num_slice_width * (count)
        end_indx = num_slice_height * num_slice_width * (count + 1)
        temp_pred = np.mean(y_pred[start_indx:end_indx])
        final_pred.append(temp_pred)
    df = pd.DataFrame({"Filepath":filepaths, "Prediction": final_pred})
    return(df)
 


# In[124]:



#######################################################################
#####          Sample usage of prediction endpoint               ######
#######################################################################

get_prediction("Linke_Prediction")

