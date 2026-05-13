# JAVASCRIPT · TIER 4 CONCEPTS (EXPERIENCED)

  <<dim>>Classes plus the ML primitives that combine the array tools from
  earlier tiers into real model components. Where Intermediate teaches the
  pieces, Experienced teaches the assembly.<</dim>>

# CLASSES

  A class defines a type. The constructor runs at instantiation. <<bold>>this<</bold>>
  is the current instance, passed implicitly when you call a method on an
  object.

      <<amber>>class<</amber>> <<teal>>WorkOrder<</teal>> {
          <<teal>>constructor<</teal>>(id, cost, status) {
              this.id = id
              this.cost = cost
              this.status = status
          }
          <<teal>>is_open<</teal>>() {
              <<amber>>return<</amber>> this.status === <<green>>'Open'<</green>>
          }
      }

  Construct with <<bold>>new WorkOrder(1, 100, 'Open')<</bold>>. Methods are
  declared without <<amber>>function<</amber>> inside the class body.

# INHERITANCE

  <<amber>>class<</amber>> Child extends Parent inherits Parent's methods. Use
  <<amber>>super<</amber>> in the constructor to pass arguments up. <<amber>>super.method()<</amber>>
  inside an overridden method calls the parent's version.

      <<amber>>class<</amber>> <<teal>>SportsCar<</teal>> <<amber>>extends<</amber>> <<teal>>Vehicle<</teal>> {
          <<teal>>constructor<</teal>>(make, year, topSpeed) {
              <<amber>>super<</amber>>(make, year)
              this.topSpeed = topSpeed
          }
          <<teal>>is_fast<</teal>>() { <<amber>>return<</amber>> this.topSpeed > <<blue>>150<</blue>> }
      }

  <<dim>>Inheritance is one of three ways to share behavior. Composition
  (objects that contain other objects) and duck-typing (any object with
  the right shape works) are the others. Use inheritance when the
  relationship is genuinely "is-a."<</dim>>

# GETTERS AND SETTERS

  <<purple>>get<</purple>> and <<purple>>set<</purple>> inside a class declare property
  accessors. Callers read and write <<bold>>obj.name<</bold>> without parens; the
  class controls what happens.

      <<amber>>class<</amber>> <<teal>>Temperature<</teal>> {
          <<teal>>constructor<</teal>>(c) { this.celsius = c }
          <<purple>>get<</purple>> <<teal>>fahrenheit<</teal>>() { <<amber>>return<</amber>> this.celsius * <<blue>>9<</blue>>/<<blue>>5<</blue>> + <<blue>>32<</blue>> }
          <<purple>>set<</purple>> <<teal>>fahrenheit<</teal>>(v) { this.celsius = (v - <<blue>>32<</blue>>) * <<blue>>5<</blue>>/<<blue>>9<</blue>> }
      }

  Useful for derived properties (computed from internals), validation on
  write, or backwards compatibility when refactoring a stored value into
  a computed one.

# PROMISE CHAINING

  Before async/await there was <<bold>>.then()<</bold>>. Both forms exist; await
  is sugar over then for sequential code, but raw chaining is still useful
  when transforming a Promise into another Promise without awaiting.

      <<amber>>const<</amber>> scaled = fetch_score().<<purple>>then<</purple>>(x => x * <<blue>>2<</blue>>).<<purple>>then<</purple>>(x => x + <<blue>>1<</blue>>)
      <<amber>>const<</amber>> final = <<amber>>await<</amber>> scaled

  Each <<bold>>.then<</bold>> returns a new Promise resolving to the callback's
  return value. Chaining is how you transform a value pipeline-style.

# FETCH IDIOMS

  Real fetch calls do two awaits: one for the response object, one for
  the body. Forgetting the second is the most-common production fetch bug.

      <<amber>>const<</amber>> resp = <<amber>>await<</amber>> fetch(url)
      <<amber>>const<</amber>> data = <<amber>>await<</amber>> resp.json()

  Wrap with try/catch to handle network errors and JSON parse errors
  separately. Check <<bold>>resp.ok<</bold>> for HTTP status before calling
  <<bold>>.json()<</bold>> — fetch only rejects on network failures, not on 404
  or 500.

# ML PRIMITIVES — VECTOR ARITHMETIC

  At this tier the ML content gets denser. You're building model components.

  <<bold>>Vector add<</bold>> is element-wise sum, returning a new array. Building
  block for residual connections and bias addition.

      <<amber>>function<</amber>> <<teal>>vec_add<</teal>>(a, b) { <<amber>>return<</amber>> a.<<purple>>map<</purple>>((x, i) => x + b[i]) }

  <<bold>>Vector mean<</bold>> is sum / length. The base operation behind mean
  pooling, where multiple embeddings get averaged into one representation.

  <<bold>>Stable softmax<</bold>> is the version of softmax you actually use in
  practice. Subtract max(xs) before exponentiating — same answer, doesn't
  overflow.

      <<amber>>const<</amber>> shift = <<amber>>Math<</amber>>.max(...xs)
      <<amber>>const<</amber>> exps = xs.<<purple>>map<</purple>>(x => <<amber>>Math<</amber>>.exp(x - shift))

# A TINY FEEDFORWARD PASS

  Linear layer + ReLU is the fundamental building block of neural networks.
  Given an input vector x, a weight matrix W, and a bias vector b:

      output[i] = max(0, dot(W[i], x) + b[i])

  That's a layer. Stacking two of these with a softmax at the end is a
  one-hidden-layer classifier. Real models do the same operation, just
  with bigger matrices and more layers.

  <<dim>>Implementing this from scratch — once — gives you the mental model
  for what numpy / torch / tensorflow do under the hood. After that you
  can read the framework code without it feeling like magic. See
  <</dim>><<qid:js_exp_09>><<dim>>.<</dim>>

# CROSS-ENTROPY LOSS

  Given a probability distribution and the index of the true class,
  cross-entropy is <<bold>>-log(probs[true_index])<</bold>>. When the model puts
  high probability on the right answer, loss is small. When it's confident
  in the wrong answer, loss is large.

  Pair this with softmax outputs and you have the loss function used to
  train almost every classification model.

  NEXT TIER: generators, Proxy, typed arrays, performance patterns, and
  the closing image of the track — embedding lookup with cosine similarity,
  the foundation of semantic search.

---

# EXAMPLE 1

  A class with a constructor, a method, and a property accessor. The
  canonical "domain object" shape in production code.

      <<amber>>class<</amber>> <<teal>>Order<</teal>> {
          <<teal>>constructor<</teal>>(cost, status) {
              this.cost = cost
              this.status = status
          }
          <<purple>>get<</purple>> <<teal>>tax<</teal>>() { <<amber>>return<</amber>> this.cost * <<blue>>0.08<</blue>> }
          <<teal>>is_open<</teal>>() { <<amber>>return<</amber>> this.status === <<green>>'Open'<</green>> }
      }

      <<amber>>const<</amber>> o = <<amber>>new<</amber>> <<teal>>Order<</teal>>(<<blue>>100<</blue>>, <<green>>'Open'<</green>>)
      console.log(o.tax)         <<dim>>8 (no parens, it's a getter)<</dim>>
      console.log(o.is_open())   <<dim>>true (parens, it's a method)<</dim>>

  <<dim>>Getters look like attributes from outside; methods look like
  functions. The choice depends on whether the operation feels like "what
  is this thing" (getter) or "do this thing" (method). Tax is data
  derived from cost, so it's a getter.<</dim>>

# EXAMPLE 2

  Stable softmax — the production version of the algorithm from
  Intermediate. The shift before exponentiating prevents overflow without
  changing the result.

      <<amber>>function<</amber>> <<teal>>stable_softmax<</teal>>(xs) {
          <<amber>>const<</amber>> shift = <<amber>>Math<</amber>>.max(...xs)
          <<amber>>const<</amber>> exps  = xs.<<purple>>map<</purple>>(x => <<amber>>Math<</amber>>.exp(x - shift))
          <<amber>>const<</amber>> sum   = exps.<<purple>>reduce<</purple>>((a, b) => a + b, <<blue>>0<</blue>>)
          <<amber>>return<</amber>> exps.<<purple>>map<</purple>>(e => e / sum)
      }

      <<teal>>stable_softmax<</teal>>([<<blue>>1000<</blue>>, <<blue>>1001<</blue>>, <<blue>>1002<</blue>>])
      <<dim>>[0.090, 0.245, 0.665] — same as softmax([1, 2, 3])<</dim>>

  <<dim>>The naive softmax from Intermediate would return [NaN, NaN, NaN]
  on this input because Math.exp(1002) overflows to Infinity, and
  Infinity / Infinity is NaN. The shift makes the largest input 0, so
  the largest exponential is exp(0) = 1.<</dim>>

# EXAMPLE 3

  Tiny feedforward pass — the closing example of Experienced and the
  shape that Master tier extends. One linear layer with ReLU activation.

      <<amber>>function<</amber>> <<teal>>forward<</teal>>(x, W, b) {
          <<amber>>return<</amber>> W.<<purple>>map<</purple>>((row, i) => {
              <<amber>>const<</amber>> z = row.<<purple>>reduce<</purple>>((acc, w, j) => acc + w * x[j], <<blue>>0<</blue>>) + b[i]
              <<amber>>return<</amber>> <<amber>>Math<</amber>>.max(<<blue>>0<</blue>>, z)
          })
      }

  <<dim>>Read it as: for each row of the weight matrix, dot it with x, add
  the bias, apply ReLU. That's the entire forward pass of one layer. At
  Master tier you'll batch this with matrix-vector multiply (matvec) and
  use the output to drive nearest-neighbor retrieval. See <</dim>><<qid:js_mas_09>><<dim>>.<</dim>>
