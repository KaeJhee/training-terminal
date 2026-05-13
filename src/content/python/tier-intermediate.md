# PYTHON · TIER 3 CONCEPTS (INTERMEDIATE)

  <<dim>>The shift this tier: from imperative "do these steps" to declarative
  "describe the result." Comprehensions, lambdas, and the functional triad
  (map, filter, reduce-style) all serve that shift.<</dim>>

# LIST COMPREHENSIONS

  A comprehension is a one-line expression that builds a collection from an
  iterable. Three pieces: the output expression, the <<amber>>for<</amber>> clause,
  and an optional <<amber>>if<</amber>> filter.

      squared    = [x**<<blue>>2<</blue>> <<amber>>for<</amber>> x <<amber>>in<</amber>> nums]
      high       = [p <<amber>>for<</amber>> p <<amber>>in<</amber>> prices <<amber>>if<</amber>> p > <<blue>>500<</blue>>]
      labeled    = [(name, len(name)) <<amber>>for<</amber>> name <<amber>>in<</amber>> mechanics]

  <<dim>>Read it left-to-right: "for each x in nums, give me x squared." The
  filter, when present, runs before the output expression.<</dim>>

# DICT AND SET COMPREHENSIONS

  Same shape, different braces. Dict comprehensions need a key:value pair in
  the output expression.

      squares = {x: x**<<blue>>2<</blue>> <<amber>>for<</amber>> x <<amber>>in<</amber>> <<amber>>range<</amber>>(<<blue>>1<</blue>>, <<blue>>6<</blue>>)}
      lower   = {tag.lower() <<amber>>for<</amber>> tag <<amber>>in<</amber>> tags}

# LAMBDAS

  An anonymous, single-expression function. Useful as an argument to
  higher-order functions like <<amber>>sorted<</amber>>, <<amber>>map<</amber>>, <<amber>>filter<</amber>>.
  No statements, just an expression.

      sorted(people, key=<<amber>>lambda<</amber>> p: p[<<green>>'age'<</green>>])

  <<dim>>If your lambda is more than one expression, write a real function with
  <</dim>><<amber>>def<</amber>><<dim>>. Readability matters more than brevity.<</dim>>

# MAP, FILTER, AND THE COMPREHENSION TRADEOFF

  <<amber>>map<</amber>>(fn, iter) applies fn to every element. <<amber>>filter<</amber>>(pred,
  iter) keeps elements where pred is truthy. Both return iterators, so you
  usually wrap them in <<amber>>list<</amber>>().

      <<amber>>list<</amber>>(<<amber>>map<</amber>>(<<amber>>lambda<</amber>> x: x * <<blue>>2<</blue>>, nums))
      <<amber>>list<</amber>>(<<amber>>filter<</amber>>(<<amber>>lambda<</amber>> x: x % <<blue>>2<</blue>> == <<blue>>0<</blue>>, nums))

  Most Pythonistas prefer comprehensions for these because the syntax is more
  direct: <<bold>>[x*2 for x in nums]<</bold>> vs the map version. Both are correct.
  Comprehensions chain better and skip the <<amber>>list<</amber>>() wrapper.

# DEFAULT ARGUMENTS AND .get()

  Function defaults handle "usually this, sometimes that" without a wrapper.
  <<bold>>dict.get<</bold>>(key, default) does the same thing for dictionary lookups.

      <<amber>>def<</amber>> <<teal>>total_with_tax<</teal>>(amount, rate=<<blue>>0.08<</blue>>):
          <<amber>>return<</amber>> amount * (<<blue>>1<</blue>> + rate)

      d.get(<<green>>'missing'<</green>>, <<blue>>0<</blue>>)

  <<dim>>Both protect you from "this thing might not be present." Pick the form
  that fits the call site.<</dim>>

# SETS

  Unordered collections of unique elements. Useful when you need fast
  membership tests or set algebra. <<bold>>a & b<</bold>> is intersection, <<bold>>a |
  b<</bold>> is union, <<bold>>a - b<</bold>> is difference.

# F-STRING FORMATTING

  Specifiers go after a colon inside the brace. <<bold>>:.2f<</bold>> is two-decimal
  float. <<bold>>:,<</bold>> is thousand separators. They compose: <<bold>>:,.2f<</bold>>.

      <<green>>f'Price: ${price:.2f}'<</green>>    <<dim>>Price: $1500.00<</dim>>
      <<green>>f'Count: {n:,}'<</green>>            <<dim>>Count: 1,234,567<</dim>>

  <<dim>>ML aside: comprehensions and lambdas are how you transform features in
  preprocessing pipelines without reaching for pandas or numpy. The "describe
  the result" mindset translates directly to vectorized operations.<</dim>>

  NEXT TIER: classes, exception handling, and the standard-library data
  structures (Counter, defaultdict). Once you can model entities and handle
  error paths, you can build real applications.

---

# EXAMPLE 1

  Comprehension with a filter. The shape is <<bold>>[output for item in iter
  if predicate]<</bold>>.

      orders = [{<<green>>'cost'<</green>>: <<blue>>100<</blue>>, <<green>>'status'<</green>>: <<green>>'Open'<</green>>},
                {<<green>>'cost'<</green>>: <<blue>>250<</blue>>, <<green>>'status'<</green>>: <<green>>'Closed'<</green>>},
                {<<green>>'cost'<</green>>: <<blue>>75<</blue>>,  <<green>>'status'<</green>>: <<green>>'Open'<</green>>}]
      open_costs = [o[<<green>>'cost'<</green>>] <<amber>>for<</amber>> o <<amber>>in<</amber>> orders <<amber>>if<</amber>> o[<<green>>'status'<</green>>] == <<green>>'Open'<</green>>]
      <<amber>>print<</amber>>(<<amber>>sum<</amber>>(open_costs))    <<dim>>175<</dim>>

  <<dim>>Replace the for-loop-with-append-and-condition pattern with this. Same
  result, half the lines, easier to read once you've internalized the shape.<</dim>>

# EXAMPLE 2

  Sort by a derived key with a lambda. Without a key, sorted compares whole
  elements. With one, sorted compares whatever the key returns.

      people = [{<<green>>'name'<</green>>: <<green>>'Dave'<</green>>, <<green>>'age'<</green>>: <<blue>>30<</blue>>},
                {<<green>>'name'<</green>>: <<green>>'Emily'<</green>>, <<green>>'age'<</green>>: <<blue>>22<</blue>>}]
      youngest_first = <<amber>>sorted<</amber>>(people, key=<<amber>>lambda<</amber>> p: p[<<green>>'age'<</green>>])

  <<dim>>Add reverse=True to flip the order. Pass tuples in the key for tiebreakers:
  key=lambda p: (p<</dim>><<green>>'team'<</green>><<dim>>, -p<</dim>><<green>>'score'<</green>><<dim>>) sorts by
  team ascending then by score descending.<</dim>>

# EXAMPLE 3

  Class-shaped data, previewing OOP at the next tier. Right now you model an
  entity as a dict and act on it with functions:

      <<amber>>def<</amber>> <<teal>>is_open<</teal>>(order):
          <<amber>>return<</amber>> order[<<green>>'status'<</green>>] == <<green>>'Open'<</green>>

      orders = [{<<green>>'cost'<</green>>: <<blue>>100<</blue>>, <<green>>'status'<</green>>: <<green>>'Open'<</green>>}, ...]
      open_jobs = [o <<amber>>for<</amber>> o <<amber>>in<</amber>> orders <<amber>>if<</amber>> <<teal>>is_open<</teal>>(o)]

  <<dim>>At Experienced tier the function moves onto the entity itself:

  <</dim>>      <<amber>>class<</amber>> <<teal>>WorkOrder<</teal>>:
          <<amber>>def<</amber>> <<teal>>__init__<</teal>>(self, cost, status): ...
          <<amber>>def<</amber>> <<teal>>is_open<</teal>>(self): <<amber>>return<</amber>> self.status == <<green>>'Open'<</green>>

  <<dim>>Same logic, different attachment point. See <</dim>><<qid:py_exp_01>><<dim>>.<</dim>>
