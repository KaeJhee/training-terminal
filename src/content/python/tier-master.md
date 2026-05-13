# PYTHON · TIER 5 CONCEPTS (MASTER)

  <<dim>>The mental model that makes everything else click: in Python, functions
  are values. You pass them, return them, decorate them, and close over their
  environment. The same machinery that makes generators lazy makes decorators
  declarative.<</dim>>

# GENERATORS

  A function that contains <<amber>>yield<</amber>> is a generator. Each <<amber>>yield<</amber>>
  produces a value and pauses execution. The next call resumes where it left
  off. State persists across yields without you wiring it up.

      <<amber>>def<</amber>> <<teal>>count_up_to<</teal>>(n):
          <<amber>>for<</amber>> i <<amber>>in<</amber>> <<amber>>range<</amber>>(<<blue>>1<</blue>>, n + <<blue>>1<</blue>>):
              <<amber>>yield<</amber>> i

  <<bold>>list(count_up_to(4))<</bold>> gives <<bold>>[1, 2, 3, 4]<</bold>>. The list call
  drives the generator to exhaustion. In a <<amber>>for<</amber>> loop the generator
  yields one value per iteration with no intermediate list.

  <<dim>>This is how the entire iterator protocol works. Files, ranges,
  enumerate, zip, dict.items() are all driven by the same yield-style
  pause-and-resume mechanism.<</dim>>

# CLOSURES AND NONLOCAL

  An inner function "closes over" the names visible at definition. Mutating
  those names from inside requires <<amber>>nonlocal<</amber>> (for enclosing scope)
  or <<amber>>global<</amber>> (for module scope). Reading is automatic.

      <<amber>>def<</amber>> <<teal>>make_counter<</teal>>():
          n = <<blue>>0<</blue>>
          <<amber>>def<</amber>> <<teal>>inner<</teal>>():
              <<amber>>nonlocal<</amber>> n
              n += <<blue>>1<</blue>>
              <<amber>>return<</amber>> n
          <<amber>>return<</amber>> inner

  Each call to <<bold>>make_counter()<</bold>> creates a fresh <<bold>>n<</bold>> in a fresh
  scope. The returned <<bold>>inner<</bold>> keeps a private reference to it. This is
  how state lives inside functional-looking code.

# DECORATORS

  A decorator is a function that takes a function and returns a function.
  <<purple>>@name<</purple>> above a <<amber>>def<</amber>> is sugar for <<bold>>fn = name(fn)<</bold>>.

      <<amber>>def<</amber>> <<teal>>double<</teal>>(fn):
          <<amber>>def<</amber>> <<teal>>wrapper<</teal>>(*a, **kw):
              <<amber>>return<</amber>> fn(*a, **kw) * <<blue>>2<</blue>>
          <<amber>>return<</amber>> wrapper

      <<purple>>@double<</purple>>
      <<amber>>def<</amber>> <<teal>>val<</teal>>(): <<amber>>return<</amber>> <<blue>>21<</blue>>

  <<bold>>val()<</bold>> now returns 42. The wrapper closure intercepts every call
  and transforms the result. Logging, retries, caching, timing, auth checks
  are all decorators in production code. <<purple>>@functools.lru_cache<</purple>> is
  memoization in one line.

# RECURSION AND MEMOIZATION

  A recursive function calls itself with a smaller argument and a base case.
  Pure recursion blows up on overlapping subproblems. Caching the results
  (<<bold>>memoization<</bold>>) restores polynomial behavior.

      cache = {}
      <<amber>>def<</amber>> <<teal>>fib<</teal>>(n):
          <<amber>>if<</amber>> n <<amber>>in<</amber>> cache: <<amber>>return<</amber>> cache[n]
          <<amber>>if<</amber>> n < <<blue>>2<</blue>>: <<amber>>return<</amber>> n
          cache[n] = <<teal>>fib<</teal>>(n-<<blue>>1<</blue>>) + <<teal>>fib<</teal>>(n-<<blue>>2<</blue>>)
          <<amber>>return<</amber>> cache[n]

  <<dim>>ML aside: this is exactly the dynamic-programming trick used in
  Viterbi decoding, RNN forward passes, and any pipeline where overlapping
  subcomputations would otherwise dominate the cost.<</dim>>

# REDUCE

  <<amber>>functools.reduce<</amber>>(fn, iter) folds an iterable to a single value
  using a binary function. <<amber>>sum<</amber>> is reduce with addition.
  <<amber>>max<</amber>> is reduce with the larger-of-two function.

      <<amber>>from<</amber>> functools <<amber>>import<</amber>> <<teal>>reduce<</teal>>
      <<teal>>reduce<</teal>>(<<amber>>lambda<</amber>> a, b: a + b, nums)

  Mostly the built-ins (<<amber>>sum<</amber>>, <<amber>>max<</amber>>, <<amber>>min<</amber>>) are
  clearer. Reach for <<amber>>reduce<</amber>> when the operation is custom: building
  a tree, composing transforms, applying a reduction not in the stdlib.

# NAMEDTUPLE AND DATACLASS

  Two ways to define a record type without writing <<bold>>__init__<</bold>>
  yourself.

      <<amber>>from<</amber>> collections <<amber>>import<</amber>> <<teal>>namedtuple<</teal>>
      <<teal>>Point<</teal>> = <<teal>>namedtuple<</teal>>(<<green>>'Point'<</green>>, [<<green>>'x'<</green>>, <<green>>'y'<</green>>]])
      p = <<teal>>Point<</teal>>(<<blue>>3<</blue>>, <<blue>>4<</blue>>)
      p.x, p[<<blue>>0<</blue>>]    <<dim>>both work<</dim>>

      <<amber>>from<</amber>> dataclasses <<amber>>import<</amber>> <<teal>>dataclass<</teal>>
      <<purple>>@dataclass<</purple>>
      <<amber>>class<</amber>> <<teal>>Car<</teal>>:
          make: <<teal>>str<</teal>>
          year: <<teal>>int<</teal>>

  <<dim>>namedtuple is immutable, lightweight, and tuple-compatible. dataclass
  is mutable by default, takes type hints, and gives you __eq__ /
  __repr__ / __init__ for free. Use namedtuple for value objects you'll never
  mutate. Use dataclass for everything else.<</dim>>

# THE ML CONNECTION

  Generators are the pattern behind data loaders streaming batches without
  materializing the dataset. Decorators are how training-loop annotations
  (<<purple>>@torch.no_grad<</purple>>, <<purple>>@tf.function<</purple>>) hook in without
  changing the function body. Closures are how <<bold>>optimizer.step<</bold>>
  retains a reference to the model parameters. Recursion + memoization is
  the pattern behind any DP-style inference algorithm.

  The Python tier ends here. The next axis is libraries: numpy for
  vectorized math, pandas for tabular data, then a deep-learning framework.
  But the language itself doesn't get harder than what's above.

---

# EXAMPLE 1

  A decorator that times a function. Real-world decorators are this shape:
  wrap, do something around the call, return the result.

      <<amber>>import<</amber>> time

      <<amber>>def<</amber>> <<teal>>timed<</teal>>(fn):
          <<amber>>def<</amber>> <<teal>>wrapper<</teal>>(*a, **kw):
              start = time.perf_counter()
              result = fn(*a, **kw)
              elapsed = time.perf_counter() - start
              <<amber>>print<</amber>>(<<green>>f'{fn.__name__} took {elapsed:.4f}s'<</green>>)
              <<amber>>return<</amber>> result
          <<amber>>return<</amber>> wrapper

      <<purple>>@timed<</purple>>
      <<amber>>def<</amber>> <<teal>>heavy<</teal>>():
          <<amber>>return<</amber>> <<amber>>sum<</amber>>(<<amber>>range<</amber>>(<<blue>>10**6<</blue>>))

      <<teal>>heavy<</teal>>()    <<dim>>heavy took 0.0142s<</dim>>

  <<dim>>Logging frameworks, retry libraries, caching layers, and authorization
  hooks are all variations on this template. Read once, reach for it forever.<</dim>>

# EXAMPLE 2

  A generator that streams transformed data without materializing the
  intermediate list. This is roughly how data pipelines work at scale.

      <<amber>>def<</amber>> <<teal>>read_orders<</teal>>(path):
          <<amber>>with<</amber>> <<amber>>open<</amber>>(path) <<amber>>as<</amber>> f:
              <<amber>>for<</amber>> line <<amber>>in<</amber>> f:
                  yield line.strip().split(<<green>>','<</green>>)

      <<amber>>def<</amber>> <<teal>>as_floats<</teal>>(rows):
          <<amber>>for<</amber>> row <<amber>>in<</amber>> rows:
              <<amber>>yield<</amber>> [<<amber>>float<</amber>>(x) <<amber>>for<</amber>> x <<amber>>in<</amber>> row]

      <<amber>>for<</amber>> cost, qty <<amber>>in<</amber>> <<teal>>as_floats<</teal>>(<<teal>>read_orders<</teal>>(<<green>>'orders.csv'<</green>>)):
          <<amber>>print<</amber>>(cost * qty)

  <<dim>>Two generators chained. Constant memory regardless of file size. This
  is the same pattern behind PyTorch's DataLoader and TensorFlow's
  tf.data.Dataset, just with batching and shuffling layered on.<</dim>>

# EXAMPLE 3

  Putting it all together: a memoized recursive function defined with a
  decorator, applied to a problem that would be exponential without it. This
  is the production-ready pattern.

      <<amber>>from<</amber>> functools <<amber>>import<</amber>> <<teal>>lru_cache<</teal>>

      <<purple>>@lru_cache<</purple>>(maxsize=<<amber>>None<</amber>>)
      <<amber>>def<</amber>> <<teal>>fib<</teal>>(n):
          <<amber>>if<</amber>> n < <<blue>>2<</blue>>:
              <<amber>>return<</amber>> n
          <<amber>>return<</amber>> <<teal>>fib<</teal>>(n - <<blue>>1<</blue>>) + <<teal>>fib<</teal>>(n - <<blue>>2<</blue>>)

      <<amber>>print<</amber>>(<<teal>>fib<</teal>>(<<blue>>100<</blue>>))

  <<dim>>Without the decorator, fib(100) would do 1.7e21 calls. With it, 100.
  <</dim>><<purple>>@lru_cache<</purple>><<dim>> is closure + decorator + dict, all the ideas
  from this tier composed into a stdlib one-liner.

  That's the Python track. From <</dim>><<green>>'Hello, world'<</green>><<dim>> in tier 1
  to a memoized recursive Fibonacci in five tiers. The vocabulary fits on a
  page; the patterns take longer to internalize. See <</dim>><<qid:py_mas_10>><<dim>> for
  the manual version of the same idea, then come back here when you want it
  in one line.<</dim>>
