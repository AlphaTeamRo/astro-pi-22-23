# Post-processing scripts
### Used to process the received data back on earth

Needs python <3.10 as 3.11 does not support cv2

## Testing(before receiving data)

- Create the directory structure as per folder_structure.txt
(Already done). Make sure to delete .gitkeep files from all empty directories

- Download raw images [here](https://s3.eu-west-2.amazonaws.com/learning-resources-production/projects/astropi-ndvi/2cc9d1033d9c4f05388632e7912a4bb5531b3d94/en/resources/astropi-ndvi-en-resources.zip) (inputted into "images" folder)

# Post-processing steps

1. Place the received "auto-classify" directory in the root folder

2. Convert raw images to NDVI

    ```
    cd 1-convert-to-ndvi
    python3 convert_to_ndvi.py
    cd ..
    ```

3. Add image mask (transparent should be used for panoramas, BLUE for pixelcount. TODO)
    ```
    cd 2-mask
    python3 add_mask.py
    cd ..
    ```

3. Pixel count
    ```
    cd 3-pixelcount
    python3 pixelcount.py
    cd ..
    ```
