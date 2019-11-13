# leetcode-discussion-spider

Webinfo 开放实验，要求见 https://git.bdaa.pro/yxonic/data-specification/wikis/LeetCode%20%E8%AE%A8%E8%AE%BA

大约用了两天时间来写，很烂，但是勉强能用。

## 说明

`spider.py`: 从 Leetcode 中爬取内容，支持有限的从断点继续爬取的功能。用户名和密码需要放在 `config.py` 中。

`database.py`: 读写 SQLite 数据库，实现（相比直接读写文件而言）更好的数据处理。

`solution.py`: 第一遍清洗数据，尝试从标签、标题、内容直接推断获得 `solution` 域。

`guess.py`: 第二遍清洗数据，使用 `guesslang` 直接猜代码的语言。（很慢，使用 CPU 运行时处理 ~80000 个代码大约需要 5 个小时）

`export.py`: 从 SQLite 导出到 JSON。