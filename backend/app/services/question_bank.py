"""Curated offline assessment questions used when an AI provider is unavailable."""

import random


# Each subject has ten distinct concepts. The same concepts are assessed at
# different levels by changing the prompt from recall to applied scenarios.
_BANK = {
    "Python": (
        ("List comprehension", "A compact expression that builds a list from an iterable and may filter items.", "Transform or filter a sequence while keeping the result as a list."),
        ("Generator", "An iterator that yields values lazily instead of storing the whole result at once.", "Process a very large data stream while keeping memory use low."),
        ("Dictionary", "A mutable mapping from unique hashable keys to values with average constant-time lookup.", "Retrieve a record by a stable identifier without scanning every item."),
        ("Tuple", "An immutable ordered sequence that can represent a fixed collection of values.", "Return a fixed pair of coordinates that should not be changed by callers."),
        ("Context manager", "An object that sets up and reliably cleans up a resource around a block of code.", "Ensure a file or lock is released even when an exception interrupts the block."),
        ("Decorator", "A callable that wraps another function to add behavior while preserving its interface.", "Apply the same timing or authorization behavior to several functions."),
        ("Exception handling", "The mechanism for catching, raising, and responding to runtime errors.", "Recover from a missing file while allowing unrelated programming errors to surface."),
        ("Closure", "A function that retains access to variables from the scope where it was created.", "Create a callback that remembers configuration after the outer function returns."),
        ("Coroutine", "A suspendable function that cooperatively yields control at await points.", "Handle many network waits without dedicating a thread to each request."),
        ("GIL", "In standard CPython, a lock that allows only one thread at a time to execute Python bytecode.", "Choose multiple processes for CPU-bound parallel work in standard CPython."),
    ),
    "SQL": (
        ("JOIN", "An operation that combines rows from tables using a related column.", "Return each order with the matching customer details."),
        ("GROUP BY", "A clause that groups rows so aggregate functions can summarize each group.", "Calculate total sales separately for each store."),
        ("HAVING", "A clause that filters grouped results after aggregate values are calculated.", "Keep only departments whose employee count exceeds a threshold."),
        ("Index", "An auxiliary structure that can speed up lookups at the cost of storage and write work.", "Speed up frequent searches on a column that is selective and rarely updated."),
        ("Primary key", "A column or column set that uniquely identifies each row and cannot be null.", "Give every account a stable identifier that no other row can share."),
        ("Foreign key", "A constraint that requires a referenced value to exist in another table.", "Prevent an order from referring to a customer that does not exist."),
        ("Transaction", "A group of database operations committed or rolled back as one unit.", "Transfer funds so debit and credit either both persist or neither does."),
        ("Common table expression", "A named temporary query result introduced with WITH for one statement.", "Break a long query into readable steps that are reused by the final select."),
        ("Window function", "A calculation over related rows that keeps each input row in the result.", "Rank employees within each department without collapsing the rows."),
        ("Parameterized query", "A query that sends values separately from SQL syntax.", "Search for a user-provided name without allowing it to alter the query structure."),
    ),
    "Java": (
        ("Interface", "A declared contract of operations that implementing classes provide.", "Allow unrelated payment classes to be used through the same API."),
        ("Encapsulation", "Keeping state behind a controlled public interface and protecting its invariants.", "Validate a balance change instead of exposing a field for arbitrary writes."),
        ("Polymorphism", "Calling an overridden method through a base type and using the runtime implementation.", "Process different notification classes through one common reference."),
        ("Generics", "Type parameters that let code reuse algorithms while retaining compile-time type checks.", "Build a collection that accepts strings without casts when values are read."),
        ("Try-with-resources", "A construct that closes AutoCloseable resources when its block exits.", "Close a stream reliably after reading, including when reading throws."),
        ("HashMap", "A hash-based map with average constant-time get and put operations.", "Look up a value by key when insertion order is not required."),
        ("Immutable object", "An object whose observable state cannot change after construction.", "Safely share a value object between threads without coordinating mutations."),
        ("Stream pipeline", "A sequence of source, intermediate, and terminal operations over data.", "Filter and transform a collection before collecting the results."),
        ("Checked exception", "An exception that Java requires code to catch or declare.", "Make callers handle a recoverable file or network operation failure."),
        ("Volatile field", "A field whose reads and writes have cross-thread visibility guarantees but are not compound atomic operations.", "Publish a simple status flag between threads without treating increments as atomic."),
    ),
    "C": (
        ("Pointer", "A value that stores the address of an object or function.", "Pass a buffer to a function that must update the caller's value."),
        ("Array decay", "In most expressions, an array is converted to a pointer to its first element.", "Pass an array to a function while also passing its length explicitly."),
        ("Dynamic allocation", "Requesting and releasing storage during program execution with functions such as malloc and free.", "Allocate a buffer whose size is known only after reading input."),
        ("Structure", "A user-defined type that groups named fields, potentially of different types.", "Keep a person's identifier and status together as one value."),
        ("const qualifier", "A type qualifier that prevents modification through a particular access path.", "Tell a function it may read a buffer but must not change it."),
        ("Static storage duration", "Storage that exists for the entire execution of the program.", "Keep a counter's value between calls without exposing it globally."),
        ("sizeof", "An operator that reports an object's or type's size in bytes.", "Allocate enough bytes for an array using the element type's actual size."),
        ("Undefined behavior", "Behavior for which the C standard imposes no requirements on the implementation.", "Avoid relying on the result of reading an uninitialized automatic variable."),
        ("Function pointer", "A pointer that can refer to a function with a compatible signature.", "Select a callback at runtime for a sorting or event routine."),
        ("Heap storage", "Dynamically managed storage whose lifetime is controlled by allocation and release operations.", "Return data that must outlive the function that created it."),
    ),
    "C++": (
        ("RAII", "A design technique that ties resource lifetime to object lifetime.", "Release a lock or file handle automatically when its owning object leaves scope."),
        ("unique_ptr", "A smart pointer that represents exclusive ownership and transfers it when moved.", "Represent one owner of a dynamically created object without manual delete."),
        ("shared_ptr", "A smart pointer that shares ownership using a reference count.", "Keep an object alive while several independent components still own it."),
        ("Move semantics", "Operations that transfer resources from an expiring object instead of copying them.", "Return a large buffer efficiently when its previous owner is no longer needed."),
        ("Virtual destructor", "A base-class destructor declared virtual so deleting through a base pointer destroys the derived object too.", "Safely destroy derived instances through an owning base-class pointer."),
        ("Template", "A compile-time mechanism for defining functions or types parameterized by types or values.", "Implement one type-safe container algorithm for many element types."),
        ("Vector reallocation", "A capacity-growing operation that may move vector elements and invalidate references or iterators.", "Avoid keeping an element pointer across an insertion that can grow the vector."),
        ("Const reference", "A reference that avoids copying while preventing mutation through that reference.", "Pass a large object efficiently to a function that only reads it."),
        ("std::map", "An ordered associative container with logarithmic lookup and insertion.", "Iterate keys in sorted order while supporting predictable logarithmic searches."),
        ("Lambda capture", "A rule that determines which surrounding variables a lambda stores or references.", "Keep a small value copy in a callback that will run after the current scope ends."),
    ),
    "HTML & CSS": (
        ("Semantic HTML", "Elements whose names describe the meaning and role of their content.", "Mark the primary page content so browsers and assistive tools can identify it."),
        ("Flexbox", "A layout system designed to align and distribute items along one main axis.", "Align controls in a row and distribute remaining horizontal space."),
        ("CSS Grid", "A two-dimensional layout system for arranging items in rows and columns.", "Build a page layout with aligned card rows and columns."),
        ("Specificity", "A selector weight used to resolve competing declarations for the same property.", "Diagnose why a class rule overrides a broad element selector."),
        ("Box model", "The content, padding, border, and margin layers that determine an element's layout size.", "Explain why adding padding changes a box's rendered width."),
        ("Media query", "A conditional CSS rule that applies styles when viewport or device features match.", "Change a multi-column layout to one column on a narrow screen."),
        ("Alternative text", "A text alternative that conveys an informative image's purpose to nonvisual users.", "Describe the useful content of a chart when the image cannot be seen."),
        ("Form label", "A programmatic name associated with a form control.", "Make an input's purpose available to screen readers and clickable labels."),
        ("CSS custom property", "A reusable CSS value declared with a double-hyphen name and read with var().", "Change a shared color in one place across several components."),
        ("Pseudo-class", "A selector for an element's state or position without adding a class to the markup.", "Style a focused control consistently for keyboard users."),
    ),
    "JavaScript": (
        ("Closure", "A function bundled with access to variables from its lexical creation scope.", "Create a callback that keeps a private counter between calls."),
        ("Event loop", "The runtime mechanism that schedules queued callbacks around the call stack.", "Explain why a timer callback runs after the current synchronous code finishes."),
        ("Promise", "An object representing the eventual fulfillment or rejection of an asynchronous operation.", "Chain success and failure handling for a network request."),
        ("async/await", "Syntax that lets asynchronous code use Promise results in a sequential style.", "Wait for a response before rendering data while still allowing the browser to work."),
        ("Array map", "An array method that creates a new array by applying a callback to each element.", "Convert each record into a display label without changing the source array."),
        ("Strict equality", "The === operator compares without coercing operands to a common type.", "Avoid treating a numeric identifier and its string form as the same value."),
        ("Prototype chain", "The lookup path used to find properties on an object and its prototypes.", "Share methods across instances without copying a function onto each object."),
        ("Event delegation", "Handling descendant events at a shared ancestor using event bubbling.", "Support clicks on many dynamically added list items with one listener."),
        ("ES module", "A file-scoped JavaScript unit that explicitly exports and imports bindings.", "Share a utility function between files without adding it to the global object."),
        ("Immutable update", "Creating a new object or array with changes instead of mutating shared state.", "Update one UI record while preserving references to unchanged records."),
    ),
    "Data Structures": (
        ("Stack", "A last-in, first-out collection that adds and removes items at one end.", "Track nested function calls or support undoing the latest action."),
        ("Queue", "A first-in, first-out collection that removes items in arrival order.", "Schedule print jobs so the earliest submitted job runs first."),
        ("Hash table", "A key-value structure that uses a hash to locate entries with average constant-time operations.", "Check membership quickly when key order is not needed."),
        ("Binary search tree", "A node structure ordered so left and right subtrees contain smaller and larger keys.", "Maintain ordered values with efficient searches when the tree remains balanced."),
        ("Heap", "A complete tree that keeps the minimum or maximum value at its root.", "Repeatedly retrieve the highest-priority task without sorting everything."),
        ("Breadth-first search", "A graph traversal that explores vertices in increasing distance using a queue.", "Find the fewest-edge path in an unweighted graph."),
        ("Depth-first search", "A graph traversal that follows a path deeply before backtracking.", "Explore reachability using recursion or an explicit stack."),
        ("Linked list", "A sequence of nodes connected by references rather than contiguous storage.", "Insert a known node without shifting all later array elements."),
        ("Trie", "A prefix tree that shares path nodes among keys with common prefixes.", "Provide autocomplete suggestions for words sharing an entered prefix."),
        ("Disjoint-set union", "A structure that tracks connected components with near-constant amortized union and find operations.", "Check whether two vertices are already connected while building components."),
    ),
    "DBMS": (
        ("Normalization", "A design process that reduces redundant data and update anomalies by organizing relations.", "Store each customer's address once instead of repeating it on every order."),
        ("ACID transaction", "A transaction model emphasizing atomicity, consistency, isolation, and durability.", "Keep a multi-step account transfer all-or-nothing after a crash."),
        ("Isolation level", "A transaction setting that controls which effects of concurrent work may be observed.", "Choose consistency behavior when concurrent readers and writers overlap."),
        ("Database index", "A maintained lookup structure that speeds reads while adding write and storage costs.", "Improve a common selective query while measuring the impact on updates."),
        ("Referential integrity", "A guarantee that related keys reference valid rows or follow a declared deletion rule.", "Prevent child records from pointing to a nonexistent parent."),
        ("MVCC", "A concurrency technique that keeps row versions so readers can use a consistent snapshot.", "Let a long-running reader proceed while writers commit newer versions."),
        ("Lock", "A coordination mechanism that limits conflicting concurrent access to a resource.", "Prevent two transactions from updating the same row unsafely."),
        ("Replication", "Maintaining copies of data on multiple database servers.", "Serve read traffic from a secondary while preserving a primary copy."),
        ("Sharding", "Partitioning data across servers so each server stores only part of the dataset.", "Scale a dataset beyond one machine by distributing rows across partitions."),
        ("Materialized view", "A stored result of a query that must be refreshed as underlying data changes.", "Speed up an expensive dashboard summary that can tolerate scheduled refreshes."),
    ),
    "Computer Networks": (
        ("DNS", "A distributed naming system that resolves host names to records such as IP addresses.", "Find the address for a service using its human-readable domain name."),
        ("TCP", "A transport protocol that provides an ordered, reliable byte stream between endpoints.", "Deliver a complete ordered file transfer despite packet loss."),
        ("UDP", "A connectionless datagram transport without built-in delivery or ordering guarantees.", "Favor low-latency live media where late packets are less useful than fresh ones."),
        ("TLS", "A protocol that protects application traffic with encryption and peer authentication.", "Prevent eavesdropping and verify a server's identity for a web connection."),
        ("HTTP statelessness", "The protocol does not inherently retain application session state between requests.", "Use a cookie or token when a web application must recognize a returning client."),
        ("Routing", "Selecting a next hop to forward packets toward a destination network.", "Forward traffic between networks using the best available route."),
        ("Subnet", "An IP network range expressed by an address and prefix length.", "Separate a private address range into smaller routed networks."),
        ("TCP handshake", "The SYN, SYN-ACK, ACK exchange that establishes a TCP connection.", "Synchronize initial sequence numbers before application bytes are sent."),
        ("Congestion control", "Transport behavior that adjusts sending rate to avoid overwhelming a network path.", "Reduce a sender's rate when packet loss signals a congested path."),
        ("NAT", "Address translation that maps traffic between private and public address spaces.", "Allow several private hosts to share one public IPv4 address."),
    ),
}

# Basic remains accepted for older assessments already saved in the database.
_LEVELS = {"Basic", "Beginner", "Intermediate", "Advanced"}
_LETTERS = "ABCD"


def generate_local_questions(subject: str, difficulty: str) -> list[dict]:
    """Return ten distinct, validated-shape questions without external services."""
    facts = _BANK.get(subject)
    if facts is None or difficulty not in _LEVELS:
        raise ValueError("No built-in question bank exists for this subject or level")

    rng = random.SystemRandom()
    selected = rng.sample(facts, 10)
    questions = []
    for term, definition, scenario in selected:
        if difficulty == "Basic":
            question_text = f"Which {subject} concept matches this description? {definition}"
            correct_value = term
            choices = [fact[0] for fact in rng.sample([fact for fact in facts if fact[0] != term], 3)]
        elif difficulty == "Beginner":
            question_text = f"Which statement correctly describes {term}?"
            correct_value = definition
            choices = [fact[1] for fact in rng.sample([fact for fact in facts if fact[0] != term], 3)]
        elif difficulty == "Intermediate":
            question_text = f"A practical task has this requirement: {scenario} Which concept is the best fit?"
            correct_value = term
            choices = [fact[0] for fact in rng.sample([fact for fact in facts if fact[0] != term], 3)]
        else:
            question_text = f"In a design review, the constraint is: {scenario} Which concept should guide the decision?"
            correct_value = term
            choices = [fact[0] for fact in rng.sample([fact for fact in facts if fact[0] != term], 3)]

        options = [(correct_value, True), *((choice, False) for choice in choices)]
        rng.shuffle(options)
        correct_answer = _LETTERS[next(index for index, (_, correct) in enumerate(options) if correct)]
        questions.append({
            "question": question_text,
            "options": {letter: value for letter, (value, _) in zip(_LETTERS, options)},
            "correct_answer": correct_answer,
            "explanation": f"{term}: {definition} In practice, {scenario}",
        })
    return questions
