# streaming_algorithms_2353892_choiyowon

# Streaming Algorithm Trade-off Analysis

## Student Information

- Student ID: 2353892
- Name: 최요원
- GitHub ID: hiyowon

## Assignment

스트리밍 알고리즘 2종 구현 및 정확도·메모리 트레이드오프 분석

## Dataset

This project uses the MovieLens 1M dataset.

- Dataset: MovieLens 1M
- Main file used: ratings.dat
- Number of rating records: 1,000,209
- Source: https://files.grouplens.org/datasets/movielens/ml-1m.zip

## Implemented Algorithms

1. Bloom Filter
   - Purpose: approximate membership test
   - Target: user-movie rating event existence

2. Count-Min Sketch
   - Purpose: approximate frequency estimation
   - Target: movie rating frequency

## How to Run

Place `ratings.dat` in the same directory as the source code.

```bash
python streaming_algorithm_tradeoff_2353892_choiyowon_source.py
