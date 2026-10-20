"""Accuracy is a fraction, higher is better; splits are equally weighted."""
from statistics import mean, stdev
import math


def accuracy(predictions, labels, mask=None, prediction_ids=None, label_ids=None):
    p, y = list(predictions), list(labels)
    if len(p) != len(y) or not y:
        raise ValueError('Predictions and labels must have the same nonzero length.')
    if (prediction_ids is None) != (label_ids is None):
        raise ValueError('Provide both ID arrays when auditing alignment.')
    if prediction_ids is not None:
        pi, yi = list(prediction_ids), list(label_ids)
        if pi != yi or len(pi) != len(y) or len(set(pi)) != len(pi):
            raise ValueError('Node IDs are misaligned or duplicated.')
    if mask is None: mask = [True] * len(y)
    mask = list(mask)
    if len(mask) != len(y): raise ValueError('Mask length mismatch.')
    if any(v not in (True, False) for v in mask): raise ValueError('Mask must be boolean.')
    selected = [(a, b) for a, b, keep in zip(p, y, mask) if keep]
    if not selected: raise ValueError('Empty evaluation mask.')
    correct = sum(int(a == b) for a, b in selected)
    return dict(accuracy=correct / len(selected), correct=correct, size=len(selected),
                unit='fraction', accuracy_percent=100 * correct / len(selected), higher_is_better=True)


def aggregate(values):
    values = list(values)
    if not values or not all(math.isfinite(v) and 0 <= v <= 1 for v in values):
        raise ValueError('Expected finite accuracy fractions in [0,1].')
    return dict(n=len(values), mean=mean(values), sample_sd=stdev(values) if len(values) > 1 else None,
                unit='fraction', weighting='equal run/split weight', ddof=1)

