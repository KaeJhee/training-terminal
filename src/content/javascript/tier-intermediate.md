# JAVASCRIPT · TIER 3 CONCEPTS (INTERMEDIATE)

  <<dim>>Closures, asynchronous code, and the first explicit-ML primitives.
  Each idea is small individually; together they're how real JS gets
  written.<</dim>>

# ARROW FUNCTIONS AND CLOSURES

  Arrow functions are JS's anonymous-function syntax, optimized for use
  as callbacks. The classic non-trivial use is closing over an enclosing
  scope's variable.

      <<amber>>function<</amber>> <<teal>>make_counter<</teal>>() {
          <<amber>>let<</amber>> n = <<blue>>0<</blue>>
          <<amber>>return<</amber>> () => ++n
      }

      <<amber>>const<</amber>> a = <<teal>>make_counter<</teal>>()
      a()    <<dim>>1<</dim>>
      a()    <<dim>>2<</dim>>

  Each call to make_counter creates a fresh n in a fresh scope. The
  returned arrow function keeps a private reference to that n. This is
  how state lives inside functional-looking code.

  <<dim>>Closures are the prerequisite for understanding why generators work
  (Master tier), why React's useState returns what it does, and why
  decorators wrap state — they're the most leveraged single concept in
  modern JS. See <</dim>><<qid:js_int_02>><<dim>>.<</dim>>

# ASYNC/AWAIT

  A <<amber>>Promise<</amber>> represents a future value. <<amber>>async<</amber>> declares
  a function that returns a Promise. <<amber>>await<</amber>> unwraps one inside an
  async function — the function pauses, the resolved value is returned.

      <<amber>>const<</amber>> result = <<amber>>await<</amber>> fake_fetch()

  <<bold>>Promise.all([p1, p2, p3])<</bold>> runs Promises in parallel and resolves
  to an array of values. Use it whenever the next step doesn't depend on
  any specific Promise's result.

      <<amber>>const<</amber>> [a, b, c] = <<amber>>await<</amber>> Promise.<<purple>>all<</purple>>([fa(), fb(), fc()])

  Awaiting a sequence one-by-one is N times slower than Promise.all when
  the calls are independent.

# ERROR HANDLING

  <<amber>>try<</amber>> / <<amber>>catch<</amber>> catches synchronous throws AND awaited
  Promise rejections. This is the single biggest reason async code goes
  wrong: a Promise that rejects without try/catch surfaces as an
  unhandled-rejection warning, not a normal stack trace.

      <<amber>>try<</amber>> {
          <<amber>>const<</amber>> data = <<amber>>await<</amber>> fetch_user(id)
      } <<amber>>catch<</amber>> (e) {
          console.error(<<green>>'failed:'<</green>>, e.message)
      }

  Inside async/await, treat every external call as if it could reject.

# JSON

  <<amber>>JSON.parse<</amber>>(str) converts a JSON string to a value.
  <<amber>>JSON.stringify<</amber>>(v) converts back. The two roundtrip cleanly for
  plain data — strings, numbers, booleans, null, arrays, objects.

      <<amber>>const<</amber>> obj = JSON.<<purple>>parse<</purple>>(raw)
      obj.count += <<blue>>1<</blue>>
      <<amber>>const<</amber>> out = JSON.<<purple>>stringify<</purple>>(obj)

  <<dim>>Parsing fails on malformed input by throwing — wrap in try/catch
  if input might be invalid. See <<qid:js_int_09>>.<</dim>>

# OBJECT ITERATION

  <<amber>>Object.values<</amber>>(obj) gives you the array of values.
  <<amber>>Object.keys<</amber>>(obj) gives the keys. <<amber>>Object.entries<</amber>>(obj)
  gives [key, value] pairs.

      <<amber>>const<</amber>> total = <<amber>>Object<</amber>>.values(status_counts).<<purple>>reduce<</purple>>((a,b)=>a+b, <<blue>>0<</blue>>)

# EXPLICIT-ML PRIMITIVES

  This tier introduces the first ML algorithms you'll implement directly:

  <<bold>>Softmax<</bold>> turns a vector of arbitrary scores into a probability
  distribution. Each output is exp(x_i) / sum_of_all_exp_values. Outputs
  are positive and sum to 1.

  <<bold>>Cosine similarity<</bold>> measures the angle between two vectors,
  ignoring their magnitudes. dot(a,b) / (|a| · |b|). Identical direction
  gives 1, orthogonal gives 0.

  <<bold>>Dot product<</bold>> is the sum of element-wise products. Building block
  for cosine similarity, matrix multiply, and any vector-vector
  computation in ML.

  <<bold>>Euclidean distance<</bold>> is sqrt(sum of squared differences). The
  geometric distance between two vectors.

  <<dim>>All four are array iterations with one or two accumulators. The
  algebraic content is light; the JS idioms are the actual lesson.<</dim>>

  NEXT TIER: classes, inheritance, getters and setters, fetch idioms,
  promise chaining, and ML primitives heavier in flavor — vector
  arithmetic, mean pooling, cross-entropy loss, a tiny feedforward pass.

---

# EXAMPLE 1

  A closure that maintains private state. The inner function "remembers"
  the variable from its enclosing scope across calls.

      <<amber>>function<</amber>> <<teal>>make_logger<</teal>>(prefix) {
          <<amber>>let<</amber>> count = <<blue>>0<</blue>>
          <<amber>>return<</amber>> (msg) => {
              count += <<blue>>1<</blue>>
              console.log(<<green>>`[${prefix} ${count}] ${msg}`<</green>>)
          }
      }

      <<amber>>const<</amber>> log = <<teal>>make_logger<</teal>>(<<green>>'INFO'<</green>>)
      log(<<green>>'started'<</green>>)     <<dim>>[INFO 1] started<</dim>>
      log(<<green>>'connected'<</green>>)   <<dim>>[INFO 2] connected<</dim>>

  <<dim>>The count and prefix variables only live inside log. Two separate
  calls to make_logger produce two independent counters with independent
  prefixes. This is how event handlers, retry wrappers, and rate limiters
  are built in real code.<</dim>>

# EXAMPLE 2

  Async work with try/catch and Promise.all. The pattern: do as much in
  parallel as possible, catch errors at the boundary.

      <<amber>>async<</amber>> <<amber>>function<</amber>> <<teal>>load_dashboard<</teal>>(customer_id) {
          <<amber>>try<</amber>> {
              <<amber>>const<</amber>> [customer, vehicles, orders] = <<amber>>await<</amber>> Promise.<<purple>>all<</purple>>([
                  fetch_customer(customer_id),
                  fetch_vehicles(customer_id),
                  fetch_orders(customer_id),
              ])
              <<amber>>return<</amber>> { customer, vehicles, orders }
          } <<amber>>catch<</amber>> (e) {
              console.error(<<green>>'dashboard load failed:'<</green>>, e.message)
              <<amber>>return<</amber>> <<amber>>null<</amber>>
          }
      }

  <<dim>>Three independent fetches run in parallel — total latency is the
  slowest one, not the sum. Any rejection lands in the catch, which
  returns null so the caller has a single shape to handle. This is the
  template for nearly every "load page data" function in a SPA.<</dim>>

# EXAMPLE 3

  Softmax, the canonical first ML primitive. Two passes: compute the
  exponentials, then divide by their sum.

      <<amber>>function<</amber>> <<teal>>softmax<</teal>>(xs) {
          <<amber>>const<</amber>> exps = xs.<<purple>>map<</purple>>(x => <<amber>>Math<</amber>>.exp(x))
          <<amber>>const<</amber>> sum  = exps.<<purple>>reduce<</purple>>((a, b) => a + b, <<blue>>0<</blue>>)
          <<amber>>return<</amber>> exps.<<purple>>map<</purple>>(e => e / sum)
      }

      <<teal>>softmax<</teal>>([<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>])    <<dim>>[0.090, 0.245, 0.665]<</dim>>

  <<dim>>At Experienced tier you'll write the numerically-stable version
  that subtracts max(xs) before exponentiating — same answer mathematically,
  but doesn't overflow on large inputs. The naive form above gives NaN on
  inputs around 700+. See <</dim>><<qid:js_exp_08>><<dim>>.<</dim>>
