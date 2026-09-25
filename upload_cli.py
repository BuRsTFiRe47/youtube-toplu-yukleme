#!/usr/bin/env python3
"""
upload_cli.py - Komut satırından toplu yükleme (isteğe bağlı, teknik kullanıcılar için)
==========================================================================================
Çoğu kullanıcı için gui_upload.py önerilir. Bu dosya sadece terminal/otomasyon
tercih edenler içindir; aynı config.json ve aynı ilerleme (progress.json) kaydını kullanır.

Kullanım: python upload_cli.py
"""
import core


def main():
    cfg = core.load_config()
    core.run_upload_batch(cfg, log=print)


if __name__ == "__main__":
    main()
