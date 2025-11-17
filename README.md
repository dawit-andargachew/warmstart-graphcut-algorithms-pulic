# Image Segmentation Based On Graph Cut Algorithms With Warm-Start
# Warm-Start Graph Cut for Image Segmentation

This repo is a restructured and beginner-friendly version of the implementation for the paper [**"Predictive Flows for Faster Ford-Fulkerson"**](https://arxiv.org/abs/2303.00837) by Yuyan Wang, Siddhartha Banerjee, and David P. Williamson.

**Original Repository**: [wang-yuyan/warmstart-graphcut-algorithms-pulic](https://github.com/wang-yuyan/warmstart-graphcut-algorithms-pulic)


## Background

During grad school, I took a course on **advanced algorithms**, where we explored **Learning-Augmented Algorithms** (aka **algorithms with predictions**). One of our tasks was to choose a research paper, read it in detail, and present it. I picked this paper, [**“Predictive Flows for Faster Ford-Fulkerson,”**](https://arxiv.org/abs/2303.00837) and, after spending some time understanding the ideas and running the authors’ code, I decided to clean up the structure and documentation to make the project easier to follow, so that others could understand and appreciate how cool and elegant the design of this algorithm is.

### Hope you find it as interesting as I did!

---

## What's This About?

This algorithm is about **learning-augmented algorithms** applied to image segmentation. Image segmentation is a core problem in computer vision that aims at separating an object from the background in a given image. It's formulated as a max-flow/min-cut problem using a graph built from pixels.

Here's the cool part: when you're processing a sequence of images (like video frames), each image is only a minor variation of the previous one. The differences are subtle, like a small shift in perspective or lighting, but the overall structure remains constant.

Since each image is similar, the algorithm uses the previous image's result to make the next image computation faster. Instead of starting from scratch every time, it uses the previous result as a starting point, making it much faster. Classical algorithms start from scratch all the time, even though each image is just a slight change in angle or lighting. This algorithm makes use of that similarity to be more efficient.


---

## Prerequisites

Make sure you have a Python 3 environment with dependencies from `requirements.txt` installed.
```bash
pip install -r requirements.txt
```

---





## Dataset

The dataset is available at the [Pattern Recognition and Image Processing dataset from the University of Freiburg](https://lmb.informatik.uni-freiburg.de/resources/datasets/sequences.en.html) (Scroll down to see the individual groups).

The paper mentions four groups: BIRDHOUSE, HEAD, SHOE, and DOG. However, for the sake of simplicity, this implementation includes only the **BIRDHOUSE**, **HEAD**, and **SHOE** groups. The **DOG** group is not included because it’s a large video (**4.8 GB**), and the remaining three groups are sufficient for understanding the algorithm.

Each group contains consecutive images, and I've included 10 images per group for testing and experimentation. If you'd like to use more images, feel free to download the dataset, extract the frames, and place them in the appropriate folder.

The directory structure looks like this:


```
sequential_datasets/
├── birdhouse/
├── head/
└── shoe/
```

If you'd like to add your own group, just create a new folder inside the `sequential_datasets` directory and add the images!

---

## Quick Overview of Commands

The commands I've mentioned here can be used right after the repo is cloned. If you'd like to try other groups, just change the name to respective group names (e.g., replace `birdhouse` with `head` or `shoe`).

- `python image_cropping.py -g birdhouse` - Crop and grayscale images
- `python imagesegmentation.py -i birdhouse_001_cropped.jpg -g birdhouse -s 30 -l no` - Segment one image with manual seeding
- `python warmstart.py -g birdhouse -s 30` - Run warm-start on the entire sequence
- `python average.py -g birdhouse` - Generate performance report


## Quick overview of each files

- `image_cropping.py` - Image preprocessing: crops and grayscales all images in a sequence
- `imagesegmentation.py` - Performs segmentation on a single image (used for the baseline/cold-start)
- `warmstart.py` - Implements the warm-start algorithm for the entire sequence
- `average.py` - Calculates averages from experiment results
- `augmentingPath.py` - Core Ford-Fulkerson implementation



---

### Step 1: Crop the Original RGB Images
```bash
python image_cropping.py -g birdhouse
```

Replace `birdhouse` with other group names like `head` or `shoe` if needed.

<!-- **What happens:** -->
After running the above command, a folder for the respective group will be created containing grayscale cropped images. In our case, it will be `birdhouse_cropped` and contains cropped images for each image found in the `birdhouse` group.

---

### Step 2: Run Image Segmentation Algorithm on One Image
```bash
python imagesegmentation.py -i birdhouse_001_cropped.jpg -g birdhouse -s 30 -l no
```

- Replace `birdhouse_001_cropped.jpg` and `birdhouse` with respective names
- `30` can be `60` or `120`—it determines the size of the resized image (30×30, 60×60, or 120×120 pixels)
- `-l no` means we're NOT loading seeds from a file (we'll mark them manually)

<!-- **What happens:** -->
This step generates an image that can be used to initiate the warm-starting phase. It also creates a folder `birdhouse_cropped/30` (in our case) and puts an image inside it which is used to seed the rest of the images. At this stage, we're just marking the first image manually—what's the object and what's the background.

**Interactive Part:** 
After running this command, a popup window will appear:
1. Place red dots on the object, then press **ESC**.
2. On the same window, place green dots on the background, then press **ESC** when done.


The script then runs graph-cut using these seeds.

#### Why Do We Mark Points?

These points are user seeds for segmentation:
- **Red dots** = foreground (object you want to segment)
- **Green dots** = background (area to exclude)

Graph-cut (and Ford-Fulkerson behind it) needs these seeds to know where to start the max-flow/min-cut computation. Without seeds, the algorithm wouldn't know what to segment.


---

### Step 3: Run Warm-Starting
```bash
python warmstart.py -g birdhouse -s 30
```

- `30` could be `60` or `120` as well

#### **❗ Important**: Make sure you use the same number as in Step 2. If you used `-s 30` in Step 2, use `-s 30` here.

**What happens:**

Assuming we have 10 images in the sequence, the algorithm:
1. Uses the first image to warm-start the second image segmentation
2. Uses the second image result to warm-start the third
3. Continues like this—each previous result is used as input to the current image until the last one

By the end of this, the folder `birdhouse_cuts/30` contains the segmentation result for each image (a total of 10 images).

#### Why Warm-Start?

Instead of starting Ford-Fulkerson from scratch for every image, it uses the previous image's max-flow as a starting point → much faster segmentation. The first image needs the seeds, but segmentation is automatic for the rest of the sequence—no need to mark seeds again.

---

### Step 4: Generate Performance Report
```bash
python average.py -g birdhouse
```

This generates the average time taken to process each image and puts the report in a `.txt` file. The report can be found as `all_path_averages.txt` and `all_time_avearages.txt` undre `sequential_datasets` folder.

---

## Example Images

### Original RGB Image
![original RGB image you want to segment](sequential_datasets/birdhouse/birdhouse_001.jpg)

### After Step 1: Cropped Image
![cropped and grayscaled image](birdhouse(sample_output)/birdhouse_cropped/birdhouse_001_cropped.jpg)

### After Step 2: Seeded Image
![image showing red foreground seeds and green background seeds](birdhouse(sample_output)/birdhouse_seeded/120/birdhouse_001_cropped_seeded.jpg)

### After Step 3: Segmentation Result
![final segmented image with object separated from background](birdhouse(sample_output)/birdhouse_cuts/120/birdhouse_001_cropped_cuts.jpg)



---

## Credits and Acknowledgments

This work is based on:
- **Paper**: [Predictive Flows for Faster Ford-Fulkerson](https://arxiv.org/abs/2303.00837) by Yuyan Wang, Siddhartha Banerjee, and David P. Williamson
- **Original Repository**: [wang-yuyan/warmstart-graphcut-algorithms-pulic](https://github.com/wang-yuyan/warmstart-graphcut-algorithms-pulic)

---

#### More detailed descriptions can be found in the code files themselves.

#### *That's it! The algorithm is pretty clever—by reusing information from previous frames, it dramatically speeds up video segmentation tasks. Pretty cool, right?*
