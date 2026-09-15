# Hands-on L5: Report

**Name:** Eswar Kumar

**Student ID:** 801505751

**Email:** epanta@charlotte.edu

---

## What I ran

The commands you used, in the order you used them. If you deviated from the steps in the
README, say where and why.

```bash
# 1. Start the cluster
docker compose -f docker-compose.codespaces.yml up -d

# 2. Interactive PySpark Shell session
docker exec -it spark-master /opt/spark/bin/pyspark --master spark://spark-master:7077

# 3. Copy original script into container and run Part 1
docker cp wordcount.py spark-master:/opt/spark/work-dir/
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/work-dir/wordcount.py \
  /opt/spark/work-dir/shared/input/data/input.txt \
  /opt/spark/work-dir/shared/output/wordcount

# 4. Copy updated script and run Part 2 (v2 - default min length 3)
docker cp wordcount.py spark-master:/opt/spark/work-dir/
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/work-dir/wordcount.py \
  /opt/spark/work-dir/shared/input/data/input.txt \
  /opt/spark/work-dir/shared/output/wordcount-v2

# 5. Run Part 2 with min length 5
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/work-dir/wordcount.py \
  /opt/spark/work-dir/shared/input/data/input.txt \
  /opt/spark/work-dir/shared/output/wordcount-long 5

# 6. Stop cluster
docker compose down
```

---

## Input and output

### My input dataset

```
hadoop mapreduce is a software framework for writing applications
Hadoop word count is the classic hello world program for big Data
mapreduce breaks down processing into map phase and reduce phase
hadoop processes large datasets across clusters of computers
hDFS stores data reliably across distributed nodes in a hadoop cluster
word count counts the occurrence of each word in a dataset
learning hadoop opens up big data processing opportunities
```

### The output of part 1

Paste the contents of the `part-...txt` file from `shared-folder/output/wordcount/`.

```

```

---

## What I observed

A few sentences on what you actually noticed. Some things worth looking at:

- What the master page at <http://localhost:8080> showed when the shell connected
- How many tasks and executors the Spark UI at <http://localhost:4040> listed for `show`
- How long the job took, in the shell and with `spark-submit`



---

## What I changed

The three changes you made to `wordcount.py`. Paste the lines you added or rewrote
(`git diff` gives you exactly this).

```python
1. change 1
words = lines.select(explode(split(lower(col("value")), r"\s+")).alias("word"))
2. change 2
min_length = int(sys.argv[3] if len(sys.argv)>3 else 3)
3. change 3
words_filtered = filtered_words.count()

counts = (filtered_words
               .groupBy("word").count()
               .orderBy(col("count").desc(), col("word")))

distinct_words = counts.count()

print(f"{words_scanned} words scanned")
print(f"{words_filtered} words of at least {min_length} characters")
print(f"{distinct_words} distinct words")
```

---

## What the changes did

### The three numbers

| Run | Min length | Words scanned | Words kept | Distinct words |
| --- | ---------- | ------------- | ---------- | -------------- |
| `wordcount-v2` | 3 | | | |
| `wordcount-long` | | | | |

### The three outputs compared

How many distinct words did folding the case remove (compare `wordcount/` with
`wordcount-v2/`)? How many did the longer minimum remove? Name one word from your own text
whose count changed when the counting became case-insensitive.



### Jobs

How many jobs did your run launch, according to the **Jobs** tab, and how does that compare
with the original program? Why does Spark read the same file more than once in a single run?



---

## Problems and fixes

Anything that went wrong and what resolved it. Paste the actual error message. If nothing
went wrong, say so.


