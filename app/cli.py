# -*- coding: utf-8 -*-
"""
命令列：隨時手動推一次。

範例：
  python -m app.cli                      # 推全部
  python -m app.cli --metals 黃金,銅      # 只推黃金和銅
  python -m app.cli --markets 大陸,美國   # 只推這兩個市場
  python -m app.cli --dry                # 只印不推（測試用）
"""

import argparse
import logging

from .message import build_message
from .push import push_wecom


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    p = argparse.ArgumentParser()
    p.add_argument("--metals", help="逗號分隔，如 黃金,銅,鎳")
    p.add_argument("--markets", help="逗號分隔，如 大陸,美國,倫敦")
    p.add_argument("--dry", action="store_true", help="只印不推")
    args = p.parse_args()

    metals = [m.strip() for m in args.metals.split(",")] if args.metals else None
    markets = [m.strip() for m in args.markets.split(",")] if args.markets else None

    msg = build_message(metals=metals, markets=markets)
    print(msg)
    if not args.dry:
        push_wecom(msg)
        print("\n[已推送]")


if __name__ == "__main__":
    main()
