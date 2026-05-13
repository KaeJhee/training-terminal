# JAVASCRIPT · TIER 2 CONCEPTS (AMATEUR)

  <<dim>>Array methods, destructuring, and the first taste of ML framing.
  The shift this tier: from "loop and append" to "describe the result."<</dim>>

  At this tier the JS code starts to look like real-world JS. You stop
  writing for-loops with manual counters and start chaining array methods
  that read like English: filter these, then map those.

# ARRAY METHODS: MAP, FILTER, REDUCE

  Three methods cover most data transformations. They don't mutate the
  original array; they return a new value.

      <<amber>>const<</amber>> doubled = scores.<<purple>>map<</purple>>(x => x * <<blue>>2<</blue>>)
      <<amber>>const<</amber>> high    = probs.<<purple>>filter<</purple>>(p => p > <<blue>>0.5<</blue>>)
      <<amber>>const<</amber>> total   = counts.<<purple>>reduce<</purple>>((acc, v) => acc + v, <<blue>>0<</blue>>)

  <<bold>>.map<</bold>> transforms each element. <<bold>>.filter<</bold>> keeps elements
  where the predicate returns true. <<bold>>.reduce<</bold>> folds the array down
  to a single value using a binary function and an initial accumulator.

  <<dim>>Reduce's initial accumulator (the second argument) is critical —
  forgetting it makes the first array element the seed, which silently
  changes the answer for the empty-array case.<</dim>>

# CHAINING

  Array methods return arrays, so you can chain them. Filter narrows;
  map transforms. Together they replace most for-loops with branching
  logic.

      <<amber>>const<</amber>> open_costs = orders
          .<<purple>>filter<</purple>>(o => o.status === <<green>>'Open'<</green>>)
          .<<purple>>map<</purple>>(o => o.cost)

  <<dim>>Equivalent for-loop is six lines. The chained version is one
  expression and reads top-down. See <<qid:js_am_09>>.<</dim>>

# DESTRUCTURING

  Pull values out of arrays and objects with one statement.

      <<amber>>const<</amber>> [x, y] = point                  <<dim>>array form<</dim>>
      <<amber>>const<</amber>> { name, phone } = customer      <<dim>>object form<</dim>>

  Object destructuring matches by key name. Rename with <<bold>>{ name:
  customer_name }<</bold>>. Set defaults with <<bold>>{ name = 'unknown' }<</bold>>. This
  pattern shows up in function parameters constantly.

# DEFAULT ARGUMENTS

  Function parameters can have default values. Used when the caller
  omits the argument.

      <<amber>>function<</amber>> <<teal>>total_with_tax<</teal>>(amount, rate=<<blue>>0.08<</blue>>) {
          <<amber>>return<</amber>> amount * (<<blue>>1<</blue>> + rate)
      }

  Defaults are evaluated each call, not once at definition time — different
  from Python's gotcha. Mutable defaults are safe in JS.

# SPREAD OPERATOR

  <<bold>>...arr<</bold>> unpacks an array's elements into a context. Combine arrays:
  <<bold>>[...a, ...b]<</bold>>. Pass elements as separate arguments:
  <<bold>>Math.max(...nums)<</bold>>.

      <<amber>>const<</amber>> all = [...primary, ...backup]

# LIGHT ML FRAMING

  At this tier you'll meet your first ML primitives, framed as JS tasks.
  <<bold>>One-hot encoding<</bold>> turns a class index into a vector with 1 at
  that index and 0 elsewhere — used to feed categorical data into models.
  <<bold>>Argmax<</bold>> returns the index of the largest value — used to pick
  the predicted class from a vector of model scores.

  <<dim>>No ML knowledge required to solve them. Both are pure array
  manipulation; the ML names are just the labels the field uses for these
  shapes.<</dim>>

  NEXT TIER: arrow functions in earnest, closures, async/await, JSON, and
  the first explicit-ML primitives — softmax and cosine similarity. Arrays
  give way to working with promises and shared state.

---

# EXAMPLE 1

  Chain filter and map. The shape is <<bold>>narrow then transform<</bold>>.

      <<amber>>const<</amber>> orders = [
          { cost: <<blue>>100<</blue>>, status: <<green>>'Open'<</green>> },
          { cost: <<blue>>250<</blue>>, status: <<green>>'Closed'<</green>> },
          { cost: <<blue>>75<</blue>>,  status: <<green>>'Open'<</green>> },
      ]
      <<amber>>const<</amber>> open_costs = orders
          .<<purple>>filter<</purple>>(o => o.status === <<green>>'Open'<</green>>)
          .<<purple>>map<</purple>>(o => o.cost)
      console.log(open_costs)    <<dim>>[100, 75]<</dim>>

  <<dim>>Three lines replace a six-line for-loop. The intent is in the verbs:
  "filter to open, then map to cost." When you find yourself writing a
  for-loop with an if inside, reach for filter+map first.<</dim>>

# EXAMPLE 2

  Object destructuring in a function parameter. The function reads its
  inputs straight from a config object.

      <<amber>>function<</amber>> <<teal>>format_customer<</teal>>({ name, phone = <<green>>'N/A'<</green>> }) {
          <<amber>>return<</amber>> <<green>>`${name} — ${phone}`<</green>>
      }
      console.log(<<teal>>format_customer<</teal>>({ name: <<green>>'Kara'<</green>> }))
      <<dim>>'Kara — N/A'<</dim>>

  <<dim>>Three things in one signature: pull name and phone out of the arg,
  default phone to 'N/A' if missing, then build the output with a template
  literal. This is what a real-world API endpoint handler looks like.<</dim>>

# EXAMPLE 3

  One-hot encoding, previewing the next tier's softmax problem. Right now
  the task is "build an array with 1 at one index and 0 elsewhere":

      <<amber>>function<</amber>> <<teal>>one_hot<</teal>>(index, length) {
          <<amber>>return<</amber>> Array.<<purple>>from<</purple>>({ length }, (_, i) => i === index ? <<blue>>1<</blue>> : <<blue>>0<</blue>>)
      }
      <<teal>>one_hot<</teal>>(<<blue>>2<</blue>>, <<blue>>5<</blue>>)    <<dim>>[0, 0, 1, 0, 0]<</dim>>

  <<dim>>At Intermediate tier you'll write softmax, which goes the OTHER
  direction: it takes a vector of scores and returns a vector of
  probabilities. one_hot is the "answer key" shape; softmax is the "model
  output" shape. Both are arrays of length N where N is the number of
  classes. See <</dim>><<qid:js_int_01>><<dim>>.<</dim>>
