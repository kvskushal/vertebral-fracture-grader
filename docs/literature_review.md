# Literature Review

## Project

Automated Genant grading of thoracolumbar vertebrae from non-contrast CT.

## Purpose

This literature review explains the medical grading standard, available

datasets, vertebra-localization methods, fracture-classification methods,

and appropriate training techniques for an ordinal grading model.

# Paper 1: Genant Semiquantitative Grading Standard

## Citation

Genant, H. K., Wu, C. Y., van Kuijk, C., & Nevitt, M. C. (1993).

Vertebral fracture assessment using a semiquantitative technique.

Journal of Bone and Mineral Research, 8(9), 1137–1148.

https://doi.org/10.1002/jbmr.5650080915

## Research question

How can radiologists consistently identify and grade vertebral fractures

using the appearance and height loss of each vertebral body?

## Important vocabulary

- Vertebra: One of the bones that forms the spine.

- Vertebral body: The large, weight-bearing part of a vertebra.

- Fracture: A break or collapse in a bone.

- Height loss: How much shorter a vertebral body has become.

- Semiquantitative: A method that combines visual judgment with approximate measurements.

- Ground truth: The correct label that the AI is trained to predict.

## Genant grades

| Grade | Meaning | Approximate vertebral height loss |
|---|---|---:|
| 0 | Normal | Less than 20% |
| 1 | Mild fracture | 20–25% |
| 2 | Moderate fracture | 25–40% |
| 3 | Severe fracture | More than 40% |

## Common vertebral deformity shapes

1. Wedge deformity:

   The front of the vertebral body loses more height than the back.

2. Biconcave deformity:

   The middle of the vertebral body loses height while the front and back

   remain taller.

3. Crush deformity:

   Most or all of the vertebral body loses height.

## Summary

Genant and colleagues presented a semiquantitative method for grading

vertebral fractures. The method assigns a grade from 0 to 3 based on the

appearance of a vertebral body and the approximate amount of height loss.

Grade 0 represents a normal vertebra. Grade 1 represents mild deformity,

grade 2 represents moderate deformity, and grade 3 represents severe

collapse.

The researchers tested whether different observers could apply the method

consistently. Three observers examined spinal radiographs from 57

postmenopausal women between 65 and 75 years old. The same observer showed

excellent consistency when repeating the assessment, while different

observers showed good agreement. The authors concluded that the method

could be reliable when observers followed clearly defined criteria.

The method is semiquantitative because it is not based only on an exact

measurement. The observer also examines the shape of the vertebral body.

Common patterns include wedge, biconcave, and crush deformities. This

visual examination helps prevent normal anatomical differences from being

incorrectly labeled as fractures.

This paper defines the ground-truth labels for the proposed AI system.

Every vertebra from T4 through L4 must receive a grade from 0 to 3. Because

the grades represent increasing severity, they should be treated as

ordered categories. The model should therefore be trained with an

ordinal-aware loss rather than treating all mistakes as equally serious.

One limitation is that the original technique was developed using lateral

radiographs, while this project uses three-dimensional CT volumes.

Therefore, the project must document how the dataset's radiologist labels

apply the Genant standard to CT images. Mild grade-1 cases may be

especially difficult because they are close to the boundary between a

normal vertebra and a fracture.

# Paper 2: The VerSe Benchmark

## Citation

Sekuboyina, A., Husseini, M. E., Bayat, A., Löffler, M., Liebl, H.,

Li, H., Tetteh, G., et al. (2021). VerSe: A vertebrae labelling and

segmentation benchmark for multi-detector CT images.

Medical Image Analysis, 73, 102166.

https://doi.org/10.1016/j.media.2021.102166

Free paper:

https://arxiv.org/abs/2001.09193

Official project:

https://github.com/anjany/verse

## Research question

How accurately can automated systems find, name, and separate individual

vertebrae in CT scans?

## Important vocabulary

- Localization: Finding the three-dimensional location of a vertebra.

- Labeling: Giving a vertebra its correct name, such as T12 or L1.

- Segmentation: Marking every voxel belonging to a vertebra.

- Voxel: A three-dimensional pixel in a CT volume.

- Mask: An image marking the voxels belonging to an object.

- Centroid: A point near the center of an object.

- Field of view: The part of the body included in a CT scan.

- Benchmark: A shared test used to compare computer systems fairly.

- Anatomical variation: A natural difference in a person's anatomy.

## Dataset

The VerSe benchmark combines the 2019 and 2020 VerSe challenges. It

contains 374 CT scans from 355 patients and 4,505 individually annotated

vertebrae. Its annotations include vertebral names, center coordinates,

and voxel-level segmentation masks.

A typical VerSe case includes:

1. A CT volume.

2. A segmentation mask.

3. A JSON file containing vertebral labels and centroids.

4. A PNG preview of the annotations.

## Summary

Sekuboyina and colleagues created the VerSe benchmark to improve automated

vertebral labeling and segmentation. These tasks are necessary because a

fracture-grading model cannot grade a vertebra until it knows where the

vertebra is and what anatomical name it has.

The first task is localization, which finds the position of a vertebra.

The second task is labeling, which identifies it as C1, T12, L1, or

another spinal level. The third task is segmentation, which creates a

mask around the vertebra. A mask lets the system separate that vertebra

from nearby bones and tissue.

Automated spine processing is difficult because CT scans are not all the

same. They may come from different scanners, include different portions

of the spine, or contain fractures, implants, cement, noise, and unusual

anatomy. Some people may have an extra thoracic or lumbar vertebra. If the

system misidentifies one vertebra, the names of several nearby vertebrae

may also become incorrect.

The main lesson from VerSe is that a system must handle rare anatomical

variations. A system may work well on ordinary cases but fail when the

patient's anatomy is unusual. Testing must examine unusual cases instead

of relying only on average performance.

VerSe supports Stage A of this project: localization, labeling, and

segmentation. It is not the primary source of Genant fracture grades.

A separate dataset containing radiologist-assigned grades is needed to

train Stage B.

The project will initially use TotalSegmentator for Stage A. After it

creates a labeled vertebral mask, the program will crop the vertebra,

add padding, resample it to 64 by 64 by 64 voxels, and send the crop to

the grading model.

The complete pipeline is:

Full CT scan -> localization -> labeling -> segmentation -> crop -> grade

A limitation is that accurate segmentation does not guarantee accurate

fracture grading. The segmentation and grading systems must be evaluated

separately. Rare anatomy may also produce incorrect vertebral names even

when the segmentation masks appear correct.

## Connection to the project

VerSe will help the project:

1. Locate the spine.

2. Identify vertebrae T4 through L4.

3. Produce a separate mask for every vertebra.

4. Create a 64 by 64 by 64 crop from each mask.

5. Send each crop to the Genant-grading model.

## License and provenance

Dataset: VerSe 2019 and VerSe 2020

Source:

https://github.com/anjany/verse

Dataset license: CC BY-SA 4.0

Helper-code license: MIT

Planned use:

Training or testing vertebral localization, labeling, and segmentation.

The large CT files will be stored outside GitHub. GitHub will contain only

the download instructions, license information, manifests, and code.

# Paper 3: Löffler Vertebral Segmentation and Fracture-Grading Dataset

## Citation

Löffler, M. T., Sekuboyina, A., Jacob, A., Grau, A. L., Scharr, A.,

El Husseini, M., Kallweit, M., Zimmer, C., Baum, T., and Kirschke, J. S.

(2020). A Vertebral Segmentation Dataset with Fracture Grading.

Radiology: Artificial Intelligence, 2(4), e190138.

https://doi.org/10.1148/ryai.2020190138

Full paper:

https://pubs.rsna.org/doi/full/10.1148/ryai.2020190138

Dataset:

https://osf.io/nqjyw/

## Research question

Can a public CT dataset provide accurate vertebral masks and fracture

grades for training automated spine-analysis systems?

## Important vocabulary

- Annotation: Information added to an image by an expert.

- Fracture grade: A number describing fracture severity.

- Consensus: An answer on which multiple experts agree.

- Class imbalance: Some grades appear much more often than others.

- Data leakage: Test-patient information accidentally enters training data.

- Contrast material: A substance that makes structures more visible on CT.

## Dataset

The dataset contains:

- 160 CT image series

- 141 patients

- 1,725 fully visible vertebrae

- 220 cervical vertebrae

- 884 thoracic vertebrae

- 621 lumbar vertebrae

- Vertebral segmentation masks

- Vertebral names and center coordinates

- Genant grades for thoracolumbar vertebrae

- Fracture-shape labels

- Foreign-material annotations

- Lumbar bone-mineral-density measurements

The original split contains:

- Training: 80 image series and 862 vertebrae

- Validation: 40 image series and 434 vertebrae

- Test: 40 image series and 429 vertebrae

All scans belonging to one patient were kept in the same split. This

prevents patient-level data leakage.

## How the masks were created

The researchers first used an automated system to find, label, and segment

the vertebrae. Trained medical students corrected the computer-generated

masks. Neuroradiologists then reviewed the corrections. Metal implants and

bone cement were excluded from the vertebral bone masks.

This human-machine method was faster than drawing every mask from the

beginning while still including expert review.

## Fracture grading

Two radiologists evaluated the thoracolumbar vertebrae together using the

Genant standard.

| Grade | Meaning | Height loss |
|---|---|---:|
| 0 | Normal | Less than 20% |
| 1 | Mild | At least 20% but less than 25% |
| 2 | Moderate | At least 25% but less than 40% |
| 3 | Severe | At least 40% |

They also recorded wedge, biconcave, and crush fracture shapes.

Developmental abnormalities were not labeled as fractures.

## Summary

Löffler and colleagues created a public spine CT dataset containing

vertebral segmentation masks and per-vertebra fracture information. The

dataset supports machine-learning systems for vertebral segmentation and

fracture detection.

It contains 160 CT image series from 141 patients and 1,725 fully visible

vertebrae. The scans were divided into training, validation, and test

groups. Scans belonging to the same patient were kept together. This is

important because allowing one patient's scans in both training and

testing would make performance appear better than it truly is.

The masks were produced using artificial intelligence followed by human

correction. A computer created an initial segmentation. Medical students

corrected the result, and neuroradiologists reviewed the masks. Two

radiologists then evaluated thoracolumbar vertebrae using the Genant

grading method.

This dataset is useful because the mask tells the program where a

vertebra is, while the Genant annotation supplies the correct training

answer. The program can crop an individual vertebra using its mask and

pair that crop with its grade.

The dataset also has limitations. It is small for a three-dimensional

neural network. Grade 1 fractures are more common than severe fractures,

which creates class imbalance. Patients younger than 30 and patients with

bone metastases were excluded. Some scans contain contrast material even

though this project's final target is non-contrast CT.

This dataset is also part of VerSe 2019. VerSe 2019 and the Löffler

dataset must not be counted as two completely separate groups. Patient and

scan identifiers must be checked to prevent duplicate images and data

leakage.

## Connection to the project

This will be a primary labeled dataset for the grading model.

For each vertebra, the preparation program will:

1. Read the patient and scan identifiers.

2. Read the CT volume.

3. Read the vertebral mask and anatomical name.

4. Read the Genant grade.

5. Crop the vertebra with padding.

6. Resample the crop to 64 by 64 by 64 voxels.

7. Record its grade and source in a manifest.

8. Keep the entire patient in only one data split.

Non-contrast scans will be identified when possible. Contrast and

non-contrast scans must not be mixed without documenting and testing the

difference.

## License and provenance

Dataset:

Löffler Vertebral Segmentation Dataset with Fracture Grading

Source:

https://osf.io/nqjyw/

Data license:

CC BY-SA 4.0

Article license:

CC BY 4.0

Planned use:

Training and evaluating the per-vertebra Genant-grading model.

The CT scans, masks, and generated crops will remain outside GitHub.

GitHub will contain code, manifests, licenses, patient-level split files,

and evaluation reports.

# Paper 4: Tomita Deep-Learning Fracture Detection

## Citation

Tomita, N., Cheung, Y. Y., and Hassanpour, S. (2018).

Deep neural networks for automatic detection of osteoporotic vertebral

fractures on CT scans. Computers in Biology and Medicine, 98, 8-15.

https://doi.org/10.1016/j.compbiomed.2018.05.011

Paper:

https://www.sciencedirect.com/science/article/abs/pii/S0010482518301185

## Research question

Can a deep-learning system examine chest, abdominal, and pelvic CT scans

and determine whether a patient has an osteoporotic vertebral fracture?

## Important vocabulary

- CNN: A neural network that learns visual features from images.

- RNN: A neural network designed to process an ordered sequence.

- LSTM: A type of RNN that remembers information across a sequence.

- Feature extraction: Finding useful patterns in an image.

- Feature aggregation: Combining information from multiple images.

- F1 score: A measurement balancing precision and sensitivity.

- Incidental finding: A medical problem found while examining something else.

## Method and results

The system used a CNN to examine individual two-dimensional sagittal CT

images. The CNN produced features describing each image. An LSTM then

combined the sequence of features and predicted whether the complete CT

scan contained an osteoporotic vertebral fracture.

The study used:

- 1,432 CT scans

- 10,546 sagittal two-dimensional images

- A held-out test set of 129 CT scans

- Chest, abdominal, and pelvic examinations

The best model achieved:

- Accuracy: 89.2%

- F1 score: 90.8%

The reported performance was similar to that of practicing radiologists

on the test set.

## Summary

Tomita and colleagues developed an automatic system for finding

osteoporotic vertebral fractures on routine CT examinations. These

fractures are frequently missed because the CT may have been ordered for

another medical reason and the fracture may not produce symptoms.

The system used two kinds of neural networks. First, a CNN examined

individual sagittal CT images and extracted visual features. Second, an

LSTM combined information from the ordered sequence of images and made

one prediction for the entire CT scan.

This design demonstrated that deep learning could screen existing CT

examinations without requiring additional imaging or radiation. A

suspicious scan could be flagged for review by a radiologist.

However, the model produced a patient-level binary answer: fracture

present or fracture absent. It did not identify every vertebral level and

did not assign individual Genant grades from 0 through 3. It was also

developed using data from one medical institution, so performance at

different hospitals and with different scanners was uncertain.

This paper explains why some earlier systems used an RNN. They processed

an ordered sequence of two-dimensional images. The current project will

instead process one three-dimensional vertebral crop at a time. Therefore,

a three-dimensional CNN is more appropriate than an RNN for the grading

model.

## Connection to this project

Tomita supports the idea that deep learning can detect fractures on CT.

However, this project needs a more detailed output.

Tomita output:

One CT scan -> fracture present or absent

This project output:

Each T4-L4 vertebra -> Genant grade 0, 1, 2, or 3

The project will use a three-dimensional CNN on individual vertebral crops.

It will not use an RNN as its main classifier.

# Paper 5: Nicolaes Three-Dimensional CNN

## Citation

Nicolaes, J., Raeymaeckers, S., Robben, D., Wilms, G.,

Vandermeulen, D., Libanati, C., and Debois, M. (2020).

Detection of vertebral fractures in CT using 3D convolutional neural

networks. In Computational Methods and Clinical Applications for Spine

Imaging, Lecture Notes in Computer Science, 11963, 3-14.

https://doi.org/10.1007/978-3-030-39752-4_1

Free preprint:

https://arxiv.org/abs/1911.01816

## Research question

Can a three-dimensional CNN learn the spatial appearance of vertebral

fractures directly from CT volumes?

## Important vocabulary

- 3D CNN: A CNN that examines width, height, and depth.

- Spatial information: Information about three-dimensional shape and position.

- Voxel classification: Predicting a label for locations in a 3D image.

- Cross-validation: Repeating training and testing with different data portions.

- AUC: A measurement of how well a model separates positive and negative cases.

- Opportunistic screening: Checking an existing scan for an additional disease.

## Method and results

The researchers trained a three-dimensional CNN using 90 CT cases. The

training data were created semi-automatically using information available

in radiology reports.

The system learned three-dimensional feature maps and localized possible

fractures. In five-fold cross-validation, it achieved:

- Patient-level AUC: 0.95

- Vertebra-level AUC: 0.93

## Summary

Nicolaes and colleagues created a system that detected vertebral fractures

using three-dimensional CT information. Earlier systems often used flat

sagittal images or several nearby slices. This method allowed the network

to learn the complete three-dimensional appearance of a fracture.

Three-dimensional information is valuable because vertebrae are solid

objects. A fracture can change the front, middle, back, sides, and internal

structure of a vertebral body. A flat image may not show every important

change.

The model also localized its predictions. This is useful because a

radiologist needs to know which vertebra caused the positive result.

Localization makes the output more understandable than a single unexplained

patient-level answer.

The method was evaluated using five-fold cross-validation. It produced an

AUC of 0.95 for patient-level detection and 0.93 for vertebra-level

detection. These results showed that learned three-dimensional features

could successfully detect vertebral fractures.

The study also had limitations. Only 90 cases were available, which is

small for deep learning. Cross-validation reuses the same overall dataset

across different folds, so it is not as strong as testing once on a large

independent hospital dataset. The main task was fracture detection rather

than complete Genant grading.

## Connection to this project

This paper supports the decision to use a three-dimensional CNN.

The project will use:

- One vertebral crop at a time

- A single CT channel

- A tensor shaped [batch, 1, 64, 64, 64]

- A 3D ResNet-18 or a MONAI three-dimensional DenseNet

- Four ordered Genant grades

The project must use a held-out patient test set in addition to any

cross-validation. No patient may appear in more than one split.

# Paper 6: Husseini Grading Loss

## Citation

Husseini, M., Sekuboyina, A., Löffler, M., Navarro, F.,

Menze, B. H., and Kirschke, J. S. (2020).

Grading Loss: A fracture grade-based metric loss for vertebral fracture

detection. In Medical Image Computing and Computer Assisted Intervention,

MICCAI 2020, Lecture Notes in Computer Science, 12265, 733-742.

https://doi.org/10.1007/978-3-030-59725-2_71

Free preprint:

https://arxiv.org/abs/2008.07831

## Research question

Can a training loss improve fracture detection by teaching a model that

Genant grades have a meaningful order?

## Important vocabulary

- Loss function: A number showing how wrong the model is during training.

- Ordinal: Categories that have a meaningful order.

- Metric learning: Learning a feature space where similar examples are close.

- Latent representation: The internal features learned by a neural network.

- Class imbalance: Some classes occur much more frequently than others.

- Naive classifier: A basic model that does not use important problem structure.

## Why regular classification is insufficient

Genant grades have this order:

0 -> 1 -> 2 -> 3

A regular four-class cross-entropy loss treats every incorrect category as

simply wrong. It does not fully represent the difference between nearby

and distant mistakes.

For a true grade 3 vertebra:

- Predicting grade 2 is a one-grade error.

- Predicting grade 0 is a three-grade error.

The second error is much more serious and should usually receive a larger

penalty.

## Method and results

The authors proposed Grading Loss to make the model's learned

representations respect the order of the Genant grades. Vertebrae with

similar grades should have more similar representations, while vertebrae

with very different grades should be separated more strongly.

The paper identified three major difficulties:

1. Too few labeled examples

2. Severe class imbalance

3. Small visual differences between healthy and mildly fractured vertebrae

The proposed method achieved a fracture-detection F1 score of 81.5%. The

authors reported an improvement of approximately 10% over a naive

classification baseline.

## Summary

Husseini and colleagues focused on how a fracture model should learn from

ordered labels. Genant grades are not unrelated names. They describe a

progression from normal to severe collapse.

A standard classifier can learn four outputs, but it does not necessarily

organize its internal features according to fracture severity. Grading

Loss encourages the learned feature representation to preserve the order

of the grades.

This matters most for difficult cases. A healthy vertebra and a mild

grade-1 fracture may look very similar. Grades 2 and 3 usually show more

obvious collapse. The loss function should help the model learn both the

difference between normal and fractured vertebrae and the progression of

fracture severity.

The reported F1 improvement demonstrates that including medical grading

structure can outperform a naive classifier. However, the method does not

eliminate the need for class balancing, careful patient splits, or

independent testing.

## Connection to this project

The final model should use an ordinal-aware approach. Possible choices are:

1. Reproduce Grading Loss.

2. Use CORAL ordinal regression.

3. Use CORN ordinal regression.

The first baseline will still use ordinary cross-entropy so that the

ordinal model can be compared against it.

The project will report:

- Exact four-grade accuracy

- Quadratic-weighted Cohen's kappa

- Four-by-four confusion matrix

- Binary fracture sensitivity and specificity

- Grade 2-or-higher sensitivity

Quadratic-weighted kappa is important because it penalizes large grading

errors more than small grading errors.

# Paper 7: Bar and Burns Automated Detection Pipelines

## Bar citation

Bar, A., Wolf, L., Bergman Amitai, O., Toledano, E., and Elnekave, E.

(2017). Compression Fractures Detection on CT.

Medical Imaging 2017: Computer-Aided Diagnosis, Proceedings of SPIE,

10134, 1013440.

https://doi.org/10.1117/12.2249635

Free preprint:

https://arxiv.org/abs/1706.01671

## Burns citation

Burns, J. E., Yao, J., and Summers, R. M. (2017).

Vertebral Body Compression Fractures and Bone Density:

Automated Detection and Classification on CT Images.

Radiology, 284(3), 788-797.

https://doi.org/10.1148/radiol.2017162100

Paper:

https://pubs.rsna.org/doi/10.1148/radiol.2017162100

## Research question

How can a complete automated pipeline find the spine, detect compression

fractures, and produce clinically useful information?

## Bar pipeline

The Bar system contained three major processes:

1. Segment the spinal column.

2. Extract sagittal patches and classify them with a CNN.

3. Use an RNN to combine the patch predictions into a scan-level answer.

The CNN examined the visual appearance of individual patches. The RNN

used the order of the patch predictions to decide whether the scan

contained a compression fracture.

This was an important early example of a multistage deep-learning

pipeline. However, it mainly produced a binary patient-level prediction.

It did not produce a Genant grade for every vertebra.

## Burns pipeline

The Burns study used CT scans from 150 patients:

- 75 patients with compression fractures

- 75 matched patients without compression fractures

- 210 fractured thoracic or lumbar vertebrae

The automated system segmented the spine, detected fractures, localized

them anatomically, classified the fracture type and grade, and measured

bone density.

Reported results included:

- Fracture-detection sensitivity: 95.7%

- False-positive rate: 0.29 per patient

- Case-level sensitivity: 98.7%

- Case-level specificity: 77.3%

- Fracture-type accuracy: 0.95

- Weighted kappa for fracture type: 0.90

- Height-loss grade accuracy: 0.68

- Weighted kappa for height-loss grade: 0.59

## Summary

Bar and Burns demonstrated complete pipelines rather than isolated

classifiers. Both systems first reduced the large CT scan to a smaller

spine region before analyzing fractures.

Bar used a CNN to classify sagittal patches and an RNN to combine the

ordered patch predictions. This design was useful for producing one answer

for the entire scan. However, a patient-level result does not provide the

vertebral name or fracture grade required by the current project.

Burns developed a system that performed more detailed analysis. It

detected and localized compression fractures, classified fracture type,

estimated Genant height-loss grade, and measured vertebral bone density.

The system achieved high fracture-detection sensitivity with a relatively

low false-positive rate.

An important result was that fracture detection was easier than accurate

severity grading. The system detected fractures with high sensitivity,

but its exact height-loss grade accuracy was 0.68 and weighted kappa was

0.59. This difference shows why the current project must evaluate grading

separately from binary fracture detection.

The Burns method also provides a useful morphometric baseline. A

segmentation can be used to estimate anterior, middle, and posterior

vertebral heights. The height-loss ratios can then be converted into

Genant grades without a grading CNN.

## Connection to this project

The project follows the multistage lesson from these pipelines:

1. Locate and label each vertebra.

2. Create a vertebral mask.

3. Crop the vertebral body.

4. Predict the Genant grade.

5. Return the vertebral name, grade, and confidence.

The project will implement two grading methods:

### Morphometric baseline

Estimate anterior, middle, and posterior height from the mask. Convert

height loss into grades using the Genant thresholds.

### Three-dimensional CNN

Use the complete 64 by 64 by 64 vertebral crop to predict the grade.

The CNN must be compared with the morphometric baseline. This comparison

will show whether the neural network learns useful fracture information

beyond simple height measurements.

## Combined lessons from all reviewed papers

The literature supports the following design:

1. Genant defines the four ordered grades.

2. VerSe supports localization, labeling, and segmentation.

3. Löffler supplies segmentation masks and fracture grades.

4. Tomita shows that deep learning can screen routine CT scans.

5. Nicolaes shows the value of three-dimensional features.

6. Husseini shows why ordinal-aware training is important.

7. Bar and Burns demonstrate complete automated pipelines.

8. Burns shows that exact grading is harder than binary detection.

The proposed system will therefore use a two-stage pipeline:

Stage A:

TotalSegmentator produces labeled vertebral masks.

Stage B:

A three-dimensional CNN predicts an ordered Genant grade for each

vertebral crop.

The main grading metric will be quadratic-weighted Cohen's kappa.

Binary fracture detection and grade 2-or-higher sensitivity will also be

reported. All dataset splits will be created at the patient level.
