\# Vertebral Fracture Grader: Design Document



Status: Awaiting approval before coding



\## 1. Objective



Build a research system that receives a non-contrast CT volume and returns

a Genant grade from 0 through 3 for every detected vertebra from T4

through L4.



Genant grades:



| Grade | Meaning | Height loss |

|---|---|---:|

| 0 | Normal | Less than 20% |

| 1 | Mild | 20% to less than 25% |

| 2 | Moderate | 25% to less than 40% |

| 3 | Severe | At least 40% |



The system is for research and testing. It is not a medical device and

must not be used to make clinical decisions without additional validation

and regulatory approval.



\## 2. Input and output



\### Complete system input



A non-contrast CT volume supplied as:



\- A NIfTI file, or

\- A directory containing one DICOM CT series



\### Complete system output



The inference function will return one record for each vertebra:



```python

\[

&#x20;   {

&#x20;       "vertebra": "T12",

&#x20;       "genant\_grade": 0,

&#x20;       "confidence": 0.97,

&#x20;       "status": "ok"

&#x20;   },

&#x20;   {

&#x20;       "vertebra": "L1",

&#x20;       "genant\_grade": 2,

&#x20;       "confidence": 0.91,

&#x20;       "status": "ok"

&#x20;   }

]

