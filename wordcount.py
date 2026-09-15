"""Word count in PySpark, with the same rules as the Hadoop job from Hands-on L4:
split on whitespace, ignore words shorter than three characters, sort by count.

Usage:
    spark-submit wordcount.py <input file> [<output directory>]

The output directory must not already exist. If it is omitted, the result is only printed.
"""
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, length, col, lower

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)

min_length = int(sys.argv[3] if len(sys.argv)>3 else 3)

spark = SparkSession.builder.appName("WordCount").getOrCreate()

lines = spark.read.text(sys.argv[1])
words = lines.select(explode(split(lower(col("value")), r"\s+")).alias("word"))
words_scanned = words.count()

filtered_words = words.filter(length("word") >= min_length)
words_filtered = filtered_words.count()

counts = (filtered_words
               .groupBy("word").count()
               .orderBy(col("count").desc(), col("word")))

distinct_words = counts.count()

print(f"{words_scanned} words scanned")
print(f"{words_filtered} words of at least {min_length} characters")
print(f"{distinct_words} distinct words")

counts.show(50, truncate=False)

if len(sys.argv) > 2:
    # One partition so that the result is a single file, like the L4 part-r-00000.
    (counts.coalesce(1)
           .selectExpr("concat(word, ' ', count) AS line")
           .write.text(sys.argv[2]))
    print(f"Result written to {sys.argv[2]}")

spark.stop()
