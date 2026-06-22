# RUST · TIER 4 CONCEPTS (EXPERIENCED)

  <<dim>>Abstraction without overhead: traits define shared behavior, generics
  write code once for many types, and lifetimes keep borrows honest.<</dim>>

  Intermediate moved values around safely. Now you generalize: a <<teal>>trait<</teal>>
  names behavior any type can implement, a generic works over every type
  that satisfies its bounds, and a lifetime annotation lets a struct hold a
  borrow without ever dangling.

# TRAITS

  A <<amber>>trait<</amber>> is an interface — a set of methods a type promises to provide.
  <<amber>>impl<</amber>> <<teal>>Trait<</teal>> <<amber>>for<</amber>> <<teal>>Type<</teal>> supplies them. A trait may give a
  <<bold>>default<</bold>> method body, which implementors inherit unless they override.

      <<amber>>trait<</amber>> <<teal>>Layer<</teal>> {
          <<amber>>fn<</amber>> <<teal>>forward<</teal>>(&self, x: <<teal>>f64<</teal>>) -> <<teal>>f64<</teal>>;          <<dim>>required<</dim>>
          <<amber>>fn<</amber>> <<teal>>name<</teal>>(&self) -> &<<teal>>str<</teal>> { <<green>>"layer"<</green>> }       <<dim>>default<</dim>>
      }

# GENERICS AND BOUNDS

  A generic parameter <<amber>><T><</amber>> stands for a type chosen by the caller.
  <<bold>>Bounds<</bold>> constrain it: <<amber>>T: Clone<</amber>> means "any T that is Clone." Combine
  bounds with <<amber>>+<</amber>>.

      <<amber>>fn<</amber>> <<teal>>first<</teal>><<amber>><T: Clone><</amber>>(xs: &[<<teal>>T<</teal>>]) -> <<teal>>T<</teal>> { xs[<<blue>>0<</blue>>].<<purple>>clone<</purple>>() }

  Without the <<amber>>Clone<</amber>> bound this would not compile — you can't clone a
  value whose type isn't known to support it.

# LIFETIMES

  When a struct stores a reference, Rust needs to know the reference will
  outlive the struct. A lifetime parameter <<amber>>'a<</amber>> expresses that tie.

      <<amber>>struct<</amber>> <<teal>>View<'a><</teal>> { data: &<<amber>>'a<</amber>> <<teal>>[f64]<</teal>> }

  <<red>>Always anchor lifetimes to a real scenario<</red>> — a struct holding a
  slice, a function returning a borrow. They are bookkeeping for borrows,
  not a puzzle to solve in the abstract.

# RETURNING RESULTS

  A fallible function returns <<teal>>Result<T, E><</teal>>. The <<amber>>?<</amber>> operator unwraps
  an <<amber>>Ok<</amber>> or returns the <<amber>>Err<</amber>> to the caller — <<red>>it propagates, it does
  not crash<</red>> (that is .unwrap()).

      <<amber>>let<</amber>> n: <<teal>>i32<</teal>> = text.<<purple>>parse<</purple>>()?;

  NEXT TIER: heap and shared ownership — <<teal>>Box<</teal>>, <<teal>>Rc<</teal>>, <<teal>>Arc<</teal>> — plus
  <<amber>>async<</amber>>/<<amber>>.await<</amber>> and <<amber>>unsafe<</amber>>. The capstone composes these into a
  small machine-learning primitive.

---

# EXAMPLE 1

  Define a trait with one required method, then implement it for a type.

      <<amber>>trait<</amber>> <<teal>>Score<</teal>> {
          <<amber>>fn<</amber>> <<teal>>score<</teal>>(&self) -> <<teal>>f64<</teal>>;
      }
      <<amber>>struct<</amber>> <<teal>>Run<</teal>> { hits: <<teal>>f64<</teal>>, total: <<teal>>f64<</teal>> }
      <<amber>>impl<</amber>> <<teal>>Score<</teal>> <<amber>>for<</amber>> <<teal>>Run<</teal>> {
          <<amber>>fn<</amber>> <<teal>>score<</teal>>(&self) -> <<teal>>f64<</teal>> { self.hits / self.total }
      }

  <<dim>>The impl block fills in every required method. Once implemented, a Run
  can be used anywhere a Score is expected.<</dim>>

# EXAMPLE 2

  A generic function with a trait bound: it works for any type that can be
  added, returning the sum.

      <<amber>>use<</amber>> std::ops::<<teal>>Add<</teal>>;
      <<amber>>fn<</amber>> <<teal>>combine<</teal>><<amber>><T: Add<Output = T> + Copy><</amber>>(a: <<teal>>T<</teal>>, b: <<teal>>T<</teal>>) -> <<teal>>T<</teal>> {
          a + b
      }

  <<dim>>The bound T: Add<Output = T> says "T can be added to itself and yields a
  T." Copy lets the function use a and b by value. Bounds are the contract a
  generic relies on.<</dim>>

# EXAMPLE 3

  A struct that borrows data needs a lifetime so the borrow can't outlive
  its source.

      <<amber>>struct<</amber>> <<teal>>Window<'a><</teal>> { samples: &<<amber>>'a<</amber>> <<teal>>[i32]<</teal>> }
      <<amber>>impl<</amber>><<amber>><'a><</amber>> <<teal>>Window<'a><</teal>> {
          <<amber>>fn<</amber>> <<teal>>first<</teal>>(&self) -> <<teal>>i32<</teal>> { self.samples[<<blue>>0<</blue>>] }
      }

  <<dim>>Window borrows a slice it does not own; 'a ties the two together so the
  compiler rejects any use of Window after samples is gone.<</dim>>

# EXAMPLE 4

  A preview of Master tier: <<teal>>Box<</teal>> puts a value on the heap, and a
  <<teal>>Box<dyn Score><</teal>> holds any scorer behind its trait interface.

      <<amber>>let<</amber>> boxed: <<teal>>Box<dyn Score><</teal>> = <<teal>>Box<</teal>>::new(<<teal>>Run<</teal>> { hits: <<blue>>8.0<</blue>>, total: <<blue>>10.0<</blue>> });

  <<dim>>boxed holds a heap-allocated Run, reachable only through the Score
  trait. Next tier adds Rc/Arc for sharing, async for awaiting, and the ML
  capstone.<</dim>>
