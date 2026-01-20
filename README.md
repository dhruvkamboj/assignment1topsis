# TOPSIS – Multi Criteria Decision Making Project

## Course Details
- **Course Code:** UCS654  
- **Course Name:** Data Science Lab  
- **Assignment:** TOPSIS (Part I, II & III)  
- **Student Name:** Dhruv  
- **Roll Number:** 102303645  

---

## Introduction

This repository contains the complete implementation of **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)**, a popular **Multi-Criteria Decision Making (MCDM)** technique.  

The project is implemented in three phases:
1. Command-line TOPSIS implementation  
2. Python package creation and publishing on PyPI  
3. Web application development and deployment using Streamlit  

---

## What is TOPSIS?

TOPSIS is a decision-making method used to rank alternatives based on multiple criteria.  
The best alternative is the one that is:
- Closest to the **ideal best solution**
- Farthest from the **ideal worst solution**

It is widely used in engineering, management, and data science applications.

---

# Part I – Command Line TOPSIS

## Description

A Python command-line program that:
- Reads input data from CSV/Excel files
- Accepts weights and impacts as parameters
- Computes TOPSIS scores and ranks
- Writes the result to an output file

## Command-Line Usage

```bash
python topsis.py <InputDataFile> <Weights> <Impacts> <OutputFile>
```
## Input Constraints
- Input file must contain **at least 3 columns**
- **First column** represents alternative names (not used in calculations)
- Remaining columns must contain **numeric values only**
- Number of weights = number of impacts = number of criteria
- Weights and impacts must be **comma-separated**
- Impacts must be either `+` or `-`

## Output
- Original dataset
- **Topsis Score**
- **Rank** (Rank 1 indicates the best alternative)

---

## Part II – Python Package (PyPI)

The command-line implementation was converted into a Python package and published on **PyPI**.

### Package Name
