\# Literature Review



\## Project



Automated Genant grading of thoracolumbar vertebrae from non-contrast CT.



\## Purpose



This literature review explains the medical grading standard, available

datasets, vertebra-localization methods, fracture-classification methods,

and appropriate training techniques for an ordinal grading model.



\# Paper 1: Genant Semiquantitative Grading Standard



\## Citation



Genant, H. K., Wu, C. Y., van Kuijk, C., \& Nevitt, M. C. (1993).

Vertebral fracture assessment using a semiquantitative technique.

Journal of Bone and Mineral Research, 8(9), 1137–1148.

https://doi.org/10.1002/jbmr.5650080915



\## Research question



How can radiologists consistently identify and grade vertebral fractures

using the appearance and height loss of each vertebral body?



\## Important vocabulary



\- Vertebra: One of the bones that forms the spine.

\- Vertebral body: The large, weight-bearing part of a vertebra.

\- Fracture: A break or collapse in a bone.

\- Height loss: How much shorter a vertebral body has become.

\- Semiquantitative: A method that combines visual judgment with approximate measurements.

\- Ground truth: The correct label that the AI is trained to predict.



\## Genant grades



| Grade | Meaning | Approximate vertebral height loss |

|---|---|---:|

| 0 | Normal | Less than 20% |

| 1 | Mild fracture | 20–25% |

| 2 | Moderate fracture | 25–40% |

| 3 | Severe fracture | More than 40% |



\## Common vertebral deformity shapes



1\. Wedge deformity:

&#x20;  The front of the vertebral body loses more height than the back.



2\. Biconcave deformity:

&#x20;  The middle of the vertebral body loses height while the front and back

&#x20;  remain taller.



3\. Crush deformity:

&#x20;  Most or all of the vertebral body loses height.



\## Summary



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













\# Paper 2: The VerSe Benchmark



\## Citation



Sekuboyina, A., Husseini, M. E., Bayat, A., Löffler, M., Liebl, H.,

Li, H., Tetteh, G., et al. (2021). VerSe: A vertebrae labelling and

segmentation benchmark for multi-detector CT images.

Medical Image Analysis, 73, 102166.

https://doi.org/10.1016/j.media.2021.102166



Free paper:

https://arxiv.org/abs/2001.09193



Official project:

https://github.com/anjany/verse



\## Research question



How accurately can automated systems find, name, and separate individual

vertebrae in CT scans?



\## Important vocabulary



\- Localization: Finding the three-dimensional location of a vertebra.

\- Labeling: Giving a vertebra its correct name, such as T12 or L1.

\- Segmentation: Marking every voxel belonging to a vertebra.

\- Voxel: A three-dimensional pixel in a CT volume.

\- Mask: An image marking the voxels belonging to an object.

\- Centroid: A point near the center of an object.

\- Field of view: The part of the body included in a CT scan.

\- Benchmark: A shared test used to compare computer systems fairly.

\- Anatomical variation: A natural difference in a person's anatomy.



\## Dataset



The VerSe benchmark combines the 2019 and 2020 VerSe challenges. It

contains 374 CT scans from 355 patients and 4,505 individually annotated

vertebrae. Its annotations include vertebral names, center coordinates,

and voxel-level segmentation masks.



A typical VerSe case includes:



1\. A CT volume.

2\. A segmentation mask.

3\. A JSON file containing vertebral labels and centroids.

4\. A PNG preview of the annotations.



\## Summary



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



\## Connection to the project



VerSe will help the project:



1\. Locate the spine.

2\. Identify vertebrae T4 through L4.

3\. Produce a separate mask for every vertebra.

4\. Create a 64 by 64 by 64 crop from each mask.

5\. Send each crop to the Genant-grading model.



\## License and provenance



Dataset: VerSe 2019 and VerSe 2020



Source:

https://github.com/anjany/verse



Dataset license: CC BY-SA 4.0



Helper-code license: MIT



Planned use:

Training or testing vertebral localization, labeling, and segmentation.



The large CT files will be stored outside GitHub. GitHub will contain only

the download instructions, license information, manifests, and code.



