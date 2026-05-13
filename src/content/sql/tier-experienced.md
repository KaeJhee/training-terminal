# SQL · TIER 4 CONCEPTS (EXPERIENCED)

  <<dim>>The big shift here: you stop collapsing rows when you aggregate. Window<</dim>>
  <<dim>>functions let you compute a per-row value that sees its neighbors.<</dim>>

# WINDOW FUNCTIONS

  A window function is an aggregate or rank computed across a set of related
  rows, but the original rows are kept. The shape stays the same, you just
  gain a new column.

      <<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> revenue <<amber>>DESC<</amber>>)

  Three pieces: a function (<<purple>>RANK<</purple>>, <<purple>>ROW_NUMBER<</purple>>,
  <<purple>>DENSE_RANK<</purple>>, any aggregate), the <<amber>>OVER<</amber>> keyword, and a
  window spec inside parens.

  <<bold>>RANK<</bold>> gives ties the same number and skips the next: 1, 2, 2, 4.
  <<bold>>DENSE_RANK<</bold>> also ties but doesn't skip: 1, 2, 2, 3.
  <<bold>>ROW_NUMBER<</bold>> never ties: 1, 2, 3, 4 even when values are equal.

  <<dim>>You pick the one whose tie semantics match what downstream code expects.<</dim>>
  <<dim>>Most ranking dashboards want DENSE_RANK to avoid gaps.<</dim>>

# PARTITIONING

  Add <<amber>>PARTITION BY<</amber>> to compute the window separately within each
  group. Rank within status, running total within customer, that kind of thing.

      <<purple>>ROW_NUMBER<</purple>>() <<amber>>OVER<</amber>> (<<amber>>PARTITION BY<</amber>> status <<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>)

  Without <<amber>>PARTITION BY<</amber>> the window is the whole table.

# SUBQUERIES IN WHERE AND SELECT

  A subquery is a SELECT inside another SELECT. Two flavors matter at this
  tier: scalar subqueries (return one value) and table subqueries (return
  rows you query against).

      <<amber>>WHERE<</amber>> revenue = (<<amber>>SELECT<</amber>> <<amber>>MAX<</amber>>(rev) <<amber>>FROM<</amber>> (...))

  <<dim>>The "find the row matching the max of a derived column" pattern. The<</dim>>
  <<dim>>inner SELECT computes the threshold, the outer SELECT filters by it.<</dim>>

# COALESCE AND UNION

  <<amber>>COALESCE<</amber>>(a, b, c) returns the first non-NULL argument. Use it to
  swap missing values for a sensible default at display time.

      <<amber>>COALESCE<</amber>>(phone, <<green>>'N/A'<</green>>) <<amber>>AS<</amber>> phone_display

  <<amber>>UNION<</amber>> stacks two result sets vertically. They must have the same
  number of columns and compatible types. <<amber>>UNION<</amber>> dedupes,
  <<amber>>UNION ALL<</amber>> keeps duplicates and is faster.

  <<dim>>ML aside: ranking and partitioning are how leaderboards, top-K<</dim>>
  <<dim>>retrieval, and bucketed evaluation metrics are computed at the SQL layer<</dim>>
  <<dim>>before any model sees the rows.<</dim>>

  NEXT TIER: CTEs and recursive queries, self-joins, and the pivot trick.
  Anything that requires steps you can name and reuse, or queries that talk
  to themselves.

---

# EXAMPLE 1

  Rank rows globally by a metric. The whole table is one window.

      <<amber>>SELECT<</amber>> id, total_cost,
             <<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>) <<amber>>AS<</amber>> rnk
      <<amber>>FROM<</amber>> work_orders;

  <<dim>>rnk = 1 for the most expensive job. Ties get the same rank and the next<</dim>>
  <<dim>>number is skipped. ROW_NUMBER would force-break ties; DENSE_RANK would not<</dim>>
  <<dim>>skip.<</dim>>

# EXAMPLE 2

  Window inside a partition. Rank within each status independently so you can
  ask "biggest open job, biggest completed job" in one query.

      <<amber>>SELECT<</amber>> id, status, total_cost,
             <<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (
                 <<amber>>PARTITION BY<</amber>> status
                 <<amber>>ORDER BY<</amber>> total_cost <<amber>>DESC<</amber>>
             ) <<amber>>AS<</amber>> within_status_rank
      <<amber>>FROM<</amber>> work_orders;

  <<dim>>Same rank function, different window. Each status is its own<</dim>>
  <<dim>>leaderboard.<</dim>>

# EXAMPLE 3

  Subquery in the FROM clause, previewing CTEs. Right now you nest:

      <<amber>>SELECT<</amber>> mechanic_id, revenue
      <<amber>>FROM<</amber>> (
          <<amber>>SELECT<</amber>> mechanic_id, <<amber>>SUM<</amber>>(total_cost) <<amber>>AS<</amber>> revenue
          <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> mechanic_id
      ) <<amber>>AS<</amber>> rev
      <<amber>>WHERE<</amber>> revenue > <<blue>>5000<</blue>>;

  <<dim>>At Master tier you'll write the same logic with WITH rev AS (...). It<</dim>>
  <<dim>>reads top-down instead of inside-out and lets you reference the same<</dim>>
  <<dim>>subquery multiple times. See <</dim>><<qid:sql_mas_02>><<dim>>.<</dim>>

