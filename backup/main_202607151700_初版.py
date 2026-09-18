"""英文默背小工具：貼上段落後以比例隨機遮罩單字練習默背。"""

from __future__ import annotations

import random
import re
import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

# 英數 token；含縮寫如 don't / it's
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")

WordSpan = Tuple[str, str]  # (start_index, end_index) in Tk Text coordinates


class ReciteApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("英文默背小工具")
        self.root.geometry("720x480")
        self.root.minsize(480, 320)

        self._mask_locked = False
        self._build_ui()
        self._configure_tags()
        self._bind_selection_lock()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        text_frame = ttk.Frame(self.root, padding=(8, 8, 8, 4))
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 12),
            foreground="#000000",
            background="#ffffff",
            insertbackground="#000000",
            undo=True,
            padx=8,
            pady=8,
        )
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.text.yview
        )
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(self.root, padding=(8, 4, 8, 4))
        btn_frame.grid(row=1, column=0, sticky="ew")

        ttk.Button(btn_frame, text="清除", command=self.clear_text).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_frame, text="全部顯示", command=self.show_all).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(
            btn_frame, text="覆蓋 25%", command=lambda: self.cover(0.25)
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            btn_frame, text="覆蓋 50%", command=lambda: self.cover(0.5)
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            btn_frame, text="覆蓋 75%", command=lambda: self.cover(0.75)
        ).pack(side="left", padx=(0, 6))

        self.status_var = tk.StringVar(value="共 0 個 word｜尚未遮罩")
        status = ttk.Label(
            self.root, textvariable=self.status_var, padding=(8, 4, 8, 8)
        )
        status.grid(row=2, column=0, sticky="ew")

    def _configure_tags(self) -> None:
        bg = self.text.cget("background")
        self.text.tag_configure("hidden", foreground=bg, background=bg)

    def _bind_selection_lock(self) -> None:
        self.text.bind("<<Selection>>", self._on_selection)
        self.text.bind("<Control-c>", self._block_copy_if_locked)
        self.text.bind("<Control-C>", self._block_copy_if_locked)
        self.text.bind("<Control-x>", self._block_copy_if_locked)
        self.text.bind("<Control-X>", self._block_copy_if_locked)

    def _on_selection(self, _event: tk.Event | None = None) -> None:
        if not self._mask_locked:
            return
        # 立刻清除選取，避免反白洩漏隱形字
        self.text.tag_remove("sel", "1.0", "end")

    def _block_copy_if_locked(self, _event: tk.Event) -> str | None:
        if self._mask_locked:
            return "break"
        return None

    def _set_mask_locked(self, locked: bool) -> None:
        self._mask_locked = locked
        if locked:
            self.text.tag_remove("sel", "1.0", "end")

    def _find_words(self) -> List[WordSpan]:
        content = self.text.get("1.0", "end-1c")
        spans: List[WordSpan] = []
        for match in WORD_PATTERN.finditer(content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            spans.append((start, end))
        return spans

    def cover(self, ratio: float) -> None:
        words = self._find_words()
        n = len(words)
        if n == 0:
            self.text.tag_remove("hidden", "1.0", "end")
            self._set_mask_locked(False)
            self.status_var.set("共 0 個 word｜無內容可遮罩")
            return

        m = max(0, min(n, round(n * ratio)))
        chosen = random.sample(range(n), m) if m > 0 else []

        self.text.tag_remove("hidden", "1.0", "end")
        for idx in chosen:
            start, end = words[idx]
            self.text.tag_add("hidden", start, end)

        if m > 0:
            self._set_mask_locked(True)
        else:
            self._set_mask_locked(False)

        pct = int(ratio * 100)
        self.status_var.set(f"共 {n} 個 word｜已遮罩 {m} 個 ({pct}%)")

    def show_all(self) -> None:
        self.text.tag_remove("hidden", "1.0", "end")
        self._set_mask_locked(False)
        n = len(self._find_words())
        self.status_var.set(f"共 {n} 個 word｜全部顯示")

    def clear_text(self) -> None:
        self.text.delete("1.0", "end")
        self.text.tag_remove("hidden", "1.0", "end")
        self._set_mask_locked(False)
        self.status_var.set("共 0 個 word｜尚未遮罩")


def main() -> None:
    root = tk.Tk()
    ReciteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
