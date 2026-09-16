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
1. wordcount
hadoop 4
word 3
across 2
big 2
count 2
data 2
for 2
mapreduce 2
phase 2
processing 2
the 2
Data 1
Hadoop 1
and 1
applications 1
breaks 1
classic 1
cluster 1
clusters 1
computers 1
counts 1
dataset 1
datasets 1
distributed 1
down 1
each 1
framework 1
hDFS 1
hello 1
into 1
large 1
learning 1
map 1
nodes 1
occurrence 1
opens 1
opportunities 1
processes 1
program 1
reduce 1
reliably 1
software 1
stores 1
world 1
writing 1
```
```
2. wordcount-v2
hadoop 5
data 3
word 3
across 2
big 2
count 2
for 2
mapreduce 2
phase 2
processing 2
the 2
and 1
applications 1
breaks 1
classic 1
cluster 1
clusters 1
computers 1
counts 1
dataset 1
datasets 1
distributed 1
down 1
each 1
framework 1
hdfs 1
hello 1
into 1
large 1
learning 1
map 1
nodes 1
occurrence 1
opens 1
opportunities 1
processes 1
program 1
reduce 1
reliably 1
software 1
stores 1
world 1
writing 1
```
```
3. wordcount-long
hadoop 5
across 2
count 2
mapreduce 2
phase 2
processing 2
applications 1
breaks 1
classic 1
cluster 1
clusters 1
computers 1
counts 1
dataset 1
datasets 1
distributed 1
framework 1
hello 1
large 1
learning 1
nodes 1
occurrence 1
opens 1
opportunities 1
processes 1
program 1
reduce 1
reliably 1
software 1
stores 1
world 1
writing 1

```

---

## What I observed

- When connecting to the PySpark shell, the Spark Master page at `http://localhost:8080` showed a new running application named `PySparkShell` with 4 cores allocated across the 2 worker nodes (`spark-worker-1` and `spark-worker-2` on ports 7078 and 7079).

- In the Spark Application UI at `http://localhost:4040`, running `.show()` triggered a single Spark job consisting of 2 stages. The Executors tab listed 2 active executors (one per worker container) processing tasks across the 4 total cores. 

- Execution was significantly faster in the interactive PySpark shell (~1.2 seconds for `show()`) because the SparkSession and JVM context were already initialized. In contrast, running the job via `spark-submit` took around 28 to 31 seconds per run due to the startup overhead of spinning up the driver process, registering with the master, and allocating executor resources for each submission.



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
| `wordcount-v2` | 3 |69 |59 | 43|
| `wordcount-long` |5 |69 |41 |32 |

### The three outputs compared

* **Distinct words removed by case folding:** Case folding normalized upper/lowercase variations into a single lowercase key.
* **Distinct words removed by longer minimum:** Raising the minimum word length parameter from 3 to 5 removed **11 distinct words** (dropping 3- and 4-letter words such as `data`, `word`, and `big`), reducing the distinct word count from 43 in `wordcount-v2/` down to 32 in `wordcount-long/`.
* **Word count change example:** The word **`hadoop`** (originally appearing as `hadoop 4` in the baseline) changed to lowercase (`hadoop 5`) when counting became case-insensitive.


### Jobs

* **Jobs launched:** According to the **Jobs** tab, the run launched **3 jobs**
* **Why Spark reads the file multiple times:** Spark uses lazy evaluation. Each explicit action operation in the code (such as `.count()`, `.show()`, or `.write`) triggers a separate DAG execution. Because the intermediate DataFrames were not explicitly cached in memory using `.cache()` or `.persist()`, Spark re-evaluates the transformation pipeline from the original input file for every single action triggered during the run.



---

## Problems and fixes

Initially, the Web UIs (Spark Master at port `8080` and Spark Application UI at port `4040`) were not automatically exposed by GitHub Codespaces upon starting the Pyspark session. The **Ports** panel displayed *"No forwarded ports"* instead of detecting the active services automatically.  so i had to type the ports `8080` and `4040` in the ports panel which then created a forward address to access it.


