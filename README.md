# Pattern Generation Language (PGL) 

**Pattern Generation Language (PGL)** is a domain-specific high-level language designed to simplify and automate the generation of code pattern variations used in **Source-to-Source Matching and Rewriting (SMR)** tool. 

PGL eliminates the process of manually writing exhaustive pattern specifications by replacing it with a concise, macro-based combinatorial description.


### Key Features

- Represent hundreds or thousands of syntactically different yet semantically equivalent code patterns with just a few lines of PGL.
- PGC automatically generates cartesian products of loop structures, memory access patterns, increment styles, and data types using `itertools.product`.
- Support for generating patterns targeting **C** and **Fortran 90** (`f90`).
- Integrated option to export the Abstract Syntax Tree (AST) as a PNG diagram.
- Dynamically adjust replacement code depending on concrete type expansions (e.g., binding to `cblas_sdot` for `float` vs `cblas_ddot` for `double`).

---

## Architecture & Integration Workflow

PGC acts as an intermediate pattern generation engine between the developer and SMR rewriting tools:

```text
+-------------------+      +--------------------+      +-------------------+
| Input File (.pgl) | ---> | PGL Lexer / Parser | ---> | Linearized AST    |
+-------------------+      +--------------------+      +-------------------+
                                                                |
                                                        (itertools.product)
                                                                |
                                                                v
+-------------------+      +--------------------+      +-------------------+
| Optimized Program | <--- | SMR Tool           | <--- | Output File (.pat)|
+-------------------+      +--------------------+      +-------------------+
```

1. **PGL Specification (`.pgl`)**: The user writes idiom specifications combining operational macros and type variations.
2. **Lexing & Parsing**: The SLY-based frontend converts PGL source code into a structured AST.
3. **Combinatorial Expansion**: The compiler expands AST nodes into all valid syntactic combinations (increments, array/matrix indexing styles, type bindings).
4. **Pattern Generation (`.pat`)**: The compiler outputs a exhaustive list of pattern variations.
5. **SMR Execution**: The SMR framework consumes `.pat` files to match target code snippets and replace them with high-performance library calls (e.g., BLAS / OpenBLAS).

---

## Prerequisites & Installation

- Python 3.8+
- [SLY (Sly Lex Yacc)](https://github.com/dabeaz/sly)
- [Graphviz](https://graphviz.org/) (optional, required only for AST PNG rendering)

```bash
pip install sly graphviz
```

---

## Command Line Interface (CLI)

The compiler is invoked via the `pgl.py` command-line script:

```bash
python3 pgl.py [-h] [-l {c,f90}] -i INPUT [-p PNG] [-d]
```

### Options and Parameters

| Option | Long Flag | Description | Required |
| :--- | :--- | :--- | :--- |
| `-h` | `--help` | Show help message and exit. | Optional |
| `-l` | `--language` | Target programming language (`c` for C, `f90` for Fortran 90). | Optional |
| `-i` | `--input` | Path to the input PGL specification file (`.pgl`). | **Required** |
| `-p` | `--png` | Output file path to render the AST graph image (PNG format). | Optional |
| `-d` | `--debug` | Enable debug mode with detailed parsing and generation logs. | Optional |

### Usage Examples

- **Basic pattern compilation for C:**
  ```bash
  python3 pgl.py -l c -i patterns/dot.pgl
  ```

- **Compile Fortran 90 pattern with debug output and AST visualization:**
  ```bash
  python3 pgl.py -l f90 -i patterns/gemm.pgl -p ast_gemm.png -d
  ```

---

## PGL Language Reference

A standard PGL specification consists of four primary constructs:

1. `import`: Include external definition files (`.def`) containing shared macros and types.
2. `type`: Map a generic type identifier to multiple concrete target language types.
3. `def`: Define operational macros with alternative syntactic variations separated by the pipe (`|`) operator.
4. `decl`: Declare the idiom pattern, defining the matching block (`{ ... }`) and the replacement block (`= { ... }`).

### Special Directives

- **Expansion Directive (`$`)**: Invokes a macro or type expansion (e.g., `$for(i, n)`, `$real`).
- **Conditional Output (`$if`, `$elif`, `$else`)**: Emits specialized replacement code depending on the current concrete type variation.

---

## Example Specification

Below is a complete PGL pattern for a Dot Product (`dot`) in C:

```
// Operational macro definitions with syntactic variations
def inc(x)     : ++x | x++ | x += 1 | x = x + 1 | x = 1 + x
def init(x)    : x = 0
def comp(a, b) : a < b
def for(x, y)  : for ($init(x); $comp(x, y); $inc(x))
def acc(a, b)  : a += b | a = b + a
def mul(a, b)  : (a) * (b) | (b) * (a)
def vector(x,i): x[i]

// Type variation mapping
type int  : unsigned int | int | unsigned long | long
type real : float | double

// Idiom pattern declaration
decl dot($int(n), $real(*x, *y, out)) {
    // Matching Section
    $init(out);
    $for(i, n) {
        $acc(out, $mul($vector(x, i), $vector(y, i)));
    }
} = {
    // Replacement Section with type-based conditional binding
    $if ($real == float) {
        out = cblas_sdot(n, x, 1, y, 1);
    }
    $else {
        out = cblas_ddot(n, x, 1, y, 1);
    }
}
```

From this single 25-line `.pgl` file, PGC automatically expands and generates **160 pattern variations** in the output `.pat` file.

---

# Related Tools & References

- [SMR (Source-based Matching and Rewriting)](https://github.com/PGL-SMR/SMR):
    - An MLIR-powered CLI tool designed for source-to-source pattern matching and code rewriting. It consumes the `.pat` pattern files generated by PGL to perform automated idiom replacement and library binding at the source level.

- [A Pattern Generation Language for MLIR Compiler Matching and Rewriting](https://dl.acm.org/doi/10.1145/3777905):
    ```
    @article{10.1145/3777905,
    author = {Attrot, Wesley and Zago, Luciano and Pereira, Marcio and Couto, Vin{\'i}cius and Yviquel, Herv{\'e} and Araujo, Guido},
    title = {A Pattern Generation Language for MLIR Compiler Matching and Rewriting},
    year = {2026},
    issue_date = {March 2026},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    volume = {23},
    number = {1},
    issn = {1544-3566},
    url = {https://doi.org/10.1145/3777905},
    doi = {10.1145/3777905},
    journal = {ACM Trans. Archit. Code Optim.},
    month = mar,
    articleno = {6},
    numpages = {25},
    keywords = {Pattern description, pattern generation, idiom recognition, hardware accelerators}
    }
    ```

---

# Acknowledgments

We express our gratitude to the **AnghaBench** project team for providing benchmarks to support source-to-source compiler research and pattern validation.

- **Repository:** [AnghaBench on GitHub](https://github.com/brenocfg/AnghaBench)
- **Reference:** [ANGHABENCH: A Suite with One Million Compilable C Benchmarks for Code-Size Reduction](https://ieeexplore.ieee.org/document/9370322)
