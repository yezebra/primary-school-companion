# 数据说明

## 来源

- 人教版（统编版）语文、人教版数学、人教版 PEP 英语的**单元目录**来自公开教材目录；
- 按每学期 20 周等比摊到周，**不是**官方教学计划；
- 城市教材映射是常见情况，具体以学校为准。

## 误差

| 来源 | 影响 |
|---|---|
| 学校进度快慢 | 同版本可差 1~3 周 |
| 教材版本差异 | 北京版、沪教版单元顺序不同（待补充） |
| 英语开设年级 | 多数学校 3 年级起，部分 1 年级起 |
| 单元合并/跳过 | 老师会跳讲、合并，周进度只能近似 |

## 怎么扩展

### 加一个教材版本

1. 新建 `data/<edition>/chinese.json`、`math.json`、`english.json`；
2. 结构照 `data/renjiao/*.json`：`grades.<年级>.<上|下>` 是单元数组；
3. 在 `data/cities.json` 里把城市指向新版本。

### 加一个城市

在 `cities.json` 的 `cities` 里加：

```json
"长沙": { "edition": "renjiao", "englishStartGrade": 3 }
```

### 加一个科目

1. 新建 `data/renjiao/<subject>.json`；
2. 在 `src/progress.py` 的 `SUBJECTS` 和 `SUBJECT_LABEL` 里加一项。

## 版权

只使用教材的**单元名称**（事实性目录），不包含课文正文、插图或练习内容。

## 校验

```bash
python3 src/progress.py --grade 4 --city 武汉 --date 2026-10-26 --json
```

检查输出是否符合你对教材的印象；发现单元名错误，直接改 JSON。
