# RUST CHEATSHEET

  <<dim>>A working reference for the whole language. Skim it once, come back when stuck.<</dim>>

# VARIABLES AND TYPES

  <<amber>>let<</amber>> binds an immutable name; <<amber>>let mut<</amber>> makes it
  reassignable. Rust infers most types, or you annotate with <<amber>>:<</amber>> <<teal>>Type<</teal>>.

      <<amber>>let<</amber>> rate: <<teal>>f64<</teal>> = <<blue>>0.05<</blue>>;
      <<amber>>let<</amber>> <<amber>>mut<</amber>> count = <<blue>>0<</blue>>;          <<dim>>i32 by default<</dim>>
      <<amber>>let<</amber>> open = <<amber>>true<</amber>>;            <<dim>>bool<</dim>>

  <<red>>Booleans are lowercase<</red>> true/false. Numeric literals can carry a type
  suffix (<<blue>>0u8<</blue>>, <<blue>>1.0f64<</blue>>). Every statement ends with <<amber>>;<</amber>>.

# OWNERSHIP AND BORROWING

  Each value has one owner. Assigning or passing it <<bold>>moves<</bold>> ownership;
  the old name is then invalid — unless the type is <<teal>>Copy<</teal>> (integers, bool, f64).

      <<amber>>let<</amber>> a = <<teal>>String<</teal>>::from(<<green>>"hi"<</green>>);
      <<amber>>let<</amber>> b = a;
          a  --X         <<dim>>moved out; using a is now a compile error<</dim>>
          b  -->  "hi"   <<dim>>b owns the heap data<</dim>>

  <<bold>>Borrow<</bold>> instead of moving with <<amber>>&<</amber>>. A shared borrow <<amber>>&T<</amber>> allows
  many readers; an exclusive borrow <<amber>>&mut T<</amber>> allows exactly one writer.

          &T      shared      many readers,  no writer
          &mut T  exclusive   one writer,    nothing else at once

  <<red>>A &mut borrow cannot coexist with any other borrow.<</red>> That rule, checked
  at compile time, is what makes Rust memory-safe without a garbage collector.

# COLLECTIONS

  <<teal>>Vec<T><</teal>> is a growable array; <<teal>>String<</teal>> is an owned, growable string;
  <<teal>>&str<</teal>> is a borrowed string slice. Tuples group fixed-size values.

      <<amber>>let<</amber>> xs: <<teal>>Vec<i32><</teal>> = <<purple>>vec!<</purple>>[<<blue>>1<</blue>>, <<blue>>2<</blue>>, <<blue>>3<</blue>>];
      <<amber>>let<</amber>> name: <<teal>>String<</teal>> = <<teal>>String<</teal>>::from(<<green>>"ada"<</green>>);
      <<amber>>let<</amber>> pair = (<<blue>>3<</blue>>, <<blue>>5<</blue>>);          <<dim>>(i32, i32)<</dim>>

# CONTROL FLOW

  <<amber>>if<</amber>> takes no parentheses; braces are always required. <<amber>>match<</amber>> is an
  expression and must be exhaustive — <<amber>>_<</amber>> is the catch-all arm.

      <<amber>>if<</amber>> cost > <<blue>>1000<</blue>> { <<green>>"high"<</green>> } <<amber>>else<</amber>> { <<green>>"low"<</green>> }
      <<amber>>match<</amber>> n { <<blue>>1<</blue>> => <<green>>"one"<</green>>, _ => <<green>>"many"<</green>> }

# MACROS

  A trailing <<amber>>!<</amber>> marks a <<bold>>macro<</bold>>, not a function. <<purple>>println!<</purple>> prints a
  line — <<amber>>{}<</amber>> is a placeholder filled by the args that follow; <<purple>>format!<</purple>>
  builds a <<teal>>String<</teal>> the same way; <<purple>>vec!<</purple>> constructs a <<teal>>Vec<</teal>>.

      <<purple>>println!<</purple>>(<<green>>"open: {}"<</green>>, count);
      <<amber>>let<</amber>> msg = <<purple>>format!<</purple>>(<<green>>"{} bays"<</green>>, n);

# FUNCTIONS AND CLOSURES

  <<amber>>fn<</amber>> declares a function; the final expression (no <<amber>>;<</amber>>) is the
  return value. Closures use <<amber>>|args|<</amber>> and capture their environment.

      <<amber>>fn<</amber>> <<teal>>double<</teal>>(x: <<teal>>i32<</teal>>) -> <<teal>>i32<</teal>> { x * <<blue>>2<</blue>> }
      <<amber>>let<</amber>> add = |a, b| a + b;
      <<amber>>move<</amber>> || weights      <<dim>>move: the closure owns weights (non-Copy)<</dim>>

# ITERATORS

  <<purple>>.iter()<</purple>> yields <<amber>>&T<</amber>> references. Chain <<purple>>.map<</purple>>, <<purple>>.filter<</purple>>,
  <<purple>>.fold<</purple>>, <<purple>>.zip<</purple>>, <<purple>>.enumerate<</purple>>; finish with <<purple>>.sum<</purple>>,
  <<purple>>.count<</purple>>, <<purple>>.collect<</purple>>, or <<purple>>.max_by<</purple>>.

      <<amber>>let<</amber>> ss: <<teal>>f64<</teal>> = xs.<<purple>>iter<</purple>>().<<purple>>map<</purple>>(|&x| x * x).<<purple>>sum<</purple>>();

  <<dim>>In a closure, <<amber>>|&x|<</amber>> destructures the reference so x is a value;
  <<amber>>|x| *x<</amber>> dereferences in the body. Both are accepted.<</dim>>

# OPTION AND RESULT

  <<teal>>Option<T><</teal>> is <<amber>>Some(v)<</amber>> or <<amber>>None<</amber>>; <<teal>>Result<T, E><</teal>> is
  <<amber>>Ok(v)<</amber>> or <<amber>>Err(e)<</amber>>. The <<amber>>?<</amber>> operator returns Err to your
  caller; <<red>>.unwrap() instead crashes the program on Err<</red>>.

      <<amber>>let<</amber>> v = s.<<purple>>parse<</purple>>()?;            <<dim>>returns Err early<</dim>>
      x.<<purple>>unwrap_or<</purple>>(<<blue>>0.0<</blue>>)                <<dim>>value, or a default<</dim>>

# TRAITS AND GENERICS

  A <<amber>>trait<</amber>> defines shared behavior; <<amber>>impl<</amber>> ... <<amber>>for<</amber>> implements it
  for a type. Generics use <<amber>><T><</amber>> with bounds like <<amber>>T: Copy + PartialOrd<</amber>>.

      <<amber>>trait<</amber>> <<teal>>Activation<</teal>> { <<amber>>fn<</amber>> <<teal>>apply<</teal>>(&self, x: <<teal>>f64<</teal>>) -> <<teal>>f64<</teal>>; }
      <<amber>>impl<</amber>> <<teal>>Activation<</teal>> <<amber>>for<</amber>> <<teal>>Relu<</teal>> { <<dim>>...<</dim>> }

# LIFETIMES

  A lifetime <<amber>>'a<</amber>> ties a borrow's validity to a scope. A struct holding a
  reference must name one, so the borrow can't outlive the data it points to.

      <<amber>>struct<</amber>> <<teal>>Doc<'a><</teal>> { text: &<<amber>>'a<</amber>> <<teal>>str<</teal>> }
          owner --> "..."   <<dim>>the string the slice points into<</dim>>
          Doc<'a> borrows it; Doc must not outlive owner

# SMART POINTERS

  <<teal>>Box<T><</teal>> heap-allocates one value (and enables <<amber>>dyn<</amber>> trait objects).
  <<teal>>Rc<T><</teal>> is single-threaded shared ownership; <<teal>>Arc<T><</teal>> is its atomic,
  thread-safe twin.

      <<amber>>let<</amber>> layer: <<teal>>Box<dyn Activation><</teal>> = <<teal>>Box<</teal>>::new(relu);
      <<amber>>let<</amber>> shared = <<teal>>Rc<</teal>>::new(table);    <<teal>>Rc<</teal>>::clone(&shared);

# ASYNC AND UNSAFE

  <<amber>>async fn<</amber>> returns a future; drive it with a <<red>>postfix<</red>> <<amber>>.await<</amber>>
  (<<red>>not<</red>> a prefix as in Python/JS). <<amber>>unsafe<</amber>> blocks permit raw-pointer
  deref and FFI; <<amber>>extern "C"<</amber>> exposes the C ABI.

      <<amber>>let<</amber>> w = load_checkpoint().<<purple>>await<</purple>>;
      <<amber>>unsafe<</amber>> { *p }                <<dim>>deref a raw pointer<</dim>>

# TAG REFERENCE

  <<amber>>amber<</amber>> keywords. <<teal>>teal<</teal>> types/callables. <<green>>green<</green>>
  strings. <<blue>>blue<</blue>> numerics. <<purple>>purple<</purple>> methods.
  <<red>>red<</red>> warnings. <<dim>>dim<</dim>> asides. <<bold>>bold<</bold>> emphasis.
