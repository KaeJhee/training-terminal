# JAVASCRIPT · TIER 5 CONCEPTS (MASTER)

  <<dim>>Last tier. The ideas here aren't more difficult; they're the
  patterns that production JS uses to express ML pipelines compactly.
  Generators stream data lazily. Proxy intercepts property access. Typed
  arrays let you work directly with the same memory layout your numerical
  libraries use.<</dim>>

# GENERATORS

  <<amber>>function*<</amber>> declares a generator. <<amber>>yield<</amber>> produces a
  value and pauses. The next call resumes where it left off. State
  persists across yields without you wiring it up.

      <<amber>>function*<</amber>> <<teal>>range_gen<</teal>>(start, end) {
          <<amber>>for<</amber>> (<<amber>>let<</amber>> i = start; i < end; i++) <<amber>>yield<</amber>> i
      }

  <<bold>>Array.from(range_gen(1, 5))<</bold>> gives <<bold>>[1, 2, 3, 4]<</bold>>. Inside
  a <<amber>>for...of<</amber>> loop the generator yields one value per iteration
  with no intermediate array.

  <<dim>>This is how the iterator protocol works. for...of, spread, and
  Array.from all consume the same yield-based protocol. The same machinery
  powers data loaders that stream batches without materializing the full
  dataset.<</dim>>

# PROXY

  <<amber>>Proxy<</amber>> wraps an object and intercepts operations on it. The
  handler defines <<bold>>get<</bold>>, <<bold>>set<</bold>>, <<bold>>has<</bold>>, and other
  traps. Anything you don't define falls through to the target.

      <<amber>>const<</amber>> default_dict = () => <<amber>>new<</amber>> Proxy({}, {
          <<teal>>get<</teal>>(target, p) { <<amber>>return<</amber>> p <<amber>>in<</amber>> target ? target[p] : <<blue>>0<</blue>> }
      })

  Use cases: validation on write, computed defaults on read, observability
  hooks. ORMs, state-management libraries, and reactive frameworks all
  use Proxy underneath.

# TYPED ARRAYS

  <<amber>>Int8Array<</amber>>, <<amber>>Float32Array<</amber>>, <<amber>>Float64Array<</amber>>, and
  friends are arrays with fixed numeric layouts. Same memory representation
  numerical libraries use under the hood.

      <<amber>>const<</amber>> vec = <<amber>>new<</amber>> Float32Array([<<blue>>3<</blue>>, <<blue>>4<</blue>>])
      vec[<<blue>>0<</blue>>]    <<dim>>3 (as Float32, not JS Number)<</dim>>

  Convert to a regular array with <<bold>>Array.from(typed)<</bold>>. Construct
  from a regular array by passing it to the constructor. Float32Array is
  what you'd use to interop with WASM models or shape memory the way a
  GPU expects.

# CLOSURES + FUNCTIONS AS VALUES

  Functions are first-class. You pass them, return them, store them in
  arrays, decorate them. Memoization is the canonical Master example —
  wrap a function in a cache without changing its body.

      <<amber>>function<</amber>> <<teal>>memoize<</teal>>(fn) {
          <<amber>>const<</amber>> cache = <<amber>>new<</amber>> <<teal>>Map<</teal>>()
          <<amber>>return<</amber>> (x) => {
              <<amber>>if<</amber>> (cache.has(x)) <<amber>>return<</amber>> cache.get(x)
              <<amber>>const<</amber>> v = fn(x)
              cache.set(x, v)
              <<amber>>return<</amber>> v
          }
      }

  Same shape underlies retry wrappers, rate limiters, async-throttling.
  Reach for "wrap a function in a function" when you want to add behavior
  without modifying the original.

# THE THIS BINDING GOTCHA

  <<bold>>this<</bold>> inside a regular <<amber>>function<</amber>> is determined by the
  call site — who's calling, not where it was defined. Inside an arrow
  function, <<bold>>this<</bold>> is inherited from the enclosing lexical scope.

      class Counter {
          tick() {
              <<amber>>return<</amber>> Promise.resolve().<<purple>>then<</purple>>(() => this.start + <<blue>>1<</blue>>)
          }
      }

  <<red>>Replace the arrow with <</red>><<amber>>function<</amber>><<red>>() { return this.start + 1 }<</red>>
  <<red>>and this is undefined inside the callback<</red>> — Promise.then doesn't
  pass the surrounding instance. The arrow function inherits this from
  tick's scope, which IS the instance. <<dim>>See <<qid:js_mas_07>>.<</dim>>

# ML PRIMITIVES — RETRIEVAL

  This tier closes with the operations behind semantic search and
  retrieval-augmented generation:

  <<bold>>Embedding lookup<</bold>> selects rows from an embedding matrix by index.
  This is what a model's first layer does for token IDs.

  <<bold>>Layer normalization<</bold>> standardizes a vector to mean 0, variance 1.
  Used in transformers between every attention block.

  <<bold>>Top-k retrieval<</bold>> returns the k highest-scoring indices. Used to
  pick the most-similar embeddings to a query.

  <<bold>>Matrix-vector multiply (matvec)<</bold>> is the core operation of a
  linear layer's forward pass — for each row of the matrix, dot it with
  the input vector.

  <<dim>>Combined: take a query, embed it, compute cosine similarity against
  every row of an embedding matrix, return the top-k indices. That's
  semantic search in 10 lines of JS. The capstone of this track.<</dim>>

  NEXT TIER: there isn't one. You've got the working vocabulary for ML
  primitives in JS. The next axes are libraries (numpy/torch in Python,
  ONNX in JS) and frameworks. The language itself doesn't get harder than
  what's here.

---

# EXAMPLE 1

  A generator that streams transformed data without materializing the
  intermediate array. Constant memory regardless of input size.

      <<amber>>function*<</amber>> <<teal>>as_floats<</teal>>(rows) {
          <<amber>>for<</amber>> (<<amber>>const<</amber>> row <<amber>>of<</amber>> rows) {
              <<amber>>yield<</amber>> row.<<purple>>map<</purple>>(x => <<amber>>Number<</amber>>(x))
          }
      }

      <<amber>>for<</amber>> (<<amber>>const<</amber>> [cost, qty] <<amber>>of<</amber>> <<teal>>as_floats<</teal>>(csv_rows)) {
          console.log(cost * qty)
      }

  <<dim>>Two iterators chained. The CSV rows are read lazily; as_floats
  yields each parsed row on demand; the for-of loop consumes them one at
  a time. This is the same pattern behind PyTorch's DataLoader and
  TensorFlow's tf.data.Dataset, just with batching and shuffling layered
  on.<</dim>>

# EXAMPLE 2

  A Proxy that adds default values for missing keys. Same shape underlies
  reactive frameworks where reads trigger dependency tracking.

      <<amber>>function<</amber>> <<teal>>default_dict<</teal>>(fallback) {
          <<amber>>return<</amber>> <<amber>>new<</amber>> Proxy({}, {
              <<teal>>get<</teal>>(target, p) {
                  <<amber>>return<</amber>> p <<amber>>in<</amber>> target ? target[p] : fallback
              }
          })
      }

      <<amber>>const<</amber>> counts = <<teal>>default_dict<</teal>>(<<blue>>0<</blue>>)
      counts.apple += <<blue>>1<</blue>>    <<dim>>reads 0 (default), writes 1<</dim>>
      counts.apple += <<blue>>1<</blue>>    <<dim>>reads 1, writes 2<</dim>>
      console.log(counts.banana)   <<dim>>0 (still default — never written)<</dim>>

  <<dim>>Same pattern is how Vue's reactive() and MobX's observable() work.
  The trap intercepts every property read, so the framework can record
  which components depend on which fields and re-render when those fields
  change.<</dim>>

# EXAMPLE 3

  The capstone — nearest-embedding lookup by cosine similarity. Pulls
  together cosine_sim from Intermediate, top_k from earlier in Master,
  and embedding indexing.

      <<amber>>function<</amber>> <<teal>>cosine_sim<</teal>>(a, b) {
          <<amber>>let<</amber>> d = <<blue>>0<</blue>>, ma = <<blue>>0<</blue>>, mb = <<blue>>0<</blue>>
          <<amber>>for<</amber>> (<<amber>>let<</amber>> i = <<blue>>0<</blue>>; i < a.length; i++) {
              d  += a[i] * b[i]
              ma += a[i] * a[i]
              mb += b[i] * b[i]
          }
          <<amber>>return<</amber>> d / (<<amber>>Math<</amber>>.sqrt(ma) * <<amber>>Math<</amber>>.sqrt(mb))
      }

  Then nearest() pairs each row's similarity with its index, sorts
  descending, slices the top k, and returns just the indices:

      <<amber>>function<</amber>> <<teal>>nearest<</teal>>(embeddings, query, k) {
          <<amber>>return<</amber>> embeddings
              .<<purple>>map<</purple>>((row, i) => [<<teal>>cosine_sim<</teal>>(row, query), i])
              .<<purple>>sort<</purple>>((a, b) => b[<<blue>>0<</blue>>] - a[<<blue>>0<</blue>>] || a[<<blue>>1<</blue>>] - b[<<blue>>1<</blue>>])
              .<<purple>>slice<</purple>>(<<blue>>0<</blue>>, k)
              .<<purple>>map<</purple>>(pair => pair[<<blue>>1<</blue>>])
      }

  <<dim>>This is the core operation behind semantic search and RAG. Encode
  a query into a vector, compute cosine similarity to every row of a
  precomputed embedding matrix, return the top-k matching indices. Real
  systems use ANN indexes (FAISS, HNSW) for scale, but the algorithmic
  shape is exactly this. If you can read this, you can read the source
  of nearly any retrieval system. See <</dim>><<qid:js_mas_10>><<dim>>.

  That's the JavaScript track. From <</dim>><<green>>'Hello, world'<</green>><<dim>> in
  Tier 1 to a working semantic-search loop in Tier 5. The vocabulary fits
  on a page; the patterns take longer to internalize.<</dim>>
