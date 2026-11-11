"""统一运行器，负责并发、断点续跑、token 累计与失败分类。"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from .extract import extract_answer


class Runner:
    """solver 接收题面字符串，返回 dict，键为 answer、output、prompt_tokens、
    completion_tokens、calls，可选 trace。"""

    def __init__(self, method: str, solver, out_dir: str = "results/raw", workers: int = 8):
        self.method = method
        self.solver = solver
        self.out_path = Path(out_dir) / f"{method}.jsonl"
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self.workers = workers
        self._lock = threading.Lock()

    def done_ids(self) -> set[str]:
        ids: set[str] = set()
        if self.out_path.exists():
            with self.out_path.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        ids.add(json.loads(line)["unique_id"])
                    except (json.JSONDecodeError, KeyError):
                        continue
        return ids

    def _write(self, record: dict) -> None:
        with self._lock, self.out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _one(self, item: dict) -> dict:
        start = time.time()
        record = {
            "unique_id": item["unique_id"],
            "method": self.method,
            "level": str(item["level"]),
            "subject": item.get("subject", ""),
            "answer": "",
            "output": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "calls": 0,
            "failure": "",
        }
        try:
            out = self.solver(item["problem"]) or {}
            output = out.get("output", "") or ""
            answer = (out.get("answer") or "").strip() or extract_answer(output)
            consumed = {"answer", "output", "prompt_tokens", "completion_tokens", "calls", "trace"}
            record.update(
                answer=answer,
                output=output,
                prompt_tokens=int(out.get("prompt_tokens", 0)),
                completion_tokens=int(out.get("completion_tokens", 0)),
                calls=int(out.get("calls", 0)),
                trace=out.get("trace", []),
                meta={k: v for k, v in out.items() if k not in consumed},
            )
            if not output.strip() and not answer:
                record["failure"] = "empty_output"
            elif not answer:
                record["failure"] = "extract_failed"
        except Exception as exc:  # 网络或解析异常均单独计数
            record["failure"] = "request_failed"
            record["error"] = repr(exc)
        record["latency"] = round(time.time() - start, 2)
        return record

    def run(self, problems: list[dict], limit: int | None = None) -> list[dict]:
        done = self.done_ids()
        todo = [p for p in problems if p["unique_id"] not in done]
        if limit is not None:
            todo = todo[:limit]
        records = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = [pool.submit(self._one, item) for item in todo]
            for fut in tqdm(as_completed(futures), total=len(futures), desc=self.method):
                record = fut.result()
                self._write(record)
                records.append(record)
        return records
