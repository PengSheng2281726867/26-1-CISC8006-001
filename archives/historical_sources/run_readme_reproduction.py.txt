"""Run the upstream README commands and retain their complete output."""

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import torch
import torch_geometric
from torch_geometric.datasets import Actor, WebKB, WikipediaNetwork
from torch_geometric.transforms import NormalizeFeatures


PROJECT = Path(__file__).resolve().parent / "GAMMA"
DATASETS = ("Texas", "Wisconsin", "Cornell", "Actor", "Squirrel", "Chameleon")
SHAPES = {
    "Texas": (183, 1703), "Wisconsin": (251, 1703),
    "Cornell": (183, 1703), "Actor": (7600, 932),
    "Squirrel": (5201, 2089), "Chameleon": (2277, 2325),
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git(*args):
    return subprocess.check_output(["git", "-C", str(PROJECT), *args]).decode("utf-8").replace("\r\n", "\n")


def load_dataset(name):
    options = dict(root=str(PROJECT / "data" / name),
                   transform=NormalizeFeatures(), force_reload=True)
    if name in ("Texas", "Wisconsin", "Cornell"):
        return WebKB(name=name, **options)
    if name == "Actor":
        return Actor(**options)
    return WikipediaNetwork(name=name.lower(), **options)


def run_command(arguments, log_path):
    command = [sys.executable, *arguments]
    print("RUN " + " ".join(arguments), flush=True)
    env = os.environ.copy()
    env.update(PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    started = time.perf_counter()
    lines = []
    with log_path.open("w", encoding="utf-8") as log:
        with subprocess.Popen(command, cwd=PROJECT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True,
                              encoding="utf-8", errors="strict", bufsize=1) as process:
            for line in process.stdout:
                log.write(line)
                log.flush()
                lines.append(line)
                if line.startswith(("Creating", "All splits", "Split ", "Test Accuracy:",
                                    "Results over", "Mean Test Accuracy:", "All accuracies:",
                                    "Traceback", "RuntimeError", "ValueError")):
                    print(line.rstrip(), flush=True)
            returncode = process.wait()
    if returncode:
        raise RuntimeError(f"Command failed ({returncode}); see {log_path}")
    return "".join(lines), time.perf_counter() - started


def audit_splits(output, graph_info):
    result = {}
    split_copy = output / "splits"
    split_copy.mkdir()
    for name in DATASETS:
        n = graph_info[name]["num_nodes"]
        train_n, val_n = int(0.6 * n), int(0.2 * n)
        records = []
        for index in range(10):
            path = PROJECT / "splits" / f"{name.lower()}_split_0.6_0.2_{index}.npz"
            with np.load(path) as saved:
                masks = [saved[key] for key in ("train_mask", "val_mask", "test_mask")]
            assert all(mask.shape == (n,) and mask.dtype == np.bool_ for mask in masks)
            assert np.all(np.stack(masks).sum(axis=0) == 1), (name, index, "overlap/coverage")
            assert [int(mask.sum()) for mask in masks] == [train_n, val_n, n - train_n - val_n]
            permutation = torch.randperm(n, generator=torch.Generator().manual_seed(102 + index)).numpy()
            for mask, indices in zip(masks, np.split(permutation, [train_n, train_n + val_n])):
                expected = np.zeros(n, dtype=np.bool_)
                expected[indices] = True
                assert np.array_equal(mask, expected), (name, index, "seed mismatch")
            shutil.copy2(path, split_copy / path.name)
            records.append(dict(index=index, seed=102 + index, train=train_n, val=val_n,
                                test=n - train_n - val_n, sha256=sha256(path)))
        result[name] = records
    write_json(output / "split_audit.json", result)
    return result


def summarize(output, state):
    write_json(output / "results.json", state)
    with (output / "summary.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dataset", "splits", "mean_test_accuracy_percent", "std_percent_ddof0", "seconds", "log"])
        for name, result in state["results"].items():
            writer.writerow([name, 10, result["mean"] * 100, result["std_ddof0"] * 100,
                             result["seconds"], result["log"]])
    text = ["# GAMMA README command reproduction", "",
            "Repository: https://github.com/amir-ghz/GAMMA", "",
            f"Commit: `{state['commit']}`", "",
            "The only source edits replace `/tmp/<dataset>` with `data/<dataset>` in the two entry scripts. "
            "Model, data processing, split generation, seeds, optimizer, dropout, scheduler, stopping and evaluation logic follow upstream.", "",
            "Environment: Python " + state["environment"]["python"].split()[0] +
            ", PyTorch " + torch.__version__ + ", PyG " + torch_geometric.__version__ +
            ", CUDA " + str(torch.version.cuda) + ", " + state["environment"]["gpu"] + ".", "",
            "Run from the GAMMA directory after `conda activate GAMMA`:", "", "```powershell",
            "python create_splits.py"]
    for name in DATASETS:
        text.append(f"python gamma_multi_split.py --dataset {name} --hidden_channels 32 --num_layers 2 --num_iterations 2")
    text += ["```", "", "| Dataset | Test accuracy (%), mean ± population std | Splits |",
             "| --- | ---: | ---: |"]
    for name, result in state["results"].items():
        text.append(f"| {name} | {result['mean']*100:.2f} ± {result['std_ddof0']*100:.2f} | 10 |")
    text += ["", f"Status: {state['status']}.", "",
             "All 60 masks are checked for shape, disjointness, coverage, sizes and the exact CPU "
             "`torch.randperm` sequence for seeds 102–111. Training uses upstream seeds 42–51. "
             "Each command's complete stdout/stderr is saved in its dataset log. Full per-split "
             "accuracies are recovered from the script's four-decimal accuracy list and integer test-set sizes; "
             "the resulting mean/std are checked against the printed summary.", "",
             "Important upstream behavior: `model.state_dict().copy()` is a shallow copy; it does not freeze "
             "the best validation checkpoint. This run retains that upstream behavior. The upstream scripts "
             "do not save model checkpoints. CUDA scatter aggregation is not made strictly deterministic "
             "by the original seed settings, so repeated GPU runs may vary.", "",
             "These are results of the repository commands. Matching the published paper's table is a "
             "separate comparison; no hyperparameters have been tuned to match it.", ""]
    (output / "REPORT.md").write_text("\n".join(text), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    output = PROJECT / (args.output or datetime.now().strftime("results/readme_%Y%m%d_%H%M%S"))
    output.mkdir(parents=True, exist_ok=False)
    assert torch.cuda.is_available(), "CUDA environment expected"
    state = dict(status="running", started_at=datetime.now(timezone.utc).isoformat(),
                 commit=git("rev-parse", "HEAD").strip(), environment={
                     "python": sys.version, "executable": sys.executable,
                     "torch": torch.__version__, "pyg": torch_geometric.__version__,
                     "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(),
                     "default_cpu_threads": torch.get_num_threads(),
                     "packages": {name: importlib.metadata.version(name) for name in
                                  ("numpy", "scipy", "torch-scatter", "torch-sparse")},
                     "environment_overrides": {name: os.environ.get(name) for name in
                                               ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "CUBLAS_WORKSPACE_CONFIG")}},
                 sources={}, results={})
    snapshot = output / "source_snapshot"
    snapshot.mkdir()
    for filename in ("create_splits.py", "gamma_multi_split.py", "GAMMA_layer.py", "requirements.txt", "README.md"):
        path = PROJECT / filename
        upstream = git("show", "HEAD:" + filename)
        local = path.read_text(encoding="utf-8")
        restored = local.replace("root='data/", "root='/tmp/")
        assert restored.rstrip() == upstream.rstrip(), f"Unexpected source modification: {filename}"
        shutil.copy2(path, snapshot / filename)
        state["sources"][filename] = dict(sha256=sha256(path), only_dataset_roots_changed=local != upstream)
    shutil.copy2(__file__, snapshot / Path(__file__).name)
    (output / "source_changes.patch").write_text(git("diff", "--", "create_splits.py", "gamma_multi_split.py", "GAMMA_layer.py"), encoding="utf-8")
    (output / "pip_freeze.txt").write_text(subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8"), encoding="utf-8")
    write_json(output / "results.json", state)
    graph_info = {}
    for name in DATASETS:
        dataset = load_dataset(name)
        data = dataset[0]
        assert tuple(data.x.shape) == SHAPES[name], (name, data)
        assert data.y.shape == (data.num_nodes,)
        assert int(data.edge_index.min()) >= 0 and int(data.edge_index.max()) < data.num_nodes
        assert torch.isfinite(data.x).all() and int(data.y.min()) >= 0
        for key in ("train_mask", "val_mask", "test_mask"):
            assert data[key].shape == (data.num_nodes, 10)
        graph_info[name] = dict(num_nodes=data.num_nodes, num_features=data.num_node_features,
                                num_edges=data.num_edges, num_classes=dataset.num_classes,
                                processed_sha256=sha256(dataset.processed_paths[0]),
                                raw_files={str(Path(p).relative_to(PROJECT)): sha256(p) for p in dataset.raw_paths})
        print(f"DATA OK {name}: {data.num_nodes} nodes, {data.num_node_features} features, {data.num_edges} edges", flush=True)
    write_json(output / "data_audit.json", graph_info)
    _, state["create_splits_seconds"] = run_command(["create_splits.py"], output / "create_splits.log")
    split_info = audit_splits(output, graph_info)
    print("SPLITS OK: 60 / 60", flush=True)
    summarize(output, state)
    for name in DATASETS:
        arguments = ["gamma_multi_split.py", "--dataset", name,
                     "--hidden_channels", "32", "--num_layers", "2", "--num_iterations", "2"]
        stdout, seconds = run_command(arguments, output / f"{name.lower()}.log")
        values = ast.literal_eval(re.search(r"All accuracies: (\[.*\])", stdout).group(1))
        assert len(values) == 10 and len(re.findall(r"^Test Accuracy:", stdout, re.M)) == 10
        counts = [entry["test"] for entry in split_info[name]]
        correct = [round(float(value) * count) for value, count in zip(values, counts)]
        accuracies = [number / count for number, count in zip(correct, counts)]
        assert [f"{value:.4f}" for value in accuracies] == values
        mean, std = float(np.mean(accuracies)), float(np.std(accuracies))
        printed = re.search(r"Mean Test Accuracy: ([0-9.]+) ± ([0-9.]+)", stdout)
        assert [f"{mean:.4f}", f"{std:.4f}"] == list(printed.groups())
        state["results"][name] = dict(command="python " + " ".join(arguments), seconds=seconds,
                                      accuracies=accuracies, test_correct=correct, test_sizes=counts,
                                      training_seeds=list(range(42, 52)), mean=mean, std_ddof0=std,
                                      log=f"{name.lower()}.log", log_sha256=sha256(output / f"{name.lower()}.log"))
        summarize(output, state)
        print(f"DONE {name}: {mean*100:.2f} +/- {std*100:.2f}% in {seconds:.1f}s", flush=True)
    for name in DATASETS:
        for entry in split_info[name]:
            path = PROJECT / "splits" / f"{name.lower()}_split_0.6_0.2_{entry['index']}.npz"
            assert sha256(path) == entry["sha256"]
    for filename, entry in state["sources"].items():
        assert sha256(PROJECT / filename) == entry["sha256"]
    state.update(status="complete", finished_at=datetime.now(timezone.utc).isoformat())
    summarize(output, state)
    print(f"COMPLETE: {output / 'REPORT.md'}", flush=True)


if __name__ == "__main__":
    main()
