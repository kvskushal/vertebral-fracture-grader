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

