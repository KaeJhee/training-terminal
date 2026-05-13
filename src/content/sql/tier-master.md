# SQL · TIER 5 CONCEPTS (MASTER)

  <<dim>>Last tier. The patterns here are how analysts and DEs actually compose<</dim>>
  <<dim>>hard queries: name your steps, reuse them, recurse when the data has<</dim>>
  <<dim>>structure.<</dim>>

# COMMON TABLE EXPRESSIONS

  A CTE is a named subquery you write at the top with <<amber>>WITH<</amber>>. The body
  references the name like a real table. Two reasons to prefer them over
  nested subqueries: they read top-down, and you can chain them.

      <<amber>>WITH<</amber>> rev <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> mechanic_id, <<amber>>SUM<</amber>>(total_cost) <<amber>>AS<</amber>> revenue
          <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> mechanic_id
      ),
      avg_rev <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> <<amber>>AVG<</amber>>(revenue) <<amber>>AS<</amber>> avg_rev <<amber>>FROM<</amber>> rev
      )
      <<amber>>SELECT<</amber>> rev.mechanic_id, rev.revenue, avg_rev.avg_rev
      <<amber>>FROM<</amber>> rev, avg_rev;

  <<dim>>Same answer as a nested subquery, but each step has a name and a single<</dim>>
  <<dim>>responsibility. Treat each CTE like a Python function.<</dim>>

# RECURSIVE CTEs

  <<purple>>WITH RECURSIVE<</purple>> lets a CTE reference itself, with a base case and a
  recursive case joined by <<amber>>UNION ALL<</amber>>. The classic uses are generating
  number sequences and walking parent-child hierarchies.

      <<purple>>WITH RECURSIVE<</purple>> cnt(n) <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> <<blue>>1<</blue>>
          <<amber>>UNION ALL<</amber>>
          <<amber>>SELECT<</amber>> n + <<blue>>1<</blue>> <<amber>>FROM<</amber>> cnt <<amber>>WHERE<</amber>> n < <<blue>>5<</blue>>
      )
      <<amber>>SELECT<</amber>> n <<amber>>FROM<</amber>> cnt;

  <<red>>Always include a stop condition<</red>> in the <<amber>>WHERE<</amber>> clause of the
  recursive arm or the database will spin until you cancel it.

# SELF-JOINS

  A table joined to itself, aliased twice. Use it to compare rows against
  other rows in the same table: pairs with the same key, transitive
  relationships, "find duplicates."

      <<amber>>FROM<</amber>> mechanics a <<amber>>JOIN<</amber>> mechanics b
      <<amber>>ON<</amber>> a.specialty = b.specialty <<amber>>AND<</amber>> a.id < b.id

  <<dim>>The id < id constraint dedupes pairs (a,b) and (b,a) so you don't get<</dim>>
  <<dim>>every match twice.<</dim>>

# CORRELATED SUBQUERIES

  A subquery that references the outer query's row. Logically, it runs once
  per outer row. Use sparingly because the cost is per-row.

      <<amber>>SELECT<</amber>> id, name,
             (<<amber>>SELECT<</amber>> <<amber>>COUNT<</amber>>(*) <<amber>>FROM<</amber>> vehicles <<amber>>WHERE<</amber>> customer_id = customers.id) <<amber>>AS<</amber>> vc
      <<amber>>FROM<</amber>> customers;

  Often equivalent to a <<amber>>LEFT JOIN<</amber>> + <<amber>>GROUP BY<</amber>>. The join form
  is usually faster on real data.

# WINDOWS WITH AGGREGATE FUNCTIONS

  Aggregates inside <<amber>>OVER<</amber>> become running calculations. With
  <<amber>>ORDER BY<</amber>> inside the window, the frame defaults to "all rows up to
  this one" — that's the cumulative pattern.

      <<amber>>SELECT<</amber>> id, total_cost,
             <<amber>>SUM<</amber>>(total_cost) <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> id) <<amber>>AS<</amber>> running_total

  Empty <<amber>>OVER<</amber>> () is the whole table. That gives you "this row's share
  of the total" in one expression: total_cost * 100.0 / <<amber>>SUM<</amber>>(total_cost)
  <<amber>>OVER<</amber>> ().

# THE PIVOT TRICK

  <<amber>>SUM<</amber>>(<<amber>>CASE WHEN<</amber>> cond <<amber>>THEN<</amber>> <<blue>>1<</blue>> <<amber>>ELSE<</amber>>
  <<blue>>0<</blue>> <<amber>>END<</amber>>) counts conditional matches per group. Stack one per
  category and you've pivoted long-format rows into wide-format columns
  without a true PIVOT operator.

# NTILE

  <<purple>>NTILE<</purple>>(<<blue>>4<</blue>>) <<amber>>OVER<</amber>> (...) splits ordered rows into N
  roughly-equal buckets. Quartiles, deciles, percentile bins. ML uses the same
  trick to discretize continuous features for tree models or to define
  evaluation cohorts.

  NEXT TIER: there isn't one in SQL terms. You've got the working vocabulary
  for analytics queries. The next axis is performance: indexes, query plans,
  partitioning at the storage layer. That's a different track.

---

# EXAMPLE 1

  CTE used as a step in a multi-stage calculation. Each name describes one
  thing and the final query reads like a recipe.

      <<amber>>WITH<</amber>> per_status <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> status, <<amber>>SUM<</amber>>(total_cost) <<amber>>AS<</amber>> total
          <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> status
      ),
      grand <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> <<amber>>SUM<</amber>>(total) <<amber>>AS<</amber>> grand_total <<amber>>FROM<</amber>> per_status
      )
      <<amber>>SELECT<</amber>> status, total, total * <<blue>>100.0<</blue>> / grand_total <<amber>>AS<</amber>> pct
      <<amber>>FROM<</amber>> per_status, grand;

  <<dim>>Two CTEs, one final select. The second CTE depends on the first. This<</dim>>
  <<dim>>is the pattern any analyst query of moderate complexity ends up using.<</dim>>

# EXAMPLE 2

  Self-join to find pairs sharing an attribute. Useful when you want to
  enumerate co-occurrences.

      <<amber>>SELECT<</amber>> a.name <<amber>>AS<</amber>> mech_a, b.name <<amber>>AS<</amber>> mech_b, a.specialty
      <<amber>>FROM<</amber>> mechanics a
      <<amber>>JOIN<</amber>> mechanics b
        <<amber>>ON<</amber>> a.specialty = b.specialty
       <<amber>>AND<</amber>> a.id < b.id;

  <<dim>>Two rows of the same table aliased a and b. The id < id rule keeps each<</dim>>
  <<dim>>unordered pair listed once. Drop the constraint and you get every pair<</dim>>
  <<dim>>twice plus self-pairs.<</dim>>

# EXAMPLE 3

  Tying it all together: a CTE plus a window function. Computes per-mechanic
  revenue and ranks against the global mean. This is roughly what a model
  evaluation cohort report looks like in production: bucket, rank, normalize.

      <<amber>>WITH<</amber>> rev <<amber>>AS<</amber>> (
          <<amber>>SELECT<</amber>> mechanic_id, <<amber>>SUM<</amber>>(total_cost) <<amber>>AS<</amber>> revenue
          <<amber>>FROM<</amber>> work_orders <<amber>>GROUP BY<</amber>> mechanic_id
      )
      <<amber>>SELECT<</amber>> mechanic_id, revenue,
             <<purple>>RANK<</purple>>() <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> revenue <<amber>>DESC<</amber>>) <<amber>>AS<</amber>> rnk,
             revenue - <<amber>>AVG<</amber>>(revenue) <<amber>>OVER<</amber>> () <<amber>>AS<</amber>> dev_from_mean,
             <<purple>>NTILE<</purple>>(<<blue>>4<</blue>>) <<amber>>OVER<</amber>> (<<amber>>ORDER BY<</amber>> revenue <<amber>>DESC<</amber>>) <<amber>>AS<</amber>> quartile
      <<amber>>FROM<</amber>> rev;

  <<dim>>Three windows, one CTE, one query. Rank, deviation from mean, and<</dim>>
  <<dim>>quartile bucket all computed in a single pass. If you can read this, you<</dim>>
  <<dim>>can read most analyst SQL in the wild.<</dim>>

