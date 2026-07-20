from datasets import Dataset
import os
from ragas import evaluate
from ragas.metrics.collections import Faithfulness, ContextRecall, AnswerRelevancy
import json

with open('data/evaluation/golden_test_set.json', 'r', encoding='utf-8') as f:
    golden_test_set = json.load(f)

dataset = {}
dataset['case_id'] = []
dataset['question'] = []
dataset['context'] = []
dataset['answer'] = []
dataset['ground_truth'] = []
dataset['category'] = []

for i in golden_test_set:

    dataset['case_id'].append(i['id'])
    dataset['question'].append(i['question'])
    dataset['context'].append()
    dataset['answer'].append()
    dataset['ground_truth'].append(i['ground_truth'])
    dataset['category'].append(i['category'])

datasets = Dataset.from_dict(dataset)

score = evaluate(datasets, metrics=[Faithfulness(), ContextRecall(), AnswerRelevancy()])

df = score.to_pandas()
df.to_csv('data/evaluation/eval_result/score.csv', index= False)

