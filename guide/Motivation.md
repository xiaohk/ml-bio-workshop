# Motivation

> #### Questions
>
> 1.   What is machine learning and why should biologists learn it?
> 2.   What questions in biology can machine learning help answer?
>
> #### Objectives
>
> 1.   Describe what machine learning is at a high level.
> 2.   Explain why machine learning has a growing impact on biological research.
> 3.   Illustrate the use of machine learning in biology with real-world examples.

### A gentle introduction to machine learning

Imagine you are sitting in a botany class and your professor is teaching plant taxonomy. 
She just described how to visually distinguish between the various families under <i>Sapindales</i> through a three-step procedure 
that includes examining the arrangement of leaves, counting the number of sepals and checking whether fruits open at maturity. 
Unfortunately, you were distracted by an interesting post on Facebook and did not hear her words. 
You want to figure it out on your own because there will be an in-class quiz shortly, 
and the only material available is the selected photos of leaves, flowers and fruits on the screen. 
What are the chances of learning  the right rules only from those examples? 
The answer is, not too surprisingly, very likely, 
because you as a human can notice in a second the distinguishing features hidden in the examples, 
and later apply the implicitly learned classification rules to a new example presented in the quiz.

The example above demonstrates two learning approaches.

- <b>Learning by remembering a procedure.</b> 
A procedure is a set of explicit instructions on how you should navigate through a task. 
For example, your botany professor taught you the steps you should take when you do plant classification; 
The campus safety staff taught you the procedures for handling flammable chemicals before you started your lab work. 
Such procedures can (and should) be easily understood and executed by an ordinary person.

- <b>Learning from examples.</b> 
A set of representative examples encode important knowledge about the concept from which the examples are based. 
Learning is the process of turning the hidden information into something explicit. 
In the plant classification example, a photo and its associated family together formed an example. 
Your brain processed the examples by extracting the most meaningful morphological features from the photos 
and formulating some explicit criteria for differentiating, for example, an olive tree from a mango tree.

Neither approach beats the other under all conditions. 
When a simple procedure exists, it is more efficient to learn it directly. 
When the cost of generating examples is prohibitive, you had better find an alternative learning method. 
For example, you do not want to learn chemical safety from bad practice at the cost of lives. 
However, when you encounter a complex system where no simple procedure applies but lots of examples are available, 
learning from examples becomes extremely powerful and perhaps is the only way to go. 
Our brain does have a limit though - as the size and complexity of examples grow too big for humans to interpret, we are no longer the best learner. 
Machine learning comes to the rescue.

At a high level, machine learning refers to a class of algorithms 
that can discover useful knowledge from examples, or simply data, and apply the knowledge to scenarios beyond the data it has previously seen. 
Machine learning resembles the way humans learn from examples, but a key advantage is its scalability with respect to data size and system complexity. 
That is, it can sift through volumes of data to find complex patterns or structures. 
Depending on what type of knowledge an algorithm extracts, machine-learning algorithms can be roughly divided into two categories:

- <b>Supervised learning.</b> 
An example contains a set of features, either measured or encoded in some entity, and a response value. 
A supervised-learning algorithm learns to predict a response from features. 
When the responses belong to a few discrete values, or classes, the learning task is called <i>classification</i>. 
If the responses are continuous, the task is called <i>regression</i>. 
The plant taxonomy example is a classification problem. 
The photos encode features, and the associated families are class labels.

- <b>Unsupervised learning.</b> 
An example contains features but no class label. 
An unsupervised-learning algorithm learns hidden structures in the data. 
In <i>clustering</i>, the goal is to discover groups of similar examples in the data; 
In <i>dimensionality reduction</i>, the goal is to represent examples using fewer features while losing little information.

Due to time constraints, this workshop only discusses classification in supervised learning. 
We will introduce the elements of supervised learning more formally in subsequent lessons.

### Machine learning in biology

Modern biological research is data-intensive. 
Thanks to the rapid development of high-throughput technologies, 
large amounts of biological and clinical data are being generated at an unprecedented speed every day. 
It is increasingly common for biologists to encounter "omics" data as well as other data modalities 
such as microscopic images, electronic health records and molecular structure data. 
Such massive, high-dimensional data is well suited for analysis by machine-learning algorithms. 
As the demand for large-scale data analysis grows, machine learning is becoming integral to biological research. 
Instead of enumerating all tasks on which machine learning has proven successful, 
we present some selected examples to motivate why biologists could benefit from learning and applying machine learning.

- <b>Tumor classification according to telomere repeat content.</b> 
Telomeres are repetitive DNA sequences that cap the chromosomes and protect them from abnormal degradation and recombination. 
The teolomeres in human somatic cells shorten upon every division - a mechanism that keeps cells from infinite proliferation. 
Human cancer cells, however, gain immortality by maintaining telomere length. 
They either stimulate telomerase activity, or use a pathway known as Alternative Lengthening of Telomeres (ALT). 
ALT+ and ALT- cancer cells exhibit distinct gene expression profiles and thus require individualized therapeutic strategies. 
Researchers trained a <i>random forest</i> to classify cancer cells as ALT+ or ALT- based on telomere repeat content. 
The algorithm extracts the sequence content that are unique to ALT+ and ALT- cells after seeing a collection of labeled examples. 
It achieves an accuracy of over 90%, thus having potential in guiding basic research as well as clinical therapy. 
([Lee et.al. <i>Nucleic Acid Research</i> (2018)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6007693/))

- <b>Deep learning to predict epigenetic impact of noncoding variants.</b> 
Noncoding sequences play a pivotal role in the regulation of transcription factor (TF) binding, DNA methylation and histone modification, 
which in turn control gene expression. 
Variations in noncoding regions constitute the majority of disease and other trait-associated single-nucleotide polymorphisms (SNPs), 
but characterizing their functional effects remains a challenge. 
Researchers developed DeepSEA, a fully sequence-based <i>convolutional neural network</i>, for predicting the effects of noncoding variants. 
Given a sequence with mutations, the model outputs the predicted epigenetic profiles including TF binding, DNase I sensitivity and histone marks. 
As the researchers pointed out, DeepSEA would "help unveil the regulatory information in the vast and currently poorly understood noncoding genomic regions 
and contribute to understanding the potential functions of complex disease or trait-associated SNPs". 
([Zhou et.al. <i>Nature Methods</i> (2015)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4768299/))

- <b>Predicting neural toxicity of compounds using RNA-Seq data.</b> 
Human pluripotent stem cell-based in vitro models have the potential to reduce the cost of drug toxicity assessment 
and increase the success rate of drug candidates that enter clinical trials. 
In this study, stem cell engineering and machine learning were combined to implement an <i>in vitro</i> model for neurotoxicity screening. 
Researchers derived neural constructs from human embryonic stem cells 
and trained a <i>support vector machine</i> from the RNA-Seq data for neural constructs exposed to 60 toxic and nontoxic compounds. 
Given a new construct, the model outputs the prediction on whether it is toxic or not. 
The machine-learning model achieved an accuracy of 90% and may facilitate fast and cost-effective <i>in silico</i> screening of compounds. 
([Schwartz et.al. <i>PNAS</i> (2015)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4603492/))

- <b>Detection of peptides from tandem mass spectra.</b> 
Liquid chromatography (LC) followed by tandem mass spectrometry (MS/MS), often referred to as shotgun proteomics, 
is one of the state-of-the-art techniques for analyzing complex protein samples. 
A remaining challenge is to identify the generating peptide from each of the hundreds of thousands of spectra produced by a run. 
At the core of the problem is defining a suitable metric for scoring the distance between an observed spectrum and a theoretical spectrum. 
Researchers developed a <i>dynamic Bayesian network</i> model that models peptide fragmentation in MS/MS as a physical process. 
Given an observed spectrum, the model outputs the most likely match through a database search. 
The model outperforms past non-machine-learning based tools for peptide identification. 
([Halloran et.al. <i>Journal of Proteome Research</i> (2016)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5116375/))

The examples above feature four different types of machine-learning models, 
namely random forests, convolutional neural networks, support vector machines and dynamic Bayesian networks. 
We will cover random forests and support vector machines. 
Although convolutional neural networks and dynamic Bayesian networks are beyond the scope of this workshop, 
we will discuss their most basic versions, multilayer perceptrons (a.k.a. neural networks) and naïve Bayes.


> #### Further readings
>
> 1. A survey of machine learning and its application in genetics and genomics. [Nature review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5204302/)
> 2. Opportunities and challenges for deep learning in biology. [Nature article](https://www.nature.com/articles/d41586-018-02174-z) and [a community-driven effort](http://doi.org/10.1098/rsif.2017.0387)
> 3. Stay focused in class and do not solely rely on your superb ability of learning from examples. See [what psychologists found about learning math through concrete examples](https://www.sciencedaily.com/releases/2008/04/080424140410.htm).
