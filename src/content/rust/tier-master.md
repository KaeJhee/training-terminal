# RUST · TIER 5 CONCEPTS (MASTER)

  <<dim>>The systems tier: futures you await, pointers you share, escape hatches
  you reach for deliberately — and the primitives that build a model.<</dim>>

  Everything so far ran start to finish on one thread, with the borrow
  checker watching. Master adds the tools real systems need: <<amber>>async<</amber>> for
  work that waits, smart pointers for shared ownership, and <<amber>>unsafe<</amber>> for the
  rare moment you step outside the checker's guarantees on purpose.

# ASYNC AND AWAIT

  <<amber>>async fn<</amber>> returns a <<bold>>future<</bold>> — a value that does nothing until driven.
  You drive it with <<amber>>.await<</amber>>, which is <<red>>postfix<</red>> in Rust: <<amber>>expr.await<</amber>>,
  not <<amber>>await expr<</amber>> as in Python or JavaScript.

      <<amber>>async fn<</amber>> <<teal>>warm<</teal>>() -> <<teal>>i32<</teal>> { <<blue>>1<</blue>> }
      <<amber>>let<</amber>> ready = warm().<<purple>>await<</purple>>;

# SMART POINTERS

  <<teal>>Box<T><</teal>> owns one value on the heap and powers <<amber>>dyn<</amber>> trait objects
  (<<teal>>Box<dyn Layer><</teal>>). <<teal>>Rc<T><</teal>> gives several owners a shared,
  reference-counted value on one thread; <<teal>>Arc<T><</teal>> is the atomic version
  that is safe to share across threads.

      <<amber>>let<</amber>> owned = <<teal>>Box<</teal>>::new(<<blue>>3.0<</blue>>);          <<dim>>one heap value<</dim>>
      <<amber>>let<</amber>> shared = <<teal>>Rc<</teal>>::new(<<blue>>5<</blue>>);            <<dim>>clone bumps a refcount<</dim>>
      <<amber>>let<</amber>> across = <<teal>>Arc<</teal>>::new(<<blue>>5<</blue>>);           <<dim>>same, thread-safe<</dim>>

  <<purple>>Rc::clone<</purple>>(&x) makes another handle to the same data — cheap, no deep
  copy. Reach for <<teal>>Arc<</teal>> only when the data crosses threads; it costs a
  little more.

# UNSAFE AND FFI

  Most Rust is checked at compile time. An <<amber>>unsafe<</amber>> block is where you tell
  the compiler "I have verified this myself" — dereferencing a raw pointer,
  or calling across an <<amber>>extern "C"<</amber>> boundary.

      <<amber>>let<</amber>> p = &x <<amber>>as<</amber>> *<<amber>>const<</amber>> <<teal>>i32<</teal>>;     <<dim>>making a raw pointer is safe<</dim>>
      <<amber>>let<</amber>> v = <<amber>>unsafe<</amber>> { *p };           <<dim>>dereferencing it is not<</dim>>

  <<amber>>extern "C"<</amber>> gives a function the C ABI so other languages can call it —
  the bridge to GPUs and existing numeric libraries.

  THE CAPSTONE: the final question composes iterators and closures into a
  <<bold>>dot product<</bold>> — the inner loop of every matrix multiply and dense layer.
  Everything in this track has been building toward writing real numeric
  code in safe Rust.

---

# EXAMPLE 1

  An async function returns a future; await drives it to a value.

      <<amber>>async fn<</amber>> <<teal>>fetch_batch<</teal>>() -> <<teal>>i32<</teal>> { <<blue>>32<</blue>> }
      <<amber>>let<</amber>> size = fetch_batch().<<purple>>await<</purple>>;   <<dim>>postfix .await, not a prefix<</dim>>

  <<dim>>Calling fetch_batch() alone does no work — it hands back a future.
  .await is what runs it. The postfix position is the Rust-specific habit.<</dim>>

# EXAMPLE 2

  Share one allocation through several handles with Rc, then reach for Arc
  when the data must cross threads.

      <<amber>>let<</amber>> cache = <<teal>>Rc<</teal>>::new(<<purple>>vec!<</purple>>[<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>]);
      <<amber>>let<</amber>> alias = <<teal>>Rc<</teal>>::clone(&cache);     <<dim>>second handle, same data<</dim>>
      <<amber>>let<</amber>> pool = <<teal>>Arc<</teal>>::new(<<purple>>vec!<</purple>>[<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>]);  <<dim>>thread-safe variant<</dim>>

  <<dim>>cache and alias point at the same vector; dropping one just lowers the
  count. The data frees when the last handle goes away.<</dim>>

# EXAMPLE 3

  A boxed closure stores behavior on the heap behind the Fn trait — here, a
  single activation function.

      <<amber>>let<</amber>> relu: <<teal>>Box<dyn Fn(f64) -> f64><</teal>> =
          <<teal>>Box<</teal>>::new(|x| <<amber>>if<</amber>> x > <<blue>>0.0<</blue>> { x } <<amber>>else<</amber>> { <<blue>>0.0<</blue>> });
      <<amber>>let<</amber>> y = relu(<<blue>>-2.0<</blue>>);              <<dim>>0.0<</dim>>

  <<dim>>The closure has an anonymous type, so storing it needs the Box behind
  the Fn trait. Call it like any function once boxed.<</dim>>

# EXAMPLE 4

  Closing the track: compose iterators into a numeric primitive — here the
  mean activation of a layer's outputs.

      <<amber>>let<</amber>> acts = <<purple>>vec!<</purple>>[<<blue>>0.5<</blue>>, <<blue>>1.5<</blue>>, <<blue>>-0.5<</blue>>];
      <<amber>>let<</amber>> mean = acts.<<purple>>iter<</purple>>().<<purple>>sum<</purple>>::<f64>() / acts.<<purple>>len<</purple>>() <<amber>>as<</amber>> <<teal>>f64<</teal>>;

  <<dim>>This is where the track has been heading: real numeric code, written
  in safe Rust. The capstone question builds the dot product the same way;
  the planned C++ and CUDA tracks pick up where Rust leaves off.<</dim>>
